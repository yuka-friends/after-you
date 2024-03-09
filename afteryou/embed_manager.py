# 用来将图像与文本转换为 embedding
# 处理 faiss 数据库事务（建立、添加索引、搜索）
# 处理向量搜索与 sqlite 数据库召回

# vdb: VectorDatabase

import os

import faiss
import numpy as np
import pandas as pd
import torch
import uform
from PIL import Image

from afteryou import file_utils
from afteryou.config import config
from afteryou.db_manager import db_manager
from afteryou.logger import get_logger
from afteryou.sys_path import FILEPATH_VDB_JOURNAL

logger = get_logger(__name__)

is_cuda_available = torch.cuda.is_available()
device = torch.device("cuda" if is_cuda_available else "cpu")


def get_model(mode="cpu"):
    """
    加载模型
    """
    model = uform.get_model("unum-cloud/uform-vl-multilingual-v2")
    if mode == "cpu":
        logger.info("emb run on cpu.")
    if mode == "cuda":
        logger.info("emb run on cuda.")
        if is_cuda_available:
            model.to(device=device)
        else:
            logger.warning("cude not available, emb run on cpu.")

    return model


def embed_img(model: uform.models.VLM, img_filepath, is_cuda_available=is_cuda_available):
    """
    将图像转为 embedding vector
    """
    image = Image.open(img_filepath)
    image_data = model.preprocess_image(image)
    if is_cuda_available:
        image_features, image_embedding = model.encode_image(image_data.to(device=device), return_features=True)
    else:
        image_features, image_embedding = model.encode_image(image_data, return_features=True)
    return image_embedding


def embed_text(text_query, model, detach_numpy=True):
    """
    将文本转为 embedding vector
    注意：model 必须运行在 cpu 模式下

    :param detach_numpy 是否预处理张量
    """
    # 对文本进行编码
    text_data = model.preprocess_text(text_query)
    text_features, text_embedding = model.encode_text(text_data, return_features=True)

    # 预处理张量
    if detach_numpy:
        text_np = text_embedding.detach().cpu().numpy()
        text_np = np.float32(text_np)
        faiss.normalize_L2(text_np)
        return text_np
    else:
        return text_embedding


class VectorDatabase:
    """
    向量数据库事务
    以 IndexIDMap 存储，对应关系为 向量 - sqlite 的 ROWID
    """

    def __init__(self, vdb_filename, db_dir=config.userdata_filepath, dimension=256):  # uform 使用 256d 向量
        """
        初始化新建/载入数据库

        :param vdb_filename, 向量数据库名字
        :param db_dir, 向量数据库路径
        """
        self.dimension = dimension
        self.vdb_filepath = os.path.join(db_dir, vdb_filename)
        self.all_ids_list = []
        file_utils.ensure_dir(db_dir)
        if os.path.exists(self.vdb_filepath):
            self.index = faiss.read_index(self.vdb_filepath)
            self.all_ids_list = faiss.vector_to_array(self.index.id_map).tolist()  # 获得向量数据库中已有 ROWID 列表，以供写入时比对
        else:
            self.index = faiss.IndexIDMap(faiss.IndexFlatL2(self.dimension))

    def add_vector(self, vector, rowid: int):
        """
        添加向量到 index

        :param vector: 图像 embedding 后的向量
        :param rowid: sqlite 对应的 ROWID
        """
        vector = vector.detach().cpu().numpy()  # 转换为numpy数组
        vector = np.float32(vector)  # 转换为float32类型的numpy数组
        faiss.normalize_L2(vector)  # 规范化向量，避免在搜索时出现错误的结果

        if rowid in self.all_ids_list:  # 如果 rowid 已经存在于向量数据库，删除后再更新
            self.index.remove_ids(np.array([rowid]))
        self.index.add_with_ids(vector, np.array([rowid]))  # 踩坑：使用faiss来管理就好，先用list/dict缓存再集中写入的思路会OOM

    def delete_vector(self, rowid: int):
        self.index.remove_ids(np.array([rowid]))

    def search_vector(self, vector, k=20):
        """在数据库中查询最近的k个向量，返回对应 (rowid, 相似度) 列表"""
        probs, indices = self.index.search(vector, k)
        return [(i, probs[0][j]) for j, i in enumerate(indices[0])]

    def save_to_file(self):
        """将向量数据库写入本地文件"""
        faiss.write_index(self.index, self.vdb_filepath)
        self.all_ids_list = faiss.vector_to_array(self.index.id_map).tolist()  # 更新 ROWID 列表


def find_closest_iframe_img_dict_item(target: str, img_dict: dict, threshold=3):
    """
    寻找 dict {sqlite_ROWID:图像文件名} 中最邻近输入图像名的一项
    如输入 "123.jpg"，返回字典中最接近的 "125.jpg"
    """
    closest_item = None
    min_difference = float("inf")

    for key, value in img_dict.items():
        difference = abs(int(value.split(".")[0]) - int(target.split(".")[0]))
        if difference <= threshold and difference < min_difference:
            closest_item = value
            min_difference = difference

    return closest_item


def query_vector_in_vdb(vector, vdb_filepath=FILEPATH_VDB_JOURNAL):
    """
    流程：在 vdb journal 中搜索向量，提取对应 sqlite rowid 项，合并排序返回 df
    """
    vdb = VectorDatabase(vdb_filename=os.path.basename(vdb_filepath))
    res_tuple_list = vdb.search_vector(vector, k=config.embed_search_recall_result_per_db)
    res_tuple_list = [t for t in res_tuple_list if t[0] != -1]  # 相似度结果不足时，会以 -1 的 index 填充，在进 sqlite 搜索前需过滤

    df = db_manager.db_get_rowid_and_similar_tuple_list_rows(rowid_probs_list=res_tuple_list)
    df_list = []
    df_list.append(df)

    merged_df = pd.concat(df_list)
    sorted_df = merged_df.sort_values(by="probs", ascending=True)
    sorted_df = sorted_df.reset_index(drop=True)
    return sorted_df


def embed_journal_to_vdb(model, user_timestamp, user_note, ai_reply_content):
    """
    流程：将日记片段 embed 到 vdb
    """
    text_combine = user_note + "\nreply:" + ai_reply_content
    text_embedding = embed_text(text_combine, model=model, detach_numpy=False)
    vdb = VectorDatabase(vdb_filename=os.path.basename(FILEPATH_VDB_JOURNAL))
    rowid = db_manager.query_rowid(timestamp=user_timestamp)
    if rowid:
        vdb.add_vector(vector=text_embedding, rowid=rowid)
        vdb.save_to_file()
        logger.info(f"added embedding: {text_combine=}")


def delete_vdb_journal_record_by_timestamp(timestamp):
    """
    流程：根据用户时间戳删除 vdb journal 中对应记录
    """
    vdb = VectorDatabase(vdb_filename=os.path.basename(FILEPATH_VDB_JOURNAL))
    rowid = db_manager.query_rowid(timestamp=timestamp)
    vdb.delete_vector(rowid=rowid)
    logger.info(f"delete embedding: {rowid=}")


def query_text_in_vdb_journal(model, text):
    """
    流程：根据文本在 vdb journal 搜索近似记录
    """
    text_embedding = embed_text(model=model, text_query=text)
    df = query_vector_in_vdb(vector=text_embedding, vdb_filepath=FILEPATH_VDB_JOURNAL)
    logger.info(f"querying: {text=}")
    return df


# 测试用例
if __name__ == "__main__":
    pass

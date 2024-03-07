import json
import os
import shutil
import time

import pandas as pd


# 清空指定目录下的所有文件和子目录
def empty_directory(path):
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                shutil.rmtree(entry.path)
            else:
                os.remove(entry.path)


# 检查目录是否存在，若无则创建
def ensure_dir(folder_name):
    # 获取当前工作目录
    current_directory = os.getcwd()

    # 拼接文件夹路径
    folder_path = os.path.join(current_directory, folder_name)

    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        # 创建文件夹
        os.makedirs(folder_path)


# 统计文件夹大小
def get_dir_size(dir):
    size = 0
    for root, _, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


# 查询文件的修改时间是否超过一定间隔
def is_file_modified_recently(file_path, time_gap=30):
    # time_gap 为 minutes
    # 获取文件的修改时间戳
    modified_timestamp = os.path.getmtime(file_path)

    # 获取当前时间戳
    current_timestamp = time.time()

    # 计算时间差（以分钟为单位）
    time_diff_minutes = (current_timestamp - modified_timestamp) / 60

    # 判断时间差是否超过30分钟
    if time_diff_minutes > time_gap:
        return False
    else:
        return True


# 遍历XXX文件夹下有无文件中包含入参str的文件名
def find_filename_in_dir(dir, search_str):
    if not os.path.isdir(dir):
        return False

    for filename in os.listdir(dir):
        if search_str in filename:
            return True

    return False


# 对比A文件是否比B文件新（新的文件时间戳大 -> 结果为正）
def is_fileA_modified_newer_than_fileB(file_path_A, file_path_B):
    # time_gap 为 minutes
    # 获取文件的修改时间戳
    modified_timestamp_A = os.path.getmtime(file_path_A)
    modified_timestamp_B = os.path.getmtime(file_path_B)

    # 计算时间差
    time_diff_minutes = (modified_timestamp_A - modified_timestamp_B) / 60

    if time_diff_minutes > 0:
        return True, time_diff_minutes
    else:
        return False, time_diff_minutes


# 取得文件夹下所有文件名并返回文件名列表、完整文件目录列表
def get_file_path_list(dir):
    filepath_list = []
    if os.path.exists(dir):
        for root, dirs, files in os.walk(dir):
            for file in files:
                file_path = os.path.join(root, file)
                filepath_list.append(file_path)

    return filepath_list


# 取得文件夹下的第一级文件名列表
def get_file_path_list_first_level(dir):
    file_names = []
    for filename in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, filename)):
            file_names.append(filename)
    return file_names


# 取得文件夹下的第一级文件夹列表
def get_file_dir_list_first_level(dir):
    return [d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]


# 将dataframe存储到csv文件
def save_dataframe_to_path(dataframe, file_path="cache/temp.csv"):
    """
    将DataFrame数据保存到指定路径
    """
    ensure_dir(os.path.dirname(file_path))
    dataframe.to_csv(file_path, index=False)  # 使用to_csv()方法将DataFrame保存为CSV文件（可根据需要选择其他文件格式）


# 从csv文件读取dataframe
def read_dataframe_from_path(file_path="cache/temp.csv"):
    """
    从指定路径读取数据到DataFrame
    """
    if not os.path.exists(file_path):
        return None

    dataframe = pd.read_csv(file_path)  # 使用read_csv()方法读取CSV文件（可根据文件格式选择对应的读取方法）
    return dataframe


def save_dict_as_json_to_path(data: dict, filepath):
    """将 dict 保存到 json"""
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, "w") as f:
        json.dump(data, f)


def read_json_as_dict_from_path(filepath):
    """从 json 读取 dict"""
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r") as f:
        data = json.load(f)
    return data


# 读取txt文件中每一行作为一个列表
def read_txt_as_list(file_path):
    with open(file_path, "r", encoding="utf8") as f:
        content_list = [line.strip() for line in f.readlines()]
    return content_list

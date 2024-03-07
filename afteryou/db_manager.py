import datetime
import os
import sqlite3

import pandas as pd

from afteryou.logger import get_logger

logger = get_logger(__name__)


class _DBManager:
    def __init__(self) -> None:
        self.db_filepath = "userdata\\afteryou.db"
        self.tablename = "afteryou_journal"
        self.db_initialize()

    # 初始化数据库：检查、创建、连接入参数据库对象，如果内容为空，则创建表初始化
    def db_initialize(self):
        is_db_exist = os.path.exists(self.db_filepath)

        # 检查数据库是否存在
        if not is_db_exist:
            logger.info(f"{self.db_filepath} db not existed")
            db_dirpath = os.path.dirname(self.db_filepath)
            if not os.path.exists(db_dirpath):
                os.mkdir(db_dirpath)
                logger.info(f"db dir {db_dirpath} not existed, mkdir")

        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.tablename}'")

        if c.fetchone() is None:
            logger.info("db is empty, writing new table.")
            self.db_create_table()

            self.db_insert_data(
                user_timestamp=int(datetime.datetime.now().timestamp()),
                user_note="Welcome to After you. 🥞",
                ai_character_emoji="🔮",
                ai_reply_timestamp=int(datetime.datetime.now().timestamp()),
                ai_reply_content="Hey there, great to meet you. How's your day going?",
                should_ai_reply=True,
                img_filepath="",
            )

        return is_db_exist

    # 创建表
    def db_create_table(self):
        logger.info("Making table")
        conn = sqlite3.connect(self.db_filepath)
        conn.execute(
            f"""CREATE TABLE {self.tablename}
                   (user_timestamp INT,
                   user_note TEXT,
                   ai_character_emoji TEXT,
                   ai_reply_timestamp INT,
                   ai_reply_content TEXT,
                   should_ai_reply BOOLEAN,
                   img_filepath TEXT);"""
        )
        conn.close()

    # 插入数据
    def db_insert_data(
        self,
        user_timestamp: int,
        user_note: str,
        ai_character_emoji: str,
        ai_reply_timestamp: int,
        ai_reply_content: str,
        should_ai_reply: bool,
        img_filepath: str,
    ):
        logger.info("Inserting data")

        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()

        c.execute(
            f"INSERT INTO {self.tablename} (user_timestamp, user_note, ai_character_emoji, ai_reply_timestamp, ai_reply_content, should_ai_reply, img_filepath) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                int(user_timestamp),
                user_note,
                ai_character_emoji,
                int(user_timestamp),
                ai_reply_content,
                should_ai_reply,
                img_filepath,
            ),
        )
        conn.commit()
        conn.close()

    # 根据出入时间戳获取时间段数据
    def db_get_range_by_timestamp(self, start_timestamp: int, end_timestamp: int):
        conn = sqlite3.connect(self.db_filepath)
        query = f"""
        SELECT *
        FROM {self.tablename}
        WHERE user_timestamp
        BETWEEN ? AND ?;
        """
        df = pd.read_sql_query(query, conn, params=(start_timestamp, end_timestamp))
        conn.close()
        if df.empty:
            return None
        else:
            return df

    # 根据用户时间戳删除对应行
    def delete_row_by_timestamp(self, timestamp):
        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        query = f"DELETE FROM {self.tablename} WHERE user_timestamp = ?"
        c.execute(query, (timestamp,))
        conn.commit()
        conn.close()

    # 检查 column_name 列是否存在，若无则新增
    def db_ensure_row_exist(self, column_name, column_type):
        conn = sqlite3.connect(self.db_filepath)
        cursor = conn.cursor()

        # 查询表信息
        cursor.execute(f"PRAGMA table_info({self.tablename});")
        table_info = cursor.fetchall()

        # 检查新列是否已存在
        if column_name not in [column[1] for column in table_info]:
            # 新列不存在，添加新列
            cursor.execute(f"ALTER TABLE {self.tablename} ADD COLUMN {column_name} {column_type};")
            logger.info(f"Column {column_name} added to {self.tablename}.")
        else:
            logger.debug(f"Column {column_name} already exists in {self.tablename}.")

        # 提交更改并关闭连接
        conn.commit()
        cursor.close()
        conn.close()


db_manager = _DBManager()

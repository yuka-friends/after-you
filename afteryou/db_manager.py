import datetime
import os
import sqlite3

import pandas as pd

from afteryou.config import config
from afteryou.logger import get_logger

logger = get_logger(__name__)


class _DBManager:
    def __init__(self) -> None:
        self.db_filepath = os.path.join(config.userdata_filepath, "afteryou.db")
        self.tablename_journal = "afteryou_journal"
        self.tablename_mail = "afteryou_mail"
        self.tablename_summary = "afteryou_summary"
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

        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.tablename_journal}'")
        if c.fetchone() is None:
            logger.info(f"{self.tablename_journal} is empty, writing new table.")
            query_journal = f"""CREATE TABLE {self.tablename_journal}
                   (user_timestamp INT,
                   user_note TEXT,
                   ai_character_emoji TEXT,
                   ai_reply_timestamp INT,
                   ai_reply_content TEXT,
                   should_ai_reply BOOLEAN,
                   img_filepath TEXT);"""
            self.db_create_table(query=query_journal)
            self.db_insert_data_to_journal(
                user_timestamp=int(datetime.datetime.now().timestamp()),
                user_note="Welcome to After you. 🥞",
                ai_character_emoji="🔮",
                ai_reply_timestamp=int(datetime.datetime.now().timestamp()),
                ai_reply_content="Hey there, great to meet you. How's your day going?",
                should_ai_reply=True,
                img_filepath="",
            )

        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.tablename_mail}'")
        if c.fetchone() is None:
            logger.info(f"{self.tablename_mail} is empty, writing new table.")
            query_journal = f"""CREATE TABLE {self.tablename_mail}
                   (mail_timestamp INT,
                   mail_from_name TEXT,
                   mail_content TEXT
                   mail_type TEXT);"""
            self.db_create_table(query=query_journal)
            self.db_insert_data_to_mail(
                mail_timestamp=int(datetime.datetime.now().timestamp()),
                mail_from_name="Haru",
                mail_content="Welcome to mail.",
                mail_type="system",
            )

        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.tablename_summary}'")
        if c.fetchone() is None:
            logger.info(f"{self.tablename_summary} is empty, writing new table.")
            query_journal = f"""CREATE TABLE {self.tablename_summary}
                   (summary_date TEXT,
                   summary_content TEXT,
                   keywords TEXT);"""
            self.db_create_table(query=query_journal)
            self.db_insert_data_to_mail(
                mail_timestamp=int(datetime.datetime.now().timestamp()),
                mail_from_name="Haru",
                mail_content="Welcome to mail.",
                mail_type="system",
            )

        conn.close()
        return is_db_exist

    # 创建表
    def db_create_table(self, query):
        logger.info("Making table")
        conn = sqlite3.connect(self.db_filepath)
        conn.execute(query)
        conn.close()

    # 插入日记数据
    def db_insert_data_to_journal(
        self,
        user_timestamp: int,
        user_note: str,
        ai_character_emoji: str,
        ai_reply_timestamp: int,
        ai_reply_content: str,
        should_ai_reply: bool,
        img_filepath: str,
    ):
        user_note = user_note.replace("'", "''")
        ai_reply_content = ai_reply_content.replace("'", "''")

        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        query = f"INSERT INTO {self.tablename_journal} (user_timestamp, user_note, ai_character_emoji, ai_reply_timestamp, ai_reply_content, should_ai_reply, img_filepath) VALUES (?, ?, ?, ?, ?, ?, ?)"

        logger.info(f"Inserting data: {query}")

        c.execute(
            query,
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

    # 插入邮件数据
    def db_insert_data_to_mail(
        self,
        mail_timestamp: int,
        mail_from_name: str,
        mail_content: str,
        mail_type: str,
    ):
        mail_from_name = mail_from_name.replace("'", "''")
        mail_content = mail_content.replace("'", "''")

        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        query = (
            f"INSERT INTO {self.tablename_mail} (mail_timestamp, mail_from_name, mail_content, mail_type) VALUES (?, ?, ?, ?)"
        )

        logger.info(f"Inserting data: {query}")

        c.execute(
            query,
            (int(mail_timestamp), mail_from_name, mail_content, mail_type),
        )
        conn.commit()
        conn.close()

    # 插入总结数据
    def db_insert_data_to_summary(self, summary_date: datetime.date, summary_content: str, keywords: list):
        summary_content = summary_content.replace("'", "''")

        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        query = f"INSERT INTO {self.tablename_summary} (summary_date, summary_content, keywords) VALUES (?, ?, ?)"

        logger.info(f"Inserting data: {query}")

        c.execute(
            query,
            (summary_date, summary_content, keywords),
        )
        conn.commit()
        conn.close()

    # 根据出入时间戳获取时间段数据
    def db_get_range_by_timestamp(self, start_timestamp: int, end_timestamp: int):
        conn = sqlite3.connect(self.db_filepath)
        query = f"""
        SELECT *
        FROM {self.tablename_journal}
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
        query = f"DELETE FROM {self.tablename_journal} WHERE user_timestamp = ?"
        logger.info(f"Delete: {query}")
        c.execute(query, (timestamp,))
        conn.commit()
        conn.close()

    # 根据用户时间戳修改对应行
    def update_row_by_timestamp(self, timestamp, column_name, update_content):
        if type(update_content) is str:
            update_content = update_content.replace("'", "''")

        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        query = f"UPDATE {self.tablename_journal} SET {column_name} = ? WHERE user_timestamp = ?"
        logger.info(f"Modify: {query}")
        c.execute(query, (update_content, timestamp))
        conn.commit()
        conn.close()

    def read_sqlite_table_to_dataframe(self, table_name):
        conn = sqlite3.connect(self.db_filepath)
        df = pd.read_sql_query("SELECT * from {}".format(table_name), conn)
        conn.close()
        return df

    # 检查 column_name 列是否存在，若无则新增
    def db_ensure_row_exist(self, column_name, column_type):
        conn = sqlite3.connect(self.db_filepath)
        cursor = conn.cursor()

        # 查询表信息
        cursor.execute(f"PRAGMA table_info({self.tablename_journal});")
        table_info = cursor.fetchall()

        # 检查新列是否已存在
        if column_name not in [column[1] for column in table_info]:
            # 新列不存在，添加新列
            cursor.execute(f"ALTER TABLE {self.tablename_journal} ADD COLUMN {column_name} {column_type};")
            logger.info(f"Column {column_name} added to {self.tablename_journal}.")
        else:
            logger.debug(f"Column {column_name} already exists in {self.tablename_journal}.")

        # 提交更改并关闭连接
        conn.commit()
        cursor.close()
        conn.close()


db_manager = _DBManager()

import datetime
import os
import sqlite3
from pathlib import Path

import pandas as pd

from afteryou.logger import get_logger
from afteryou.sys_path import FILEPATH_DB

logger = get_logger(__name__)


class _DBManager:
    def __init__(self) -> None:
        self.db_filepath = FILEPATH_DB
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
                user_note="Welcome to After you. Come add your first thought!🥞",
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
                   mail_content TEXT,
                   mail_type TEXT);"""
            mail_start = Path("afteryou\\src\\mail_welcome.md").read_text(encoding="utf-8")
            self.db_create_table(query=query_journal)
            self.db_insert_data_to_mail(
                mail_timestamp=int(datetime.datetime.now().timestamp()),
                mail_from_name="Haru",
                mail_content=mail_start,
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
            self.db_insert_data_to_summary(summary_date="", summary_content="", keywords="")

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
        # user_note = user_note.replace("'", "''")
        # ai_reply_content = ai_reply_content.replace("'", "''")

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
        # mail_from_name = mail_from_name.replace("'", "''")
        # mail_content = mail_content.replace("'", "''")

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
        # summary_content = summary_content.replace("'", "''")

        keywords_str = ", ".join(str(i) for i in keywords)
        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        query = f"INSERT INTO {self.tablename_summary} (summary_date, summary_content, keywords) VALUES (?, ?, ?)"

        logger.info(f"Inserting data: {query}")

        c.execute(
            query,
            (summary_date, summary_content, keywords_str),
        )
        conn.commit()
        conn.close()

    # 根据出入时间戳获取日记时间段数据
    def db_get_df_range_by_timestamp_in_table_journal(self, start_timestamp: int, end_timestamp: int):
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

    # 根据出入日期获取总结时间段数据
    def db_get_range_by_date_in_table_summary(self, date_start: datetime.date, date_end: datetime.date):
        conn = sqlite3.connect(self.db_filepath)
        sql = f"SELECT * FROM {self.tablename_summary} WHERE summary_date BETWEEN ? AND ?"
        start_date_string = date_start.strftime("%Y-%m-%d")
        end_date_string = date_end.strftime("%Y-%m-%d")
        df = pd.read_sql_query(sql, conn, params=(start_date_string, end_date_string))
        conn.close()
        return df

    # 创建查询语句
    sql = "SELECT * FROM A WHERE summary_date BETWEEN ? AND ?"

    # 根据用户时间戳删除日记对应行
    def delete_journal_row_by_timestamp(self, timestamp):
        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        query = f"DELETE FROM {self.tablename_journal} WHERE user_timestamp = ?"
        logger.info(f"Delete: {query}")
        c.execute(query, (timestamp,))
        conn.commit()
        conn.close()

    # 根据用户时间戳删除总结对应行
    def delete_summary_row_by_date(self, input_date: datetime.date):
        date_string = input_date.strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        query = f"DELETE FROM {self.tablename_summary} WHERE summary_date = ?"
        logger.info(f"Delete: {query}")
        c.execute(query, (date_string,))
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

    def db_earliest_latest_journal_time(self):
        """获取日记数据最早与最晚时间"""
        conn = sqlite3.connect(self.db_filepath)
        c = conn.cursor()
        c.execute(f"SELECT min(user_timestamp), max(user_timestamp) FROM {self.tablename_journal}")
        result = c.fetchone()
        conn.close()
        return result

    def db_search_data_journal(self, keywords, exclude_words, start_timestamp, end_timestamp):
        """搜索日记数据"""
        keywords = keywords.replace("'", "''")
        exclude_words = exclude_words.replace("'", "''")
        keyword_list = keywords.split(" ")
        exclude_list = exclude_words.split(" ")

        # 构建查询的where语句
        keyword_query = " AND ".join(
            ["(user_note LIKE '%{}%' OR ai_reply_content LIKE '%{}%')".format(word, word) for word in keyword_list]
        )
        if len(exclude_words) > 0:
            exclude_query = "AND" + " AND ".join(
                [
                    "(user_note NOT LIKE '%{}%' AND ai_reply_content NOT LIKE '%{}%')".format(word, word)
                    for word in exclude_list
                ]
            )
        else:
            exclude_query = ""
        timestamp_query = "user_timestamp BETWEEN {} AND {}".format(start_timestamp, end_timestamp)

        # 构建完整的SQL查询语句
        sql = "SELECT * FROM {} WHERE {} {} AND {}".format(
            self.tablename_journal, keyword_query, exclude_query, timestamp_query
        )

        logger.info(sql)
        conn = sqlite3.connect(self.db_filepath)
        df = pd.read_sql_query(sql, conn)
        conn.close()

        return df

    def db_get_jounal_df_by_day(self, input_date: datetime.date):
        """根据日期获取日记数据"""
        start_timestamp = int(datetime.datetime.combine(input_date, datetime.time(0, 0, 1)).timestamp())
        end_timestamp = int(datetime.datetime.combine(input_date, datetime.time(23, 23, 59)).timestamp())
        df_day = self.db_get_df_range_by_timestamp_in_table_journal(
            start_timestamp=start_timestamp, end_timestamp=end_timestamp
        )
        return df_day

    def db_get_rowid_and_similar_tuple_list_rows(self, rowid_probs_list):
        """
        根据 rowid - 相似度 元组构成的 list 提取数据库文件对应行与标注对应相似度，合在以 dataframe 形式返回
        """
        db_filepath = self.db_filepath
        conn = sqlite3.connect(db_filepath)
        rowid_list = [tuple[0] for tuple in rowid_probs_list]
        probs_list = [tuple[1] for tuple in rowid_probs_list]
        rowid_str = ",".join(map(str, rowid_list))  # 将 rowid 列表转换为逗号分隔的字符串

        # 构建SQL查询语句
        query = f"SELECT * FROM {self.tablename_journal} WHERE rowid IN ({rowid_str})"
        result_df = pd.read_sql_query(query, conn)
        conn.close()

        result_df["probs"] = probs_list
        return result_df

    def query_rowid(self, timestamp):
        """根据时间戳搜索 journal 对应行的 rowid"""
        conn = sqlite3.connect(self.db_filepath)
        cursor = conn.cursor()
        cursor.execute(f"SELECT rowid FROM {self.tablename_journal} WHERE user_timestamp=?", (timestamp,))
        result = cursor.fetchone()
        conn.close()

        # 若查询结果为空，则返回None，不为空则返回rowid
        if result is None:
            return None
        else:
            return result[0]

    def db_get_summary_line_by_date(self, input_date: datetime.date):
        """根据日期获取总结数据"""
        conn = sqlite3.connect(self.db_filepath)
        date_string = input_date.strftime("%Y-%m-%d")
        sql = f"SELECT * FROM {self.tablename_summary} WHERE summary_date = ?"
        df = pd.read_sql_query(sql, conn, params=(date_string,))
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

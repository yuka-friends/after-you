import datetime

import streamlit as st
from openai import OpenAI

from afteryou import file_utils
from afteryou.config import config
from afteryou.db_manager import db_manager
from afteryou.logger import get_logger
from afteryou.sys_path import FILEPATH_CHARCTER, FILEPATH_CHARCTER_MAIL

logger = get_logger(__name__)


def get_random_character(filepath):
    character_df = file_utils.get_character_df(filepath)
    character_df = character_df[character_df["enable"] != False]  # noqa: E712
    return character_df.sample(n=1).to_dict(orient="records")[0]


def request_llm(
    user_content,
    system_prompt,
    temperature,
    emoji,
    api_key=config.openai_api_key,
    base_url=config.openai_url,
    model=config.model_name,
):
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        msg = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_content},
        ]
        logger.info(msg)
        completion = client.chat.completions.create(
            model=model,
            messages=msg,
            temperature=temperature,
        )
    except Exception as e:
        print(e)
        return None, "⛔"

    return completion.choices[0].message.content, emoji


def request_ai_reply_instant(text: str, api_key=config.openai_api_key, base_url=config.openai_url, model=config.model_name):
    ai_emoji = "😢"
    ai_reply = "Fail to get AI reply, please 🔮re-imagine or check 🔑api-key and try again."
    character_dict = get_random_character(FILEPATH_CHARCTER)
    system_prompt = str(
        config.system_prompt_prefix
        + character_dict["system_prompt"]
        + "Please reply in {reply_language}"
        + config.system_prompt_suffix
    ).format(
        user_name=config.username,
        datetime=datetime.datetime.now().strftime("date: %Y/%m/%d,time: %H-%M-%S"),
        weather="sunny",
        reply_language=config.reply_language,
    )
    with st.spinner("🔮 praying to crystal ball ..."):
        ai_reply, ai_emoji = request_llm(
            user_content=text,
            system_prompt=system_prompt,
            temperature=character_dict["temperature"],
            emoji=character_dict["emoji"],
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
    return ai_reply, ai_emoji


def request_ai_reply_mail(
    text: str,
    datetime_start: datetime.datetime,
    datetime_end: datetime.datetime,
    api_key=config.openai_api_key,
    base_url=config.openai_url,
    model=config.model_name,
):
    ai_emoji = "⛔"
    ai_reply = None
    character_dict = get_random_character(FILEPATH_CHARCTER_MAIL)
    system_prompt = str(
        config.system_prompt_mail_prefix
        + character_dict["system_prompt"]
        + "Please reply in {reply_language}"
        + config.system_prompt_mail_suffix
    ).format(
        user_name=config.username,
        datetime_start=datetime_start.strftime("date: %Y/%m/%d,time: %H-%M-%S"),
        datetime_end=datetime_end.strftime("date: %Y/%m/%d,time: %H-%M-%S"),
        reply_language=config.reply_language,
    )
    with st.spinner("🔮 praying to crystal ball ..."):
        ai_reply, ai_emoji = request_llm(
            user_content=text,
            system_prompt=system_prompt,
            temperature=character_dict["temperature"],
            emoji=character_dict["emoji"],
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
    return ai_reply, ai_emoji


def request_ai_summary(day: datetime.date):
    """总结一天"""
    start_timestamp = int(datetime.datetime.combine(day, datetime.time(0, 0, 1)).timestamp())
    end_timestamp = int(datetime.datetime.combine(day, datetime.time(23, 23, 59)).timestamp())
    df = db_manager.db_get_range_by_timestamp_in_table_journal(start_timestamp=start_timestamp, end_timestamp=end_timestamp)
    text = []
    for index, row in df.iterrows():
        text.append(row["user_note"])
    text_to_summary = "\n".join(text)
    with st.spinner("🔮 praying to crystal ball ..."):
        text_ai_summary, _ = request_llm(
            user_content=text_to_summary,
            system_prompt=config.system_prompt_summary,
            temperature=0.3,
            emoji="✍",
        )
        if text_ai_summary:
            db_manager.db_insert_data_to_summary(summary_date=day, summary_content=text_ai_summary, keywords=[])


def request_mail_by_day_range(date_start: datetime.date, date_end: datetime.date):
    """根据时间范围总结"""
    # 拉取db summary table数据，检查是否每天齐全
    # 不齐全的天就检查当天是否有数据，有则总结补齐
    # 用所有数据进入mail总结撰写
    days = date_end - date_start
    text = []
    for i in days.days:
        date_query = date_start + datetime.timedelta(days=i)
        row = db_manager.db_get_summary_line_by_date(input_date=date_query)
        if len(row) == 0:
            #
            pass
        else:
            text.append(row["summary_content"])

    pass

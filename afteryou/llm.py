import datetime

import streamlit as st
from openai import OpenAI

from afteryou import file_utils
from afteryou.config import config
from afteryou.db_manager import db_manager
from afteryou.logger import get_logger
from afteryou.sys_path import FILEPATH_CHARCTER, FILEPATH_CHARCTER_MAIL

logger = get_logger(__name__)
FAIL_COPY = "System: Fail to get AI reply, please 🔮re-imagine, check 🔑api-key or restart app and try again."

if (
    "open_ai_base_url" not in st.session_state
    or "open_ai_api_key" not in st.session_state
    or "open_ai_modelname" not in st.session_state
):
    st.session_state.open_ai_base_url = config.openai_url
    st.session_state.open_ai_api_key = config.openai_api_key
    st.session_state.open_ai_modelname = config.model_name


def get_random_character(filepath):
    character_df = file_utils.get_character_df(filepath)
    character_df = character_df[character_df["enable"] != False]  # noqa: E712
    return character_df.sample(n=1).to_dict(orient="records")[0]


def request_llm_one_shot(
    user_content,
    system_prompt,
    temperature,
    emoji,
    api_key=st.session_state.open_ai_api_key,
    base_url=st.session_state.open_ai_base_url,
    model=st.session_state.open_ai_modelname,
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
        logger.error(e)
        return FAIL_COPY, "⛔"

    return completion.choices[0].message.content, emoji


def request_llm_custom_msg(
    msg,
    temperature,
    emoji,
    api_key=st.session_state.open_ai_api_key,
    base_url=st.session_state.open_ai_base_url,
    model=st.session_state.open_ai_modelname,
):
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        logger.info(msg)
        completion = client.chat.completions.create(
            model=model,
            messages=msg,
            temperature=temperature,
        )
    except Exception as e:
        logger.error(e)
        return FAIL_COPY, "⛔"

    return completion.choices[0].message.content, emoji


def request_ai_reply_instant(
    text: str,
    datetime_input=datetime.datetime.now(),
    api_key=st.session_state.open_ai_api_key,
    base_url=st.session_state.open_ai_base_url,
    model=st.session_state.open_ai_modelname,
):
    character_dict = get_random_character(FILEPATH_CHARCTER)
    system_prompt = str(
        config.system_prompt_prefix
        + character_dict["system_prompt"]
        + "Please reply in {reply_language}"
        + config.system_prompt_suffix
    ).format(
        user_name=config.username,
        datetime=datetime_input.strftime("date: %Y/%m/%d,time: %H-%M-%S"),
        weather="sunny",
        reply_language=config.reply_language,
    )
    with st.spinner("🔮 praying to crystal ball ..."):
        if config.multi_turn_conversation_memory > 1:  # 多轮记忆
            start_timestamp = int(datetime_input.replace(hour=0, minute=0, second=1).timestamp())
            end_timestamp = int(datetime_input.replace(hour=23, minute=59, second=59).timestamp())
            df = db_manager.db_get_df_range_by_timestamp_in_table_journal(
                start_timestamp=start_timestamp, end_timestamp=end_timestamp
            )
            msg = [
                {
                    "role": "system",
                    "content": system_prompt,
                }
            ]
            if df is not None:
                df = df.sort_index(ascending=False).reset_index(drop=True)
                for i in range(config.multi_turn_conversation_memory):
                    if i > len(df) - 1:
                        break
                    msg.append({"role": "user", "content": df.iloc[i]["user_note"]})
                    if df.iloc[i]["ai_reply_content"]:
                        msg.append({"role": "assistant", "content": df.iloc[i]["ai_reply_content"]})
                    else:
                        msg.append({"role": "assistant", "content": "ok"})
            msg.append({"role": "user", "content": text})

            ai_reply, ai_emoji = request_llm_custom_msg(
                msg=msg,
                temperature=character_dict["temperature"],
                emoji=character_dict["emoji"],
                api_key=api_key,
                base_url=base_url,
                model=model,
            )
        else:
            ai_reply, ai_emoji = request_llm_one_shot(
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
    end_timestamp = int(datetime.datetime.combine(day, datetime.time(23, 59, 59)).timestamp())
    df = db_manager.db_get_df_range_by_timestamp_in_table_journal(start_timestamp=start_timestamp, end_timestamp=end_timestamp)
    text = []
    for index, row in df.iterrows():
        text.append(row["user_note"])
    text_to_summary = "\n".join(text)
    with st.spinner("🔮 praying to crystal ball ..."):
        text_ai_summary, _ = request_llm_one_shot(
            user_content=text_to_summary,
            system_prompt=config.system_prompt_summary,
            temperature=0.3,
            emoji="✍",
        )
        if text_ai_summary:
            db_manager.delete_summary_row_by_date(input_date=day)
            db_manager.db_insert_data_to_summary(summary_date=day, summary_content=text_ai_summary, keywords=[])
            return text_ai_summary
        else:
            return None


def request_mail_by_day_range(date_start: datetime.date, date_end: datetime.date):
    """根据时间范围总结"""
    # 拉取db summary table数据，检查是否每天齐全
    # 不齐全的天就检查当天是否有数据，有则总结补齐
    # 用所有数据进入mail总结撰写
    days = date_end - date_start
    text = []
    for i in range(days.days):
        date_query = date_start + datetime.timedelta(days=i)
        row = db_manager.db_get_summary_line_by_date(input_date=date_query)  # 在总结表中获取日的总结
        if len(row) == 0:
            df_day = db_manager.db_get_jounal_df_by_day(input_date=date_query)
            if df_day is None: # FIXME 去掉所有none！！！
                continue
            if len(df_day) > 0:  # 如果当日有记录，进行总结
                summary_content = request_ai_summary(day=date_query)
                if summary_content:
                    text.append(summary_content)
        else:
            text.append(row["summary_content"])

    character_dict = get_random_character(FILEPATH_CHARCTER_MAIL)
    text_to_request_mail = "\n".join(text)
    text_to_request_mail = text_to_request_mail[: config.max_token_summary_input]  # token长度限制
    system_prompt = str(
        config.system_prompt_mail_prefix
        + character_dict["system_prompt"]
        + config.system_prompt_mail_suffix
        + "Please reply in {reply_language}"
    ).format(
        user_name=config.username,
        datetime_start=date_start.strftime("date: %Y-%m-%d"),
        datetime_end=date_end.strftime("date: %Y-%m-%d"),
        reply_language=config.reply_language,
    )
    text_letter, _ = request_llm_one_shot(
        user_content=text_to_request_mail,
        system_prompt=system_prompt,
        temperature=character_dict["temperature"],
        emoji=character_dict["emoji"],
    )
    if text_letter:
        db_manager.db_insert_data_to_mail(
            mail_timestamp=int(
                datetime.datetime.combine(
                    date_end,
                    datetime.time(
                        datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second
                    ),
                ).timestamp()
            ),
            mail_from_name=character_dict["emoji"],
            mail_content=text_letter,
            mail_type="llm_sunday",
        )


def request_mail_by_festival(special_date: tuple):
    """根据节日写信"""
    ai_emoji = "😢"
    ai_reply = FAIL_COPY
    character_dict = get_random_character(FILEPATH_CHARCTER_MAIL)
    system_prompt = str(
        config.system_prompt_mail_special_day_prefix + character_dict["system_prompt"] + "Please reply in {reply_language}"
    ).format(
        user_name=config.username,
        date=special_date[0][0].strftime("date: %Y-%m-%d"),
        festival=special_date[0][1],
        reply_language=config.reply_language,
    )
    with st.spinner("🔮 praying to crystal ball ..."):
        ai_reply, ai_emoji = request_llm_one_shot(
            user_content="期待收到你的回信！",
            system_prompt=system_prompt,
            temperature=character_dict["temperature"],
            emoji=character_dict["emoji"],
        )
        if ai_reply:
            db_manager.db_insert_data_to_mail(
                mail_timestamp=int(
                    datetime.datetime.combine(
                        special_date[0][0],
                        datetime.time(
                            datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second
                        ),
                    ).timestamp()
                ),
                mail_from_name=character_dict["emoji"],
                mail_content=ai_reply,
                mail_type="llm_festival",
            )

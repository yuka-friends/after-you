import datetime

import streamlit as st
from openai import OpenAI

from afteryou import file_utils
from afteryou.config import config
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
    ai_emoji = "⛔"
    ai_reply = None
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

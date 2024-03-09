import time
from pathlib import Path

import streamlit as st

from afteryou import __version__, file_utils, llm
from afteryou.config import config
from afteryou.sys_path import FILEPATH_CHARCTER, FILEPATH_CHARCTER_MAIL


def render():
    col1, col2, col3 = st.columns([1, 1.5, 0.5])
    with col1:
        st.markdown("### 😉 About you")
        col_us1, col_us2 = st.columns([1, 1])
        with col_us1:
            input_username = st.text_input("your name", value=config.username)
        with col_us2:
            input_weather_city = st.text_input(
                "weather city",
                value=config.weather_location,
                help="Under development, please stay tuned.",
                disabled=True,
            )

        st.divider()

        st.markdown("### ✨ AI service")
        input_api_type = st.selectbox("LLM API", ["OpenAI compatible"])
        input_api_url = st.text_input("API url", value=config.openai_url)
        input_api_key = st.text_input("API key", value=config.openai_api_key)
        input_model_name = st.text_input("model name", value=config.model_name)
        if st.button("Test API"):
            with st.spinner("testing"):
                res, emoji = llm.request_ai_reply_instant(
                    "hi", api_key=input_api_key, base_url=input_api_url, model=input_model_name
                )
            if res is None:
                st.error("⛔ test failed. Please check cache\\log for more details.")
            else:
                st.markdown(f"`{emoji}: {res}`")

        st.divider()
        st.markdown("### 🛠️ General")
        input_reply_language = st.selectbox("Reply language", ["Simple Chinese (简体中文)", "English"])

        st.divider()

    with col2:
        st.markdown("### 🔮 Crystal")
        st.markdown(
            """
Each AI reply will be randomly choosed from the following character description. At least one character needs to be enabled.
"""
        )
        st.markdown("##### Instant reply")
        df_character = file_utils.get_character_df(FILEPATH_CHARCTER)
        df_character_editor = st.data_editor(
            df_character,
            height=240,
            column_config={
                "emoji": st.column_config.TextColumn(
                    "emoji", help="Please enter the emoji only to represent the character", max_chars=4, width="small"
                ),
                "enable": st.column_config.CheckboxColumn("enable", help="Enable this character", width="small"),
                "temperature": st.column_config.NumberColumn(
                    "temperature", help="Creative for this character. Range: 0~1.", min_value=0.0, max_value=1.0, width="small"
                ),
                "note": st.column_config.TextColumn(
                    "note", help="Won't affect the character, just for introduction", width="medium"
                ),
                "system_prompt": st.column_config.TextColumn("character setting", help="System prompt for this character"),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
        )

        st.markdown("##### Mail reply")
        df_character_mail = file_utils.get_character_df(FILEPATH_CHARCTER_MAIL)
        df_character_mail_editor = st.data_editor(
            df_character_mail,
            height=240,
            column_config={
                "emoji": st.column_config.TextColumn(
                    "emoji", help="Please enter the emoji only to represent the character", max_chars=4, width="small"
                ),
                "enable": st.column_config.CheckboxColumn("enable", help="Enable this character", width="small"),
                "temperature": st.column_config.NumberColumn(
                    "temperature", help="Creative for this character. Range: 0~1.", min_value=0.0, max_value=1.0, width="small"
                ),
                "note": st.column_config.TextColumn(
                    "note", help="Won't affect the character, just for introduction", width="medium"
                ),
                "system_prompt": st.column_config.TextColumn("character setting", help="System prompt for this character"),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
        )

        if st.button("Save character sheet", type="secondary"):
            df_character_editor.dropna(how="all")
            df_character_mail_editor.dropna(how="all")
            if not all_rows_filled(df_character_editor) or not all_rows_filled(df_character_mail_editor):
                st.error("Please fill all rows.")
            elif not check_at_least_one_enable(df_character_editor) or not check_at_least_one_enable(df_character_mail_editor):
                st.error("Please enable at least one character.")
            else:
                file_utils.save_dataframe_to_path(df_character_editor, FILEPATH_CHARCTER)
                file_utils.save_dataframe_to_path(df_character_mail_editor, FILEPATH_CHARCTER_MAIL)
                st.success("🔮 saved.")

    with col3:
        st.empty()
        update_info = "update to date"
        if "is_new_version" in st.session_state:
            if st.session_state.is_new_version:
                update_info = " ✨ new version available! Exit and open `install_update.bat` to update."
        about_markdown = (
            Path("afteryou\\src\\about_en.md")
            .read_text(encoding="utf-8")
            .format(
                version=__version__,
                update_info=update_info,
            )
        )
        st.markdown(about_markdown, unsafe_allow_html=True)

    if st.button("Save and apply settings", type="primary"):
        input_api_type
        config.set_and_save_config("username", input_username)
        config.set_and_save_config("weather_location", input_weather_city)
        config.set_and_save_config("openai_url", input_api_url)
        config.set_and_save_config("openai_api_key", input_api_key)
        config.set_and_save_config("model_name", input_model_name)
        config.set_and_save_config("reply_language", input_reply_language)
        st.success("🔮 saved.")
        time.sleep(1)
        st.rerun()


def all_rows_filled(df):
    return df.dropna().shape[0] == df.shape[0]


def check_at_least_one_enable(df):
    if "enable" in df.columns:
        return df["enable"].any()
    else:
        return False

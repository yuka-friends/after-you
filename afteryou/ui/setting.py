import hashlib
import os
import time
from pathlib import Path

import streamlit as st

from afteryou import __version__, file_utils, llm, utils
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
        input_api_type = st.selectbox("LLM API", ["OpenAI compatible"], disabled=True)
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

        input_multi_turn_conversation_memory = st.number_input(
            "Multi-turn conversation memory", value=3, min_value=1, max_value=10
        )

        checkbox_enable_embedding = st.checkbox(
            "Enable local embedding",
            value=config.enable_embedding,
            help="If disabled, similar journal search and image search will not be available, but can improve webui loading speed.",
        )

        st.divider()
        st.markdown("### 🛠️ General")
        input_reply_language = st.selectbox(
            "Reply language",
            [
                "Simplified Chinese (简体中文)",
                "Traditional Chinese (繁体中文)",
                "English",
                "Japanese (日本語)",
                "Korean (한국인)",
            ],
        )

        config_webui_access_password = st.text_input(
            "🔒 webui password",
            value=config.webui_access_password_md5,
            help="If password input filled, you will be asked to provide a password when accessing webui. This setting will not encrypt your data, but only protects the entrance to webui to avoid access by unfamiliar users in the same LAN.",
            type="password",
        )
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
            Path(os.path.join("afteryou", "src", "about_en.md"))
            .read_text(encoding="utf-8")
            .format(
                version=__version__,
                update_info=update_info,
            )
        )

        if "about_image_b64" not in st.session_state:
            st.session_state.about_image_b64 = utils.image_to_base64(os.path.join("__assets__", "about_header.png"))
        if "about_bg_image_b64" not in st.session_state:
            st.session_state.about_bg_image_b64 = utils.image_to_base64(os.path.join("__assets__", "color_heart_bg.png"))
        st.markdown(
            f"<img align='right' style='max-width: 100%;max-height: 100%;' src='data:image/png;base64, {st.session_state.about_image_b64}'/>",
            unsafe_allow_html=True,
        )
        st.markdown(about_markdown, unsafe_allow_html=True)
        st.markdown(
            f"<div style='margin-top: 12em'><img align='right' style='max-width: 100%;max-height: 100%;' src='data:image/png;base64, {st.session_state.about_bg_image_b64}'/></div>",
            unsafe_allow_html=True,
        )

    if st.button("Save and apply settings", type="primary"):
        input_api_type
        config.set_and_save_config("username", input_username)
        config.set_and_save_config("weather_location", input_weather_city)
        config.set_and_save_config("openai_url", input_api_url)
        config.set_and_save_config("openai_api_key", input_api_key)
        config.set_and_save_config("model_name", input_model_name)
        config.set_and_save_config("reply_language", input_reply_language)
        config.set_and_save_config("enable_embedding", checkbox_enable_embedding)
        config.set_and_save_config("multi_turn_conversation_memory", input_multi_turn_conversation_memory)

        # 如果有新密码输入，更改；如果留空，关闭功能
        if config_webui_access_password and config_webui_access_password != config.webui_access_password_md5:
            config.set_and_save_config(
                "webui_access_password_md5", hashlib.md5(config_webui_access_password.encode("utf-8")).hexdigest()
            )
        elif len(config_webui_access_password) == 0:
            config.set_and_save_config("webui_access_password_md5", "")

        st.session_state.open_ai_base_url = input_api_url
        st.session_state.open_ai_api_key = input_api_key
        st.session_state.open_ai_modelname = input_model_name

        st.success(
            "🔮 saved. If you change the api key and other related settings, you may need to restart the application to take effect. 如果更改了 api key 等相关设置，可能需要重启应用才能生效。"
        )
        time.sleep(1)


def all_rows_filled(df):
    return df.dropna().shape[0] == df.shape[0]


def check_at_least_one_enable(df):
    if "enable" in df.columns:
        return df["enable"].any()
    else:
        return False

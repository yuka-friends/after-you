import streamlit as st

from afteryou import file_utils, llm
from afteryou.config import config


def render():
    col1, col2, col3 = st.columns([1, 1.5, 0.5])
    with col1:
        st.markdown("### About you")
        col_us1, col_us2 = st.columns([1, 1])
        with col_us1:
            input_username = st.text_input("your name", value=config.username)
        with col_us2:
            input_weather_city = st.text_input(
                "weather city", value=config.weather_location, help="leave blank to disable weather for AI"
            )

        st.divider()

        st.markdown("### AI service")
        input_api_type = st.selectbox("LLM API", ["OpenAI compatible"])
        input_api_url = st.text_input("API url", value=config.openai_url)
        input_api_key = st.text_input("API key", value=config.openai_api_key)
        input_model_name = st.text_input("model name", value=config.model_name)
        if st.button("Test API"):
            with st.spinner("testing"):
                res, emoji = llm.request_llm("hi", api_key=input_api_key, base_url=input_api_url, model=input_model_name)
            if res is None:
                st.error("⛔ test failed. Please check cache\\log for more details.")
            else:
                st.markdown(f"`{emoji}: {res}`")

        st.divider()
        st.markdown("### General")
        input_ui_lang = st.selectbox("lang", ["sc", "en"])

        st.divider()

    with col2:
        st.markdown("### Crystal")
        FILEPATH_CHARCTER = "userdata\\character.csv"
        df_character = file_utils.get_character_df()
        df_character_editor = st.data_editor(
            df_character,
            height=500,
            column_config={
                "emoji": st.column_config.TextColumn("emoji", help="Please enter emoji", max_chars=4, width="small"),
                "enable": st.column_config.CheckboxColumn("enable", help="Enable this character", width="small"),
                "temperature": st.column_config.NumberColumn(
                    "temperature", help="Creative for this character. Range: 0~1.", min_value=0.0, max_value=1.0, width="small"
                ),
                "system_prompt": st.column_config.TextColumn("character setting", help="System prompt for this character"),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
        )
        if st.button("Save character sheet", type="secondary"):
            df_character_editor.dropna(how="all")
            if not all_rows_filled(df_character_editor):
                st.error("Please fill all rows.")
            else:
                file_utils.save_dataframe_to_path(df_character_editor, FILEPATH_CHARCTER)
                st.success("🔮 saved.")

    with col3:
        st.empty()

    if st.button("Save and apply settings", type="primary"):
        input_api_type
        config.set_and_save_config("username", input_username)
        config.set_and_save_config("weather_location", input_weather_city)
        config.set_and_save_config("openai_url", input_api_url)
        config.set_and_save_config("openai_api_key", input_api_key)
        config.set_and_save_config("model_name", input_model_name)
        config.set_and_save_config("ui_lang", input_ui_lang)
        st.toast("🔮 saved.")


def all_rows_filled(df):
    return df.dropna().shape[0] == df.shape[0]

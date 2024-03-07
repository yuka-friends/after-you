# import streamlit as st

# from afteryou.config import config

# def render():
#     col1, col2, col3 = st.columns([1, 0.5, 1.5])
#     with col1:
#         input_username = st.text_input("user name", value=config.username)
#         st.divider()
#         st.selectbox("LLM api", ["OpenAI compatible"])
#         st.text_input("api key", value=config.openai_api_key)

#         st.button("add character")
#         st.selectbox("lang", ["sc", "en"])

#     with col2:
#         st.empty()
#     with col3:
#         st.empty()


# def character_setting():
#     st.text_input("emoji", value=)
#     st.text_area("system prompt", value=)
#     st.slider("temperature", value=)

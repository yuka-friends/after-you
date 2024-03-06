import streamlit as st


def render():
    st.selectbox("LLM", ["groq"])
    st.text_input("api key")
    st.text_area("system prompt")
    st.button("add character")
    st.selectbox("lang", ["sc", "en"])
    pass

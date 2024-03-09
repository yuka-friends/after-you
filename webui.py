import os

import streamlit as st

from afteryou import embed_manager, routine
from afteryou.ui import daily, mailbox, search, setting

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

st.set_page_config(page_title="After you - webui", page_icon="🧡", layout="wide")
with open("afteryou\\src\\style.css", encoding="utf-8") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

if "embedding_model" not in st.session_state:
    with st.spinner("🔮 loading embedding model, please stand by..."):
        st.session_state.embedding_model = embed_manager.get_model(mode="cpu")


def render():
    st.markdown("##### 🧡 After you")

    tab_daily, tab_mailbox, tab_search, tab_setting = st.tabs(["daily", "mailbox", "search", "setting"])
    with tab_daily:
        daily.render()

    with tab_mailbox:
        mailbox.render()

    with tab_search:
        search.render()

    with tab_setting:
        setting.render()


routine.run_before()
render()

import streamlit as st

from afteryou.ui import daily, search, setting

st.set_page_config(page_title="After you - webui", page_icon="🧡", layout="wide")
with open("afteryou\\src\\style.css", encoding="utf-8") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

st.markdown("##### 🧡 After you")

tab_daily, tab_search, tab_setting = st.tabs(["daily", "search", "setting"])
with tab_daily:
    daily.render()

with tab_search:
    search.render()

with tab_setting:
    setting.render()

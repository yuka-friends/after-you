import os
import sys

import streamlit as st

from afteryou import embed_manager, routine, utils
from afteryou.config import config
from afteryou.exceptions import LockExistsException  # NOQA: E402
from afteryou.lock import FileLock  # NOQA: E402
from afteryou.sys_path import TRAY_LOCK_PATH
from afteryou.ui import daily, mailbox, search, setting

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.chdir(PROJECT_ROOT)


os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

st.set_page_config(page_title="After you - webui", page_icon="🧡", layout="wide")
with open("afteryou\\src\\style.css", encoding="utf-8") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

if "embedding_model" not in st.session_state and config.enable_embedding:
    with st.spinner("🔮 loading embedding model, please stand by..."):
        st.session_state.embedding_model = embed_manager.get_model(mode="cpu")

update_tip = ""
if "is_new_version" in st.session_state:
    if st.session_state.is_new_version:
        update_tip = " ✨ new version available!"


def render():
    if not config.openai_api_key:
        st.warning("It seems that the LLM api key is not setting, go to the settings set to setup.", icon="👋🏻")

    st.markdown(
        f"<h5 style='color:#977455'>🧡 {utils.greeting_based_on_time()}, {config.username}.</h5>", unsafe_allow_html=True
    )

    tab_daily, tab_mailbox, tab_search, tab_setting = st.tabs(["daily", "mailbox", "search", "setting" + update_tip])
    with tab_daily:
        daily.render()

    with tab_mailbox:
        mailbox.render()

    with tab_search:
        search.render()

    with tab_setting:
        setting.render()


def interrupt_start():
    sys.exit()


def main():
    # 启动时加锁，防止重复启动
    while True:
        try:
            tray_lock = FileLock(TRAY_LOCK_PATH, str(os.getpid()), timeout_s=None)
            break
        except LockExistsException:
            with open(TRAY_LOCK_PATH, encoding="utf-8") as f:
                check_pid = int(f.read())

            tray_is_running = utils.is_process_running(check_pid, compare_process_name="python.exe")
            if tray_is_running:
                print("    Another After you process is running.")
                interrupt_start()
            else:
                try:
                    os.remove(TRAY_LOCK_PATH)
                except FileNotFoundError:
                    pass

    with tray_lock:
        if "routine_run_before" not in st.session_state:
            st.session_state.routine_run_before = True
            routine.run_before()
        render()
        if "routine_run_after" not in st.session_state:
            st.session_state.routine_run_after = True
            routine.run_after()


main()

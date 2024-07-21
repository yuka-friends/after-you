import datetime
import hashlib
import os
import sys

import streamlit as st

from afteryou import file_utils
from afteryou.config import config  # NOQA: E402

if (
    "open_ai_base_url" not in st.session_state
    or "open_ai_api_key" not in st.session_state
    or "open_ai_modelname" not in st.session_state
):
    st.session_state.open_ai_base_url = config.openai_url
    st.session_state.open_ai_api_key = config.openai_api_key
    st.session_state.open_ai_modelname = config.model_name

from afteryou import embed_manager, routine, utils  # NOQA: E402

# from afteryou.exceptions import LockExistsException  # NOQA: E402
# from afteryou.lock import FileLock  # NOQA: E402
# from afteryou.sys_path import TRAY_LOCK_PATH
from afteryou.ui import daily, mailbox, search, setting  # NOQA: E402

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.chdir(PROJECT_ROOT)


os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

st.set_page_config(page_title="After you - webui", page_icon="🧡", layout="wide")
with open(os.path.join("afteryou", "src", "style.css"), encoding="utf-8") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

update_tip = ""
if "is_new_version" in st.session_state:
    if st.session_state.is_new_version:
        update_tip = " ✨ new version available!"


def render():
    if not config.openai_api_key:
        st.warning("It seems that the LLM api key is not setting, go to the settings set to setup.", icon="👋🏻")

    if "welcome_header_and_update_dt" not in st.session_state:
        st.session_state.welcome_header_and_update_dt = (utils.greeting_based_on_time(), datetime.datetime.now())
    elif datetime.datetime.now() - st.session_state.welcome_header_and_update_dt[1] > datetime.timedelta(hours=1):
        st.session_state.welcome_header_and_update_dt = (utils.greeting_based_on_time(), datetime.datetime.now())

    st.markdown(
        f"<h5 style='color:#977455'>🧡 {st.session_state.welcome_header_and_update_dt[0]}, {config.username}.</h5>",
        unsafe_allow_html=True,
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
    if "routine_run_before" not in st.session_state:
        st.session_state.routine_run_before = True
        routine.run_before()
    render()
    if "routine_run_after" not in st.session_state:
        st.session_state.routine_run_after = True
        routine.run_after()

    if "emb_model_text" not in st.session_state and config.enable_embedding:
        with st.spinner("🔮 loading embedding model, please stand by..."):
            (
                st.session_state["emb_model_text"],
                st.session_state["emb_model_image"],
                st.session_state["emb_processor_text"],
                st.session_state["emb_processor_image"],
            ) = embed_manager.get_model_and_processor()

            # 将未 embed 的日记片段 embed 到 vdb
            if "embed_not_index_journal_last_datetime_str" not in st.session_state:
                st.session_state.embed_not_index_journal_last_datetime_str = file_utils.get_cache_dict(
                    key_operate="embed_not_index_journal_last_datetime_str", operation="read"
                )

            embed_not_index_journal_condition = False
            if st.session_state.embed_not_index_journal_last_datetime_str is None:
                embed_not_index_journal_condition = True
            elif datetime.datetime.now() - utils.str_to_datetime(
                st.session_state.embed_not_index_journal_last_datetime_str
            ) > datetime.timedelta(
                hours=24,
            ):
                embed_not_index_journal_condition = True

            if embed_not_index_journal_condition:
                with st.spinner("🔮 Embedding not index journal..."):
                    embed_manager.embed_unembed_journal_to_vdb(
                        model_text=st.session_state["emb_model_text"], processor_text=st.session_state["emb_processor_text"]
                    )
                    file_utils.get_cache_dict(
                        key_operate="embed_not_index_journal_last_datetime_str",
                        value_operate=utils.datetime_to_str(datetime.datetime.now()),
                        operation="write",
                    )


# 检查 webui 是否启用密码保护
if "webui_password_accessed" not in st.session_state:
    st.session_state["webui_password_accessed"] = False

if config.webui_access_password_md5 and st.session_state.webui_password_accessed is False:
    col_pwd1, col_pwd2 = st.columns([1, 2])
    with col_pwd1:
        password = st.text_input(
            "🔒 Password:",
            type="password",
            help="Forgot your password? Delete the webui_access_password_md5 item in config_user.json to reset password.",
        )
    with col_pwd2:
        st.empty()
    if hashlib.md5(password.encode("utf-8")).hexdigest() == config.webui_access_password_md5:
        st.session_state.webui_password_accessed = True

if not config.webui_access_password_md5 or st.session_state.webui_password_accessed is True:
    main()

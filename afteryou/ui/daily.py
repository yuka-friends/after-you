import datetime

import streamlit as st

from afteryou import embed_manager, llm, web_component
from afteryou.db_manager import db_manager
from afteryou.logger import get_logger

logger = get_logger(__name__)


def render():
    # 初始化
    if "day_date_input" not in st.session_state:
        st.session_state["day_date_input"] = datetime.date.today()
    if "user_input_text" not in st.session_state:
        st.session_state["user_input_text"] = ""

    date_selector()
    title_render()
    add_thought()

    col1, col2, col3 = st.columns([1, 1, 1])
    # FIXME 懒加载
    with col1:
        st.empty()
        render_day_data(st.session_state.day_date_input - datetime.timedelta(days=1))
    with col2:
        st.empty()
        render_day_data(st.session_state.day_date_input, dim=False)
    with col3:
        st.empty()
        render_day_data(st.session_state.day_date_input + datetime.timedelta(days=1))


def date_selector():
    col_day_0, col_day_1, col_day_2, col_day_3, col_day_4, col_day_5 = st.columns([1, 0.25, 0.25, 0.25, 0.25, 1])
    with col_day_0:
        st.empty()
    with col_day_1:
        if st.button("←", use_container_width=True):
            st.session_state.day_date_input -= datetime.timedelta(days=1)
    with col_day_2:
        if st.button("→", use_container_width=True):
            st.session_state.day_date_input += datetime.timedelta(days=1)
    with col_day_3:
        if st.button("today", use_container_width=True):
            st.session_state.day_date_input = datetime.date.today()
    with col_day_4:
        st.session_state.day_date_input = st.date_input(
            "Today Date", label_visibility="collapsed", value=st.session_state.day_date_input
        )
    with col_day_5:
        st.empty()


def add_thought():
    def submit_user_input_area():
        text = st.session_state.text_area_add_thought
        if text.strip():
            time_now = datetime.datetime.now()
            datetime_user = datetime.datetime.combine(
                st.session_state.day_date_input, datetime.time(time_now.hour, time_now.minute, time_now.second)
            )
            if st.session_state.toggle_should_reply:
                ai_reply, ai_emoji = llm.request_ai_reply_instant(text)
            else:
                ai_reply, ai_emoji = "", "⛔️"

            db_manager.db_insert_data_to_journal(
                user_timestamp=datetime_user.timestamp(),
                user_note=text,
                ai_character_emoji=ai_emoji,
                ai_reply_timestamp=datetime.datetime.now().timestamp(),
                ai_reply_content=ai_reply,
                should_ai_reply=st.session_state.toggle_should_reply,
                img_filepath="",
            )
            embed_manager.embed_journal_to_vdb(
                model=st.session_state.embedding_model,
                user_timestamp=datetime_user.timestamp(),
                user_note=text,
                ai_reply_content=ai_reply,
            )
            st.session_state.text_area_add_thought = ""

    col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
    with col_t1:
        st.empty()
    with col_t2:
        st.session_state.user_input_text = st.text_area(
            "add thought",
            label_visibility="collapsed",
            placeholder="Add thought",
            key="text_area_add_thought",
            on_change=submit_user_input_area,
        )
        col_submit1, col_submit2, col_submit3 = st.columns([0.5, 1, 3])
        with col_submit1:
            st.toggle("🔮", key="toggle_should_reply", value=True)
        with col_submit2:
            st.checkbox("Picture", disabled=True, help="Under development, please stay tuned")
        with col_submit3:
            st.markdown(
                "<p align='right' style='color:rgba(255,255,255,.1)'> Ctrl + Enter to submit</p>", unsafe_allow_html=True
            )

        st.empty()
    with col_t3:
        st.empty()


def title_render():
    col_title1, col_title2, col_title3 = st.columns([1, 1, 1])
    with col_title1:
        web_component.render_title(st.session_state.day_date_input - datetime.timedelta(days=1), dim=True)
    with col_title2:
        web_component.render_title(st.session_state.day_date_input)
    with col_title3:
        web_component.render_title(st.session_state.day_date_input + datetime.timedelta(days=1), dim=True)


def render_summary_data(input_date, dim=True):
    summary_content_df = db_manager.db_get_summary_line_by_date(input_date=input_date)
    if input_date == datetime.date.today():
        return
    if len(summary_content_df) > 0:
        summary_content = summary_content_df.iloc[0]["summary_content"]
    else:
        summary_content = ""
    web_component.render_summary(day=input_date, summary_content=summary_content, dim=dim)


def render_day_data(day_date_input, dim=True, column=0):
    res_df = db_manager.db_get_df_range_by_timestamp_in_table_journal(
        start_timestamp=datetime.datetime.combine(day_date_input, datetime.time(0, 0, 1)).timestamp(),
        end_timestamp=datetime.datetime.combine(day_date_input, datetime.time(23, 23, 59)).timestamp(),
    )
    if res_df is not None:
        render_summary_data(day_date_input, dim=dim)
        for index, row in res_df[::-1].iterrows():
            web_component.render_paragraph(
                timestamp=row["user_timestamp"],
                user_content=row["user_note"],
                ai_content=row["ai_reply_content"],
                ai_emoji=row["ai_character_emoji"],
                dim=dim,
                index=str(column) + "_" + str(index),
            )

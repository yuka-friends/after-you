import datetime

import pandas as pd
import streamlit as st

from afteryou import embed_manager, web_component
from afteryou.config import config
from afteryou.db_manager import db_manager


def clean_lazy_state_after_change_search_method():
    """
    在切换搜索方式后，清理之前搜索留下的 tab 下其他 UI 部分使用到的数据
    """
    st.session_state.search_content = ""
    st.session_state.db_global_search_result = pd.DataFrame()


def render():
    # 初始化全局状态
    if "search_date_range_in" not in st.session_state:
        st.session_state.search_date_range_in = datetime.datetime.today() - datetime.timedelta(seconds=86400)
    if "search_date_range_out" not in st.session_state:
        st.session_state.search_date_range_out = datetime.datetime.today()
    if "search_latest_record_time_int" not in st.session_state or "search_earlist_record_time_int" not in st.session_state:
        (
            st.session_state["search_earlist_record_time_int"],
            st.session_state["search_latest_record_time_int"],
        ) = db_manager.db_earliest_latest_journal_time()
    if "db_global_search_result" not in st.session_state:
        st.session_state["db_global_search_result"] = pd.DataFrame()
    if "search_content" not in st.session_state:
        st.session_state.search_content = ""
    if "search_content_exclude" not in st.session_state:
        st.session_state.search_content_exclude = ""

    if "search_content_lazy" not in st.session_state:
        st.session_state.search_content_lazy = ""
    if "search_content_exclude_lazy" not in st.session_state:
        st.session_state.search_content_exclude_lazy = None
    if "search_date_range_in_lazy" not in st.session_state:
        st.session_state.search_date_range_in_lazy = (
            datetime.datetime(1970, 1, 2)
            + datetime.timedelta(seconds=st.session_state.search_earlist_record_time_int)
            - datetime.timedelta(seconds=86400)
        )
    if "search_date_range_out_lazy" not in st.session_state:
        st.session_state.search_date_range_out_lazy = (
            datetime.datetime(1970, 1, 2)
            + datetime.timedelta(seconds=st.session_state.search_latest_record_time_int)
            - datetime.timedelta(seconds=86400)
        )

    search_col, gap_col1, thought_col, gap_col2 = st.columns([1, 0.25, 1.2, 0.5])
    with search_col:
        search_method_list = ["keyword search", "similar text search", "image semantic search"]
        title_col, search_method = st.columns([4, 2.5])
        with title_col:
            st.markdown("### 🔍 Search")
        with search_method:
            st.session_state.search_method_selected = st.selectbox(
                "Search Method",
                search_method_list,
                label_visibility="collapsed",
                on_change=clean_lazy_state_after_change_search_method,
            )

        match search_method_list.index(st.session_state.search_method_selected):
            case 0:
                keyword_search()
            case 1:
                similar_text_search()
            case 2:
                image_semantic_search()

        # 搜索结果表格的 UI
        if not len(st.session_state.search_content) == 0:
            df = st.session_state.db_global_search_result

            st.markdown(
                "`"
                + 'Found {all_result_counts} results for "{search_content}".'.format(
                    all_result_counts=len(st.session_state.db_global_search_result),
                    search_content=st.session_state.search_content,
                )
                + "`"
            )

            # 滑杆选择
            result_choose_num = result_selector(df)

            if len(df) == 0:
                st.info(
                    'No results found for "{search_content}".'.format(search_content=st.session_state.search_content),
                    icon="🎐",
                )
            else:
                # 打表
                result_dataframe(df, heightIn=800)

        else:
            st.info(
                "This is the global search page where you can search all the journal content to date. Press Enter to search after entering the keywords."
            )  # 搜索内容为空时显示指引
            st.session_state.db_global_search_result = pd.DataFrame()

    with gap_col1:
        st.empty()

    with thought_col:
        # 右侧选择展示journal snippet的 UI
        if not len(st.session_state.db_global_search_result) == 0:
            show_and_locate_journal_snippet_by_df(st.session_state.db_global_search_result, result_choose_num)
        else:
            st.empty()

    with gap_col2:
        st.empty()


# 搜索页的 UI 通用输入组件
def ui_component_date_range_selector():
    """
    组件-日期选择器
    """
    try:
        (
            st.session_state.search_date_range_in,
            st.session_state.search_date_range_out,
        ) = st.date_input(
            "Date Range",
            (
                datetime.datetime(1970, 1, 2)
                + datetime.timedelta(seconds=st.session_state.search_earlist_record_time_int)
                - datetime.timedelta(seconds=86400),
                datetime.datetime(1970, 1, 2)
                + datetime.timedelta(seconds=st.session_state.search_latest_record_time_int)
                - datetime.timedelta(seconds=86400),
            ),
            format="YYYY-MM-DD",
        )
    except Exception:
        st.warning("Please select a complete time range")


# 选择结果的行数 的滑杆组件
def result_selector(df):
    if len(df) == 1:
        # 如果结果只有一个，直接显示结果而不显示滑杆
        return 0
    elif len(df) > 1:
        slider_min_num_display = df.index.min()
        slider_max_num_display = df.index.max()
        select_num = slider_min_num_display

        # 使用滑杆选择视频
        select_num = st.slider(
            "Drag to view search results",
            slider_min_num_display,
            slider_max_num_display,
            select_num,
        )

        select_num_real = select_num - slider_min_num_display  # 将绝对范围转换到从0开始的相对范围

        return select_num_real
    else:
        return 0


def result_dataframe(df, heightIn=800):
    df["datetime"] = pd.to_datetime(df["user_timestamp"], unit="s", utc=False)
    df = df[
        [
            "datetime",
            "user_note",
            "ai_character_emoji",
            "ai_reply_content",
            "should_ai_reply",
            "img_filepath",
            "ai_reply_timestamp",
            "user_timestamp",
        ]
    ]
    st.dataframe(
        df,
        height=heightIn,
        column_config={
            "ai_character_emoji": st.column_config.TextColumn("AI", width="small"),
            "should_ai_reply": st.column_config.CheckboxColumn("should_ai_reply", width="small"),
        },
    )


# 通过表内搜索结果定位日记片段
def show_and_locate_journal_snippet_by_df(df, num):
    # 入参：df，滑杆选择到表中的第几项
    if len(df) == 0:
        return
    web_component.render_paragraph(
        timestamp=df.iloc[num]["user_timestamp"],
        user_content=df.iloc[num]["user_note"],
        ai_content=df.iloc[num]["ai_reply_content"],
        ai_emoji=df.iloc[num]["ai_character_emoji"],
        dim=False,
        index="search_result",
    )


def keyword_search():
    def do_global_keyword_search():
        # 如果搜索所需入参状态改变了，进行搜索
        if (
            st.session_state.search_content_lazy == st.session_state.search_content
            and st.session_state.search_content_exclude_lazy == st.session_state.search_content_exclude
            and st.session_state.search_date_range_in_lazy == st.session_state.search_date_range_in
            and st.session_state.search_date_range_out_lazy == st.session_state.search_date_range_out
            or len(st.session_state.search_content) == 0
        ):
            return

        # 更新懒状态
        st.session_state.search_content_lazy = st.session_state.search_content
        st.session_state.search_content_exclude_lazy = st.session_state.search_content_exclude
        st.session_state.search_date_range_in_lazy = st.session_state.search_date_range_in
        st.session_state.search_date_range_out_lazy = st.session_state.search_date_range_out

        with st.spinner("Searching..."):
            # 进行搜索，取回结果
            st.session_state.db_global_search_result = db_manager.db_search_data_journal(
                keywords=st.session_state.search_content,
                start_timestamp=int(
                    datetime.datetime.combine(st.session_state.search_date_range_in, datetime.time(0, 0, 1)).timestamp()
                ),
                end_timestamp=int(
                    datetime.datetime.combine(st.session_state.search_date_range_out, datetime.time(23, 23, 59)).timestamp()
                ),
                exclude_words=st.session_state.search_content_exclude,
            )

    # 文本搜索 UI
    col_keyword, col_exclude, col_date_range = st.columns([2, 1, 2])
    with col_keyword:  # 输入搜索关键词
        st.session_state.search_content = st.text_input("Search Keyword", help="Separate multiple keywords with spaces.")
    with col_exclude:  # 排除关键词
        st.session_state.search_content_exclude = st.text_input(
            "Exclude", "", help="Leave blank for no exclusion. Multiple keywords can be separated by space."
        )
    with col_date_range:  # 选择时间范围
        ui_component_date_range_selector()

    do_global_keyword_search()


def similar_text_search():
    def do_global_keyword_search():
        # 如果搜索所需入参状态改变了，进行搜索
        if (
            st.session_state.search_content_lazy == st.session_state.search_content
            or len(st.session_state.search_content) == 0
        ):
            return

        # 更新懒状态
        st.session_state.search_content_lazy = st.session_state.search_content

        with st.spinner("Searching..."):
            # 进行搜索，取回结果
            st.session_state.db_global_search_result = embed_manager.query_text_in_vdb_journal(
                model=st.session_state.embedding_model, text=st.session_state.search_content
            )

    # 文本搜索 UI
    if "embedding_model" in st.session_state and config.enable_embedding:
        st.session_state.search_content = st.text_input("Search similar journal or describe how it feel/what it is")

        do_global_keyword_search()
    else:
        st.warning("Enable 'Enable local embedding' option in settings to embed and search journal.")


def image_semantic_search():
    st.warning("Under development, please stay tuned.")
    pass

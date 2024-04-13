import datetime

import streamlit as st

from afteryou import embed_manager, llm, utils
from afteryou.db_manager import db_manager

GLOBAL_HEADER = """
"""


def replace_newlines_with_paragraphs(text: str, id: str):
    """替换\n为<p>"""
    paragraphs = text.split("\n")
    paragraphs = ['<p id="{}">{}</p>'.format(id, p) for p in paragraphs if p]
    result = "".join(paragraphs)
    return result


def add_dim_area(dim: bool, add_class=True):
    if dim:
        if add_class:
            return "class='dim_area'"
        else:
            return "dim_area"


# "%Y-%m-%d_%H-%M-%S"
def render_title(date: datetime.date, level="h2", dim=False):
    date_str = "{}/{}".format(date.month, date.day) + " " + utils.get_weekday_str(date)
    res = f"""
<{level} {add_dim_area(dim)}>{date_str}</{level}>
"""
    st.markdown(res, unsafe_allow_html=True)


def render_timestamp(ts: int, dim=False):
    dt = utils.seconds_to_datetime(ts)
    dt_str = dt.strftime("%H:%M")
    res = f"""
<p align='left' style='color:rgba(255,255,255,.3)' {add_dim_area(dim)}>{dt_str}</p>
"""
    st.markdown(res, unsafe_allow_html=True)


def render_user_content(content: str, dim=False):
    content = replace_newlines_with_paragraphs(content, id="user-content")
    css = """
<style>
.container_user_content {
    padding-bottom:1.5em;
}
#user-content {
    font-size:20px;
}
</style>
"""

    res = (
        css
        + f"""
<div class="container_user_content container_global {add_dim_area(dim,add_class=False)}">{content}<div>
"""
    )
    st.markdown(res, unsafe_allow_html=True)


def render_ai_content(content: str, emoji="🔮", dim=False):
    content = replace_newlines_with_paragraphs(content, id="ai-content")
    css = """
<style>
.container_ai_content {
    display: flex;
    padding-bottom:1em;
}

.cac_left {
    text-align: center;
    padding-left:1em;
}

.cac_right {
    flex-grow: 1;
    color:#A687FF;
    font-style: italic;
    padding-left:1em;
    line-height: 175%;
}
#ai-content {
  margin-bottom: .25em;
}
</style>
"""
    res = (
        css
        + f"""
<div class="container_ai_content container_global {add_dim_area(dim,add_class=False)}">
  <div class="cac_left">{emoji}</div>
  <div class="cac_right">{content}</div>
</div>
"""
    )
    st.markdown(res, unsafe_allow_html=True)


def render_summary_content(content: str, dim=False):
    content = replace_newlines_with_paragraphs(content, id="")
    css = """
<style>
.container_summary_content {
    font-style: italic;
    line-height: 175%;
    font-size: 14px ;
    padding-bottom:1em;
    color: rgba(166,135,255,.8);
}
</style>
"""
    res = (
        css
        + f"""
<div class="container_summary_content container_global {add_dim_area(dim,add_class=False)}">
{content}
</div>
"""
    )
    st.markdown(res, unsafe_allow_html=True)


def render_paragraph(timestamp: int, user_content: str, ai_content: str, ai_emoji="🔮", dim=False, editable=False, index="0_0"):
    def _reimagine():
        if st.session_state.toggle_should_reply:
            ai_reply, ai_emoji = llm.request_ai_reply_instant(user_content)
            db_manager.update_row_by_timestamp(timestamp=timestamp, column_name="ai_character_emoji", update_content=ai_emoji)
            db_manager.update_row_by_timestamp(timestamp=timestamp, column_name="ai_reply_content", update_content=ai_reply)
            db_manager.update_row_by_timestamp(
                timestamp=timestamp, column_name="ai_reply_timestamp", update_content=int(datetime.datetime.now().timestamp())
            )

    def _update_user_note():
        db_manager.update_row_by_timestamp(
            timestamp=timestamp, column_name="user_note", update_content=st.session_state[f"edit_{index}"]
        )
        _reimagine()

    st.divider()
    col_edit1, col_edit2, col_edit3, col_edit4 = st.columns([4, 0.3, 0.3, 0.3])
    with col_edit1:
        render_timestamp(timestamp, dim=dim)
    if not dim or editable:
        with col_edit2:
            edit_mode = st.button("✍🏻", help="Edit", key=f"btn_edit_{index}", use_container_width=True)
        with col_edit3:
            re_imagine = st.button("🔮", help="Re-imagine", key=f"btn_reimagine_{index}", use_container_width=True)
        with col_edit4:
            if st.button("🗑️", help="Delete", key=f"btn_delete_{index}", use_container_width=True):
                embed_manager.delete_vdb_journal_record_by_timestamp(timestamp=timestamp)
                db_manager.delete_journal_row_by_timestamp(timestamp=timestamp)
                st.rerun()
    else:
        re_imagine = False
        edit_mode = False

    if re_imagine:
        _reimagine()
        st.rerun()

    if edit_mode:
        st.session_state[f"update_note_{index}"] = st.text_area(
            "edit", value=user_content, key=f"edit_{index}", on_change=_update_user_note
        )
    else:
        render_user_content(user_content, dim=dim)
        if ai_content:
            render_ai_content(ai_content, emoji=ai_emoji, dim=dim)


def render_summary(day: datetime.date, summary_content: str, dim=False, editable=False, index="0_0", no_render=False):
    def _reimagine():
        db_manager.delete_summary_row_by_date(input_date=day)
        llm.request_ai_summary(day=day)

    if day > datetime.date.today() or no_render:
        return

    col_edit1, col_edit2 = st.columns([4.6, 0.3])
    with col_edit1:
        st.markdown(
            f"<p align='left' style='color:rgba(255,255,255,.3);padding-top:.5em' {add_dim_area(dim)}>Summary</p>",
            unsafe_allow_html=True,
        )
    if not dim or editable:
        with col_edit2:
            re_imagine = st.button("🔮", help="Re-imagine", key=f"btn_reimagine_summary_{index}", use_container_width=True)
    else:
        re_imagine = False

    if re_imagine:
        _reimagine()
        st.rerun()

    if summary_content:
        render_summary_content(summary_content, dim=dim)
    else:
        render_summary_content("click Re-imagine to summarize. ↗", dim=dim)


def render_count_static(days_num, chars_num):
    """绘制统计数据"""
    css = """
    <style>
        body{
            background-color: #19191A;
        }
        #static-container{
            display: inline-flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 60px;
        }
        #static-title{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            color: rgba(255, 255, 255, 0.30);
            font-family: "Space Mono" !important;
            font-size: 12px;
            font-style: normal;
            font-weight: 400;
            line-height: normal;
            text-transform: uppercase;
            margin: 0;
        }
        .static-content-container p{
            display: inline-block;
            text-align: left;
            margin: 0;
        }
        #static-days-num{
            background: conic-gradient(from -85deg at 15.41% 113.79%, rgba(214, 78, 35, 0.85) 2.3368923738598824deg, rgba(255, 136, 70, 0.80) 100.06757497787476deg, rgba(133, 0, 214, 0.71) 205.94711065292358deg);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            leading-trim: both;
            text-edge: cap;
            font-family: "Space Mono" !important;
            font-size: 48px;
            font-style: medium;
            font-weight: 700;
            line-height: normal;
        }
        #static-days-copy{
            leading-trim: both;
            text-edge: cap;
            font-family: "Space Mono" !important;
            font-size: 20px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
            background: linear-gradient(90deg, rgba(172, 87, 163, 0.80) 8.33%, #8062C7 94.44%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        #static-chars-stat{
            color: #8062C7;
            leading-trim: both;
            text-edge: cap;
            font-family: "Space Mono" !important;
            font-size: 14px;
            font-style: normal;
            font-weight: 400;
            line-height: normal;
            margin-left: 0.5em;
        }
    </style>
"""
    res = (
        css
        + f"""
    <div id="static-container">
        <p id="static-title">Record your heart for</p>
        <div class="static-content-container">
            <p id="static-days-num">
                {days_num}
            </p>
            <p id="static-days-copy">
                days
            </p>
            <p id="static-chars-stat">
                /{chars_num} chars
            </p>
        </div>
    </div>
"""
    )
    st.markdown(res, unsafe_allow_html=True)


"""template
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>

    </style>
</head>
<body>


</body>
</html>
"""

import datetime

import streamlit as st

from afteryou import utils

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
    date_str = date.strftime("%m/%d")
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
    content = replace_newlines_with_paragraphs(content, id="ai-content")
    css = """
<style>
.container_user_content {
    padding-bottom:1.5em;
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


def render_paragraph(timestamp: int, user_content: str, ai_content: str, ai_emoji="🔮", dim=False):
    render_timestamp(timestamp, dim=dim)
    render_user_content(user_content, dim=dim)
    render_ai_content(ai_content, dim=dim)
    st.divider()

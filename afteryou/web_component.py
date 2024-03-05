from afteryou import utils


def replace_newlines_with_paragraphs(text: str, id: str):
    # 分割文本为列表，元素为以 \n 分割的子串
    paragraphs = text.split("\n")
    # 使用 <p> 标签包裹每个子串，并加入新的列表
    paragraphs = ['<p id="{}">{}</p>'.format(id, p) for p in paragraphs if p]
    # 将列表合并为一个字符串
    result = "".join(paragraphs)

    return result


def timestamp(ts: int):
    dt = utils.seconds_to_datetime(ts)
    dt_str = dt.strftime("%H:%M")
    res = f"""
<p align='left' style='color:rgba(255,255,255,.3)'>{dt_str}</p>
"""
    return res


def ai_content(content: str):
    content = replace_newlines_with_paragraphs(content, id="ai-content")
    css = """
<style>
.container {
    display: flex;
}

.left {
    text-align: center;
    padding-left:1em;
}

.right {
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
<div class="container">
  <div class="left">🔮</div>
  <div class="right">{content}</div>
</div>
"""
    )
    return res

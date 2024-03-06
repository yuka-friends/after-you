import datetime

import streamlit as st

from afteryou import web_component


def render():
    date_selector()
    add_thought()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.empty()
        web_component.render_title(datetime.datetime(2024, 3, 6, 1, 2, 3), dim=True)
        web_component.render_paragraph(
            timestamp=1709654002,
            user_content="也许朋友本身并没有渐行渐远，真正把我们隔绝的，是孤独和虚无为我们织出的一张网。\n它是我们想要剥离过去的结界，是我们虚张声势的外壳，而它挡住的却恰恰是我们成长途中对过去那些人和事，应有的认可与坦诚。多少一路走来的伙伴就这样从我们的人生中消失了。",
            ai_content="这是对友谊的本质和时间的流逝的非常深思熟虑的反思。 这似乎表明，虽然朋友之间可能会疏远，但分隔我们的真正障碍是我们为自己创造的孤独和空虚。\n 这种自我强加的孤立使我们无法承认和诚实地对待那些塑造了我们的人和经历，并最终导致失去陪伴。 这深刻地提醒我们珍惜我们的人际关系并接受生活教给我们的教训的重要性。 您是否有任何特殊的经历或友谊激发了这些想法？",
            ai_emoji="🥞",
            dim=True,
        )
    with col2:
        st.empty()

        web_component.render_title(datetime.datetime(2024, 3, 7, 1, 2, 3))
        web_component.render_paragraph(
            timestamp=1709654002,
            user_content="也许朋友本身并没有渐行渐远，真正把我们隔绝的，是孤独和虚无为我们织出的一张网。\n它是我们想要剥离过去的结界，是我们虚张声势的外壳，而它挡住的却恰恰是我们成长途中对过去那些人和事，应有的认可与坦诚。多少一路走来的伙伴就这样从我们的人生中消失了。",
            ai_content="这是对友谊的本质和时间的流逝的非常深思熟虑的反思。 这似乎表明，虽然朋友之间可能会疏远，但分隔我们的真正障碍是我们为自己创造的孤独和空虚。\n 这种自我强加的孤立使我们无法承认和诚实地对待那些塑造了我们的人和经历，并最终导致失去陪伴。 这深刻地提醒我们珍惜我们的人际关系并接受生活教给我们的教训的重要性。 您是否有任何特殊的经历或友谊激发了这些想法？",
            ai_emoji="🥞",
        )

    with col3:
        web_component.render_title(datetime.datetime(2024, 3, 8, 1, 2, 3))


def date_selector():
    col_day_0, col_day_1, col_day_2, col_day_3, col_day_4, col_day_5 = st.columns([1, 0.25, 0.25, 0.25, 0.25, 1])
    with col_day_0:
        st.empty()
    with col_day_1:
        st.button("←", use_container_width=True)
    with col_day_2:
        st.button("→", use_container_width=True)
    with col_day_3:
        st.button("today", use_container_width=True)
    with col_day_4:
        st.date_input("date", label_visibility="collapsed")
    with col_day_5:
        st.empty()


def add_thought():
    col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
    with col_t1:
        st.empty()
    with col_t2:
        st.text_area("add though")
        col_submit1, col_submit2, col_submit3 = st.columns([1, 3, 1])
        with col_submit1:
            # st.file_uploader("submit")
            st.empty()
        with col_submit2:
            st.empty()
        with col_submit3:
            st.button("submit", use_container_width=True)

        st.empty()
    with col_t3:
        st.empty()

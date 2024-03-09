import pandas as pd
import streamlit as st

from afteryou.db_manager import db_manager


def render():
    # 初始化
    if "mail_df" not in st.session_state:
        df = db_manager.read_sqlite_table_to_dataframe("afteryou_mail")
        df.drop("mail_type", axis=1, inplace=True)
        df["mail_timestamp"] = pd.to_datetime(df["mail_timestamp"], unit="s", utc=False)
        st.session_state["mail_df"] = df.sort_index(ascending=False).reset_index(drop=True)

    st.markdown("### 📮 Mailbox")
    col1, col2 = st.columns([1, 2])
    with col1:
        if len(st.session_state.mail_df) - 1 > 0:
            mail_select = st.slider("select mail", value=0, min_value=0, max_value=len(st.session_state.mail_df) - 1)
        else:
            mail_select = 0
        st.dataframe(
            st.session_state.mail_df,
            use_container_width=False,
            column_config={
                "mail_from_name": st.column_config.TextColumn(
                    "from",
                    width="small",
                ),
                "mail_timestamp": st.column_config.DatetimeColumn("datetime", width="small"),
                "mail_content": st.column_config.TextColumn("content", width="large"),
            },
        )
        st.empty()
    with col2:
        render_letter(
            from_name=st.session_state.mail_df.loc[mail_select, "mail_from_name"],
            from_time=st.session_state.mail_df.loc[mail_select, "mail_timestamp"],
            content=st.session_state.mail_df.loc[mail_select, "mail_content"],
        )
        st.empty()


def render_letter(from_name, from_time, content):
    css = """
<style>
.container_mail_paper {
    padding: 32px;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 10px;
    border-radius: 16px;
    border: 2px solid rgba(190, 125, 255, 0.40);

    color: rgba(255,255,255,.9);
    font-size: 20px;
    width: 700px;
    min-height: 900px;
    text-align: left;

#mail_meta_container {
    display: flex;
    width: 100%;
    color: rgba(255,255,255,.4);
}

#mail_meta_l {
    text-align: left;
    width: 100%;
}

#mail_meta_r {
    text-align: right;
    width: 100%;
}
</style>
"""
    res = (
        css
        + f"""
<div class="container_mail_paper">
<div id="mail_meta_container">
<p id="mail_meta_l">from {from_name}</p>
<p id="mail_meta_r">{str(from_time)[:10]}</p>
</div>
<p>{content}</p>
</div>
"""
    )
    st.markdown(res, unsafe_allow_html=True)

import pandas as pd
import streamlit as st

from afteryou.db_manager import db_manager


def render():
    # 初始化
    if "mail_df" not in st.session_state:
        st.session_state["mail_df"] = get_mail_df()

    st.markdown("### 📮 Mailbox")
    col1, col_n, col2 = st.columns([1, 0.3, 2])
    with col1:
        if len(st.session_state.mail_df) - 1 > 0:
            mail_select = st.slider("slide to select mail", value=0, min_value=0, max_value=len(st.session_state.mail_df) - 1)
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
                "mail_datetime": st.column_config.DatetimeColumn("datetime", width="small"),
                "mail_content": st.column_config.TextColumn("content", width="large"),
                "mail_timestamp": st.column_config.NumberColumn("timestamp", width="small"),
            },
        )
        st.empty()
    with col_n:
        st.empty()
    with col2:
        if len(st.session_state.mail_df) != 0:
            render_letter(
                from_name=st.session_state.mail_df.loc[mail_select, "mail_from_name"],
                from_time=st.session_state.mail_df.loc[mail_select, "mail_datetime"],
                content=st.session_state.mail_df.loc[mail_select, "mail_content"],
                timestamp=st.session_state.mail_df.loc[mail_select, "mail_timestamp"],
            )
        st.empty()


def get_mail_df():
    df = db_manager.read_sqlite_table_to_dataframe("afteryou_mail")
    df["mail_datetime"] = pd.to_datetime(df["mail_timestamp"], unit="s", utc=False)
    df = df.sort_index(ascending=False).reset_index(drop=True)
    df = df[
        [
            "mail_datetime",
            "mail_from_name",
            "mail_content",
            "mail_timestamp",
        ]
    ]
    return df


def render_letter(from_name, from_time, content, timestamp):
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
    margin-bottom: 1.5em;

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

    def _delete_letter():
        db_manager.delete_mail_row_by_timestamp(timestamp=int(timestamp))
        st.session_state["mail_df"] = get_mail_df()
        st.toast("🗑️ letter deleted")

    st.button("🗑️", help="delete letter", key="btn_delete_letter", on_click=_delete_letter)

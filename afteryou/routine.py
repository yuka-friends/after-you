# import datetime

# import streamlit as st

# from afteryou import llm
# from afteryou.db_manager import db_manager


# def run_before():
#     # 距离上一个周日过去四天内，生成上周一~六的来信

#     # 是否有内容可以生成，是否已经生成过了
#     # 生成邮件：是否为周日 + 是否已经经历过了
#     # 是否为特殊节日
#     pass


# def run_after():
#     # 检查更新
#     pass


# def generate_mail():
#     if not datetime.date.today() - recent_last_sunday() < datetime.timedelta(days=4):
#         return
#     # datetime_start=recent_last_sunday()-datetime.timedelta(days=6)
#     # datetime_end=recent_last_sunday()
#     # llm.request_ai_reply_mail(text=,datetime_start=,datetime_end=)
#     pass


# def recent_last_sunday():
#     today = datetime.date.today()
#     day_diff = today.weekday() + 1  # 因为Python中索引是从0开始的，周一为0，周日为6
#     if day_diff == 1:  # 如果是周一，最近的周日是前一天
#         return today - datetime.timedelta(days=1)
#     else:
#         return today - datetime.timedelta(days=day_diff)

import calendar
import datetime

import pandas as pd
import streamlit as st
from dateutil.easter import easter
from lunardate import LunarDate

from afteryou import llm, utils
from afteryou.db_manager import db_manager
from afteryou.logger import get_logger

logger = get_logger(__name__)


def run_before():
    # 总结前几天的内容
    with st.spinner("🔮 Retrieving the summary of previous days..."):
        generate_summary()

    # 接收信件
    with st.spinner("📬 Retrieving the mail..."):
        get_mail()


def run_after():
    # 检查更新
    if "is_new_version" not in st.session_state:
        with st.spinner("✨ checking update..."):
            st.session_state.is_new_version = utils.get_new_version_if_available()


def generate_summary(day_trackback=3):
    """生成过去数天的总结"""
    for i in range(1, day_trackback):
        data = datetime.date.today() - datetime.timedelta(days=i)
        row = db_manager.db_get_summary_line_by_date(input_date=data)  # 在总结表中获取日的总结
        if row is None:
            continue
        if len(row) > 0:
            continue
        else:  # 如果没有总结，就生成总结
            df_day = db_manager.db_get_jounal_df_by_day(input_date=data)
            if df_day is None:
                continue
            if len(df_day) > 0:  # 如果当日有记录，进行总结
                llm.request_ai_summary(day=data)


def get_mail():
    """生成邮件"""

    df = db_manager.read_sqlite_table_to_dataframe("afteryou_mail")
    df["mail_datetime"] = pd.to_datetime(df["mail_timestamp"], unit="s", utc=False)

    # 检查上/本周日是否有数据：上/本周日距今小于5天，逾时跳过
    if datetime.date.today() - utils.recent_last_sunday() < datetime.timedelta(days=5):
        date_to_check = pd.to_datetime(utils.recent_last_sunday()).date()
        if not any(df["mail_datetime"].dt.date.isin([date_to_check])):  # 是否已有信件
            llm.request_mail_by_day_range(date_start=date_to_check - datetime.timedelta(days=6), date_end=date_to_check)
            st.toast("📮📨 You got new letter!")

    # 检查今/前三天是否为特别节日
    for i in range(3):
        date = datetime.date.today() - datetime.timedelta(days=i)
        festival_res = get_special_day(date)
        if festival_res:
            date_to_check = pd.to_datetime(festival_res[0][0]).date()
            logger.debug(date_to_check)
            if not any(df["mail_datetime"].dt.date.isin([date_to_check])):  # 是否已有信件
                llm.request_mail_by_festival(special_date=festival_res)
                st.toast("📮📨 You got new letter!")


def get_special_day(date: datetime.date):
    def get_thanksgiving(year):
        month = 11  # 感恩节在11月
        # 获取该月第一天是周几和该月的总天数
        _, num_days_month = calendar.monthrange(year, month)
        # 遍历这个月的每一天
        for day in range(1, num_days_month + 1):
            candidate_date = datetime.date(year, month, day)
            # 检查这一天是否是星期四以及这一天是这个月的第四个星期四
            if candidate_date.weekday() == calendar.THURSDAY and 22 <= day <= 28:
                return candidate_date

    year = date.year
    special_date = [
        (datetime.date(year, 1, 1), "New year's day"),
        (datetime.date(year, 2, 14), "Valentine's Day"),
        (datetime.date(year, 3, 8), "women's day"),
        (datetime.date(year, 3, 17), "St. Patrick's Day"),
        (datetime.date(year, 5, 1), "labor day"),
        (datetime.date(year, 6, 18), "half of the year"),
        (datetime.date(year, 10, 31), "halloween"),
        (datetime.date(year, 12, 25), "Christmas"),
        (datetime.date(year, 12, 31), "Lunar New Year's eve"),
        (easter(year), "Easter Sunday"),
        (get_thanksgiving(year), "Thanksgiving"),
        (datetime.date(year, 1, 6), "西班牙三王日（Three Kings Day, Spanish-speaking Countries）"),
        (datetime.date(year, 2, 5), "预备阿阿火节（Up Helly Aa Fire Festival, Scotland）"),
        (datetime.date(year, 2, 13), "威尼斯狂欢节（Carnival of Venice, Italy）"),
        (datetime.date(year, 3, 2), "冰岛圣诞老人节（Icelandic Yule Lads, Iceland）"),
        (datetime.date(year, 3, 17), "圣帕特里克节（St. Patrick's Day）"),
        (datetime.date(year, 3, 18), "印度洋里节（Holi, India and Nepal）"),
        (datetime.date(year, 5, 7), "围巾熊节（Straw Bear Day, England）"),
        (datetime.date(year, 6, 25), "美国国内鲶鱼日（National Catfish Day, U.S.A.）"),
        (datetime.date(year, 7, 27), "芬兰国民瞌睡日（National Sleepyhead Day, Finland）"),
        (datetime.date(year, 10, 24), "韩国字母日（Hangeul Day, Korea）"),
        (datetime.date(year, 11, 1), "墨西哥亡灵节（Day Of The Dead, Mexico）"),
        (datetime.date(year, 11, 11), "中国光棍节（Singles' Day, China）"),
        (datetime.date(year, 12, 22), "印度排灯节（Diwali Light Festival, India）"),
        (LunarDate(year, 1, 1).toSolarDate, "春节"),
        (LunarDate(year, 1, 15).toSolarDate, "元宵节"),
        (LunarDate(year, 2, 2).toSolarDate, "龙抬头/社日节"),
        (LunarDate(year, 3, 3).toSolarDate, "上巳节"),
        (LunarDate(year, 4, 4).toSolarDate, "寒食节"),
        (LunarDate(year, 4, 5).toSolarDate, "清明节"),
        (LunarDate(year, 5, 5).toSolarDate, "端午节"),
        (LunarDate(year, 7, 7).toSolarDate, "七夕节"),
        (LunarDate(year, 7, 15).toSolarDate, "中元节"),
        (LunarDate(year, 8, 15).toSolarDate, "中秋节"),
        (LunarDate(year, 9, 9).toSolarDate, "重阳节"),
        (LunarDate(year, 10, 1).toSolarDate, "寒衣节"),
        (LunarDate(year, 10, 15).toSolarDate, "下元节"),
        (LunarDate(year, 12, 8).toSolarDate, "腊八节"),
        (LunarDate(year, 12, 23).toSolarDate, "小年（北方）"),
        (LunarDate(year, 12, 24).toSolarDate, "小年（南方）"),
        (LunarDate(year, 2, 4).toSolarDate, "立春"),
        (LunarDate(year, 2, 19).toSolarDate, "雨水"),
        (LunarDate(year, 3, 5).toSolarDate, "惊蛰"),
        (LunarDate(year, 3, 20).toSolarDate, "春分"),
        (LunarDate(year, 4, 4).toSolarDate, "清明"),
        (LunarDate(year, 4, 20).toSolarDate, "谷雨"),
        (LunarDate(year, 5, 5).toSolarDate, "立夏"),
        (LunarDate(year, 5, 21).toSolarDate, "小满"),
        (LunarDate(year, 6, 5).toSolarDate, "芒种"),
        (LunarDate(year, 6, 21).toSolarDate, "夏至"),
        (LunarDate(year, 7, 7).toSolarDate, "小暑"),
        (LunarDate(year, 7, 22).toSolarDate, "大暑"),
        (LunarDate(year, 8, 7).toSolarDate, "立秋"),
        (LunarDate(year, 8, 23).toSolarDate, "处暑"),
        (LunarDate(year, 9, 7).toSolarDate, "白露"),
        (LunarDate(year, 9, 23).toSolarDate, "秋分"),
        (LunarDate(year, 10, 8).toSolarDate, "寒露"),
        (LunarDate(year, 10, 23).toSolarDate, "霜降"),
        (LunarDate(year, 11, 7).toSolarDate, "立冬"),
        (LunarDate(year, 11, 22).toSolarDate, "小雪"),
        (LunarDate(year, 12, 7).toSolarDate, "大雪"),
        (LunarDate(year, 12, 21).toSolarDate, "冬至"),
    ]

    result = [tup for tup in special_date if tup[0] == date]
    return result

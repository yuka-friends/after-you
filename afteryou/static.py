import calendar
import datetime

import pandas as pd

from afteryou import file_utils, utils
from afteryou.db_manager import db_manager


def update_journal_static():
    db_df = db_manager.db_fetch_table_all_data(db_manager.tablename_journal)
    db_df = db_df.sort_values("user_timestamp")
    db_df["user_datetime"] = pd.to_datetime(db_df["user_timestamp"], unit="s", utc=False)

    # 统计天数
    last_dt = datetime.datetime(2000, 1, 1, 1, 1, 1, 1)
    day_cnt = 0

    # 统计字数
    chars_cnt = 0

    for index, row in db_df.iterrows():
        current_dt = utils.str_to_datetime(str(row["user_datetime"]))
        current_dt = current_dt.replace(hour=1, minute=1, second=1, microsecond=1)
        if current_dt != last_dt:
            day_cnt += 1
            last_dt = current_dt
        chars_cnt += len(row["user_note"])

    # 写入缓存
    file_utils.get_cache_dict(
        key_operate="all_day_cnt",
        value_operate=day_cnt,
        operation="write",
    )
    file_utils.get_cache_dict(
        key_operate="all_chars_cnt",
        value_operate=chars_cnt,
        operation="write",
    )

    # 统计散点图

    return day_cnt, chars_cnt


def get_month_chars_overview_scatter(dt: datetime.datetime):
    # 统计散点图，入参仅年月有效
    weekday, month_days = calendar.monthrange(dt.year, dt.month)
    df_month_data = pd.DataFrame(columns=["weekday", "chars"])

    for day in range(1, month_days + 1):
        db_df = db_manager.db_get_jounal_df_by_day(datetime.date(dt.year, dt.month, day))
        chars_cnt = 0
        if len(db_df) > 0:
            for index, row in db_df.iterrows():
                chars_cnt += len(row["user_note"])

        df_month_data.loc[len(df_month_data.index)] = [day, chars_cnt]

    return df_month_data

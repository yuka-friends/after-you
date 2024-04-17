import calendar
import datetime
import time

import pandas as pd
from langdetect import detect

from afteryou import file_utils, utils
from afteryou.db_manager import db_manager
from afteryou.logger import get_logger

logger = get_logger(__name__)


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
    df_month_data = pd.DataFrame(columns=["emotion_baseline", "chars", "emotion"])
    df_month_data.loc[len(df_month_data.index)] = [0, 0, 0]  # skip index 0
    emotion_date_dict = file_utils.get_cache_dict(key_operate="emotion_date_dict", operation="read")
    if emotion_date_dict is None:
        emotion_date_dict = {}

    max_chars = 0
    for day in range(1, month_days + 1):
        # get chars data
        db_df = db_manager.db_get_jounal_df_by_day(datetime.date(dt.year, dt.month, day))
        chars_cnt = 0
        if len(db_df) > 0:
            for index, row in db_df.iterrows():
                chars_cnt += len(row["user_note"])

        if chars_cnt > max_chars:
            max_chars = chars_cnt
        df_month_data.at[day, "chars"] = chars_cnt

    for day in range(1, month_days + 1):
        # get mood data
        if datetime.date(dt.year, dt.month, day) == datetime.date.today():  # skip today
            continue
        db_df = db_manager.db_get_jounal_df_by_day(datetime.date(dt.year, dt.month, day))
        if len(db_df) > 0:
            try:
                emotion_prob = emotion_date_dict[utils.date_to_str(datetime.date(dt.year, dt.month, day))]
                emotion_prob = (emotion_prob - 0.1) * 1.1  # calibrate
                emotion_prob_display = utils.map_range(emotion_prob, (-1, 1), (0, max_chars))
                df_month_data.at[day, "emotion"] = emotion_prob_display
            except KeyError:
                user_journal_text = ""
                for index, row in db_df.iterrows():
                    user_journal_text += row["user_note"]
                user_journal_text = translation_text_to_en(user_journal_text)
                if user_journal_text:
                    emotion_prob = utils.get_en_text_emotion(user_journal_text)
                    emotion_date_dict[utils.date_to_str(datetime.date(dt.year, dt.month, day))] = emotion_prob

                    emotion_prob_display = utils.map_range(emotion_prob, (-1, 1), (0, max_chars))
                    df_month_data.at[day, "emotion"] = emotion_prob_display
            df_month_data.at[day, "emotion_baseline"] = utils.map_range(0, (-1, 1), (0, max_chars))

    # saved mood data
    file_utils.get_cache_dict(
        key_operate="emotion_date_dict",
        value_operate=emotion_date_dict,
        operation="write",
    )

    df_month_data.drop(0, inplace=True)

    return df_month_data


def translation_text_to_en(text):
    try:
        language = detect(text)
        text_result = utils.google_translate(text, lang_from=language, lang_to="en")
        logger.debug(f"translate from: {text}")
        logger.debug(f"translate to: {text_result}")
        time.sleep(0.2)
        return text_result
    except Exception as e:
        logger.error(e)
        return None

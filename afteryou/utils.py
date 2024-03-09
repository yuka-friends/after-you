import datetime

import requests

from afteryou import __version__


# 将时间戳秒数转为datetime格式
def seconds_to_datetime(seconds):
    return datetime.datetime.fromtimestamp(seconds)


def get_weekday_str(input_date):
    """获取日期是星期几"""
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_index = input_date.weekday()  # 返回的是0-6，代表星期一到星期日
    return weekdays[weekday_index]


def recent_last_sunday():
    """获取最近的上一个周日的日期"""
    today = datetime.date.today()
    day_diff = today.weekday() + 1  # 因为Python中索引是从0开始的，周一为0，周日为6
    if day_diff == 1:  # 如果是周一，最近的周日是前一天
        return today - datetime.timedelta(days=1)
    else:
        return today - datetime.timedelta(days=day_diff)


def get_github_version(
    url="https://raw.githubusercontent.com/yuka-friends/after-you/main/afteryou/__init__.py",
):
    response = requests.get(url)
    global_vars = {}
    exec(response.text, global_vars)
    version = global_vars["__version__"]
    return version


# 获得当前版本号
def get_current_version():
    local_version = __version__
    return local_version


def get_new_version_if_available():
    remote_version = get_github_version()
    current_version = get_current_version()
    remote_list = remote_version.split(".")
    current_list = current_version.split(".")
    for i, j in zip(remote_list, current_list):
        try:
            if int(i) > int(j):
                return remote_version
        except ValueError:
            if i.split("b") > j.split("b"):
                return remote_version
    return None

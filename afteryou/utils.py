import datetime


# 将时间戳秒数转为datetime格式
def seconds_to_datetime(seconds):
    return datetime.datetime.fromtimestamp(seconds)

import base64
import datetime
import random

import cv2
import pandas as pd
import psutil
import requests
from textblob import TextBlob

from afteryou import __version__
from afteryou.logger import get_logger

logger = get_logger(__name__)


# 将时间戳秒数转为datetime格式
def seconds_to_datetime(seconds):
    return datetime.datetime.fromtimestamp(seconds)


def get_weekday_str(input_date):
    """获取日期是星期几"""
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_index = input_date.weekday()  # 返回的是0-6，代表星期一到星期日
    return weekdays[weekday_index]


def recent_last_sunday():
    """获取最近的上一个周日的日期，如果今天是周日则是最近的周日"""
    today = datetime.date.today()
    day_diff = today.weekday() + 1  # 因为Python中索引是从0开始的，周一为0，周日为6
    if day_diff == 1:  # 如果是周一，最近的周日是前一天
        return today - datetime.timedelta(days=1)
    elif day_diff == 7:  # 如果是周日，最近的周日是今天
        return today
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


def is_process_running(pid, compare_process_name):
    """根据进程 PID 与名字比对检测进程是否存在"""
    pid = int(pid)
    try:
        # 确保 PID 与进程名一致
        process = psutil.Process(pid)
        return process.is_running() and process.name() == compare_process_name
    except psutil.NoSuchProcess:
        return False


def greeting_based_on_time():
    current_hour = datetime.datetime.now().hour

    copywrite = [
        [
            "Good morning",
            "Morning's light, whispering delight",
            "A new day has dawned, painting the world in shades of hope",
            "Morning sun seeps softly, greeting the world anew",
        ],
        [
            "Good afternoon",
            "Sun at its zenith, embracing the day",
            "Afternoon's delight, sun shines so bright",
            "As the day unfolds, new stories are told",
        ],
        [
            "Good evening",
            "Evening falls, as day's curtain calls",
            "Night's gentle eve, in its tender weave",
            "When the sun takes a bow, the evening's now",
        ],
        [
            "Good night",
            "Night's sweet lullaby, beneath a starry sky",
            "In the hush of the night, may dreams take flight",
            "Rest your eyes, under night's wise skies",
        ],
    ]

    if 5 <= current_hour < 12:  # 5:00 - 11:59 is morning
        return random.choice(copywrite[0])
    elif 12 <= current_hour < 17:  # 12:00 - 16:59 is afternoon
        return random.choice(copywrite[1])
    elif 17 <= current_hour < 22:  # 17:00 - 21:59 is evening
        return random.choice(copywrite[2])
    else:  # 22:00 - 4:59 is night
        return random.choice(copywrite[3])


def datetime_to_str(datetime_input: datetime.datetime):
    """将datetime转为str，以便存读"""
    return datetime_input.strftime("%Y-%m-%d %H:%M:%S")


def str_to_datetime(datetime_str: str):
    """将str转为datetime，以便存读"""
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


def date_to_str(date_input: datetime.date):
    """将date转为str，以便存读"""
    return date_input.strftime("%Y-%m-%d")


def str_to_date(date_str: str):
    """将str转为date，以便存读"""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


# 图片路径转base64
def image_to_base64(image_path):
    # 使用cv2加载图像，包括透明通道
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # 将图像转换为PNG格式
    _, encoded_image = cv2.imencode(".png", image)  # 返回一个元组 (retval, buffer)。retval 表示编码的结果，buffer 是包含图像数据的字节对象。

    # 将图像数据编码为base64字符串
    base64_image = base64.b64encode(encoded_image.tobytes()).decode("utf-8")

    return base64_image


def get_list_first_one_match_in_string(text, lst):
    for word in lst:
        if word in text:
            return word
    return None


def find_char_after_at(string):
    """找到'@'的位置"""
    at_index = string.find("@")
    # 假如在字符串中确实找到了'@'
    if at_index != -1:
        # 确保'@'后面还有其他字符
        if at_index < len(string) - 1:
            # 返回'@'后面的第一个字符
            return string[at_index + 1]
        else:
            return None  # '@'是最后一个字符，后面没有其他字符
    else:
        return None  # 字符串中没有'@'


def find_first_match_row_in_df(df: pd.DataFrame, row_name: str, column_value):
    # 使用 .loc 通过条件查找行
    A_rows = df.loc[df[row_name] == column_value]
    # 判断是否有满足条件的行
    if not A_rows.empty:
        # 返回第一个满足条件的行
        return A_rows.iloc[0]
    else:
        return None


def google_translate(text, lang_from="ja", lang_to="en"):
    url = "https://translate.googleapis.com/translate_a/single"
    # dt参数的作用，这里说明一下，dt决定了最终返回的数据，可以包含多个dt参数，以下是dt的一些值：
    # t - 源text的翻译
    # at - 会额外返回一些近义词
    # ex - examples
    # ss - 如果翻译的是单个词，会返回与该词相关的动词、形容词、名词
    # md - 如果翻译的是单个词，返回该词的定义
    # rw - 组词
    # bd
    # rm
    # dt - 似乎是设定返回数据的格式
    params = {"client": "gtx", "dt": "t", "sl": lang_from, "tl": lang_to, "q": text}

    headers = {
        "authority": "translate.googleapis.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "none",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "x-client-data": "CJC2yQEIpLbJAQipncoBCJXmygEIlqHLAQiFoM0B",
    }
    response = requests.get(url, headers=headers, params=params)
    results = response.json()[0]

    # 返回的结果并不是整句，所以需要拼起来
    TRANSLATION_INDEX = 0
    translation = ""
    for result in results:
        translation += result[TRANSLATION_INDEX]
    # print(f"{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return translation


def get_en_text_emotion(text: str):
    text.replace("\n", "")
    blob = TextBlob(text)
    prob = blob.sentiment.polarity
    logger.debug(f"{prob=}")
    return blob.sentiment.polarity


def map_range(value, src_range, dest_range):
    """
    Map a value from source range to destination range.

    Args:
      value (float): the value to map.
      src_range (tuple): a tuple of two values defining the source range.
      dest_range (tuple): a tuple of two values defining the destination range.

    Returns:
      The mapped value.
    """
    src_min, src_max = src_range
    dest_min, dest_max = dest_range
    src_span = src_max - src_min
    dest_span = dest_max - dest_min
    scaled_value = (value - src_min) / src_span
    return dest_min + (scaled_value * dest_span)

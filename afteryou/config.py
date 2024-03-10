import json
import os
import shutil

from afteryou.logger import get_logger

CONFIG_NAME_USER = "config_user.json"
CONFIG_NAME_DEFAULT = "config_default.json"
DIR_CONFIG_SRC = "afteryou\\src"

CONFIG_FILEPATH_DEFAULT = os.path.join(DIR_CONFIG_SRC, CONFIG_NAME_DEFAULT)
CONFIG_FILEPATH_USER = CONFIG_NAME_USER

logger = get_logger(__name__)


class Config:
    def __init__(
        self,
        reply_language,
        openai_api_key,
        openai_url,
        model_name,
        weather_location,
        username,
        system_prompt_prefix,
        system_prompt_suffix,
        system_prompt_mail_prefix,
        system_prompt_mail_suffix,
        userdata_filepath,
        embed_search_recall_result_per_db,
        system_prompt_summary,
        max_token_summary_input,
        system_prompt_mail_special_day_prefix,
        enable_embedding,
        **other_field,
    ) -> None:
        # If need to process input parameters, they should assign another variable name to prevent recursive writing into the config.
        self.reply_language = reply_language
        self.userdata_filepath = userdata_filepath
        self.openai_api_key = openai_api_key
        self.openai_url = openai_url
        self.model_name = model_name
        self.weather_location = weather_location
        self.username = username
        self.system_prompt_prefix = system_prompt_prefix
        self.system_prompt_suffix = system_prompt_suffix
        self.system_prompt_mail_prefix = system_prompt_mail_prefix
        self.system_prompt_mail_suffix = system_prompt_mail_suffix
        self.embed_search_recall_result_per_db = embed_search_recall_result_per_db
        self.system_prompt_summary = system_prompt_summary
        self.max_token_summary_input = max_token_summary_input
        self.system_prompt_mail_special_day_prefix = system_prompt_mail_special_day_prefix
        self.enable_embedding = enable_embedding

    def set_and_save_config(self, attr: str, value):
        if not hasattr(self, attr):
            logger.info("{} not exist in config!".format(attr))
            return
        setattr(self, attr, value)
        self.save_config()

    def save_config(self):
        # 读取 config.json 获取旧设置
        config_json = get_config_json()
        # 把 python 对象转为 dict
        now_config_json = vars(self)
        # 更新设置
        config_json.update(now_config_json)
        # 去除不必要的字段
        self.filter_unwanted_field(config_json)
        # 写入 config.json 文件
        with open(CONFIG_FILEPATH_USER, "w", encoding="utf-8") as f:
            json.dump(config_json, f, indent=2, ensure_ascii=False)

    def filter_unwanted_field(self, config_json):
        return config_json


# 从default config中更新user config（升级用）
def update_config_files_from_default_to_user():
    with open(CONFIG_FILEPATH_DEFAULT, "r", encoding="utf-8") as f:
        default_data = json.load(f)

    with open(CONFIG_FILEPATH_USER, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    # 将 default 中有的、user 中没有的属性从 default 写入 user中
    for key, value in default_data.items():
        if key not in user_data:
            user_data[key] = value
    # 将 default 中没有的、user 中有的属性从 user 中删除
    keys_to_remove = [key for key in user_data.keys() if key not in default_data]
    for key in keys_to_remove:
        del user_data[key]
    # 将更新后的 default 数据写入 user.json 文件
    with open(CONFIG_FILEPATH_USER, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)


def initialize_config():
    if not os.path.exists(CONFIG_FILEPATH_USER):
        logger.info("-User config not found, will be created.")
        shutil.copyfile(CONFIG_FILEPATH_DEFAULT, CONFIG_FILEPATH_USER)


def get_config_json():
    initialize_config()
    update_config_files_from_default_to_user()
    with open(CONFIG_FILEPATH_USER, "r", encoding="utf-8") as f:
        config_json = json.load(f)
    return config_json


config = Config(**get_config_json())


if __name__ == "__main__":
    print(vars(config))
    print(config)

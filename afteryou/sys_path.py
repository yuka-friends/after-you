import os

from afteryou.config import config

FILEPATH_CHARCTER = os.path.join(config.userdata_filepath, "character.csv")
FILEPATH_CHARCTER_MAIL = os.path.join(config.userdata_filepath, "mail_character.csv")
FILEPATH_DB = os.path.join(config.userdata_filepath, "afteryou.db")
FILEPATH_VDB_JOURNAL = os.path.join(config.userdata_filepath, "afteryou_journal.vdb")
TRAY_LOCK_PATH = os.path.join("cache", "lock", "webui.lock")
CACHE_DICT = os.path.join("cache", "cache_dict.json")

import os
import shutil

WINDOWS_FONT_FILEPATH = "C:/Windows/Fonts/"
DEFAULT_FONT_FILEPATH = "__assets__\\LXGWWenKaiGBScreen.ttf"
TARGET_FONT_FILEPATH = os.path.join(WINDOWS_FONT_FILEPATH, os.path.basename(DEFAULT_FONT_FILEPATH))

if not os.path.exists(TARGET_FONT_FILEPATH):
    print(f"installing font {DEFAULT_FONT_FILEPATH}")
    try:
        shutil.copy(DEFAULT_FONT_FILEPATH, TARGET_FONT_FILEPATH)
    except PermissionError:
        print("install fail, try rerun as administration.")

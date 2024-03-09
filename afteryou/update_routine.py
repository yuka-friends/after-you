import os
import shutil

WINDOWS_FONT_FILEPATH = "C:/Windows/Fonts/"
DEFAULT_FONT_FILEPATH = "__assets__\\LXGWWenKaiGBScreen.ttf"
TARGET_FONT_FILEPATH = os.path.join(WINDOWS_FONT_FILEPATH, os.path.basename(DEFAULT_FONT_FILEPATH))

try:
    print("   Checking if the embedded model has been downloaded, if so it will be skipped.")
    from afteryou import embed_manager

    embed_manager.get_model(mode="cpu")
except Exception as e:
    print(e)
    print("   uform 模型似乎下载失败，请检查网络、添加代理或进行重试。")
    print("   uform model seems to have failed to download, please check the network, add a proxy, or try again.")


if not os.path.exists(TARGET_FONT_FILEPATH):
    print(f"installing font {DEFAULT_FONT_FILEPATH}")
    try:
        shutil.copy(DEFAULT_FONT_FILEPATH, TARGET_FONT_FILEPATH)
    except PermissionError:
        print("install font fail, try rerun as administration.")

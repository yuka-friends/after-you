import os
import shutil
import platform


from afteryou.config import config

WINDOWS_FONT_FILEPATH = "C:/Windows/Fonts/"
DEFAULT_FONT_FILEPATH = os.path.join("__assets__", "LXGWWenKaiGBScreen.ttf")
TARGET_FONT_FILEPATH = os.path.join(WINDOWS_FONT_FILEPATH, os.path.basename(DEFAULT_FONT_FILEPATH))



def install_font():
    if platform.system() == 'Windows':
        if not os.path.exists(TARGET_FONT_FILEPATH):
            print(f"installing font {DEFAULT_FONT_FILEPATH}")
            try:
                shutil.copy(DEFAULT_FONT_FILEPATH, TARGET_FONT_FILEPATH)
            except PermissionError:
                print("install font fail, try rerun as administration.")
    elif platform.system() == 'Darwin':   # macOS
        # 获得用户家目录
        home = os.path.expanduser("~")
        font_folder = os.path.join(home, "Library", "Fonts")

        # 如果字体文件夹不存在，则创建它
        if not os.path.isdir(font_folder):
            os.makedirs(font_folder)

        # 复制字体文件到字体文件夹
        try:
            shutil.copy2(DEFAULT_FONT_FILEPATH, font_folder)
            print(f'Font installed at: {os.path.join(font_folder, os.path.basename(DEFAULT_FONT_FILEPATH))}')
        except Exception as e:
            print(f"Unable to install font due to error: {e}")


try:
    install_font()
except Exception as e:
    print(e)

if not platform.system() == 'Darwin': 
    try:    
        print("   Checking if the embedded model has been downloaded, if so it will be skipped.")
        from afteryou import embed_manager

        embed_manager.get_model(mode="cpu")
        print("   Embedding function has been enabled.")
        config.set_and_save_config("enable_embedding", True)
    except Exception as e:
        print(e)
        print("   uform 模型似乎下载失败，请检查网络、添加代理或进行重试。")
        print("   uform model seems to have failed to download, please check the network, add a proxy, or try again.")
        print("")
        print("   Embedding function has been disabled.")
        config.set_and_save_config("enable_embedding", False)

import os
import subprocess
import sys

from afteryou import file_utils, utils
from afteryou.config import config
from afteryou.sys_path import TRAY_LOCK_PATH

if os.path.exists(TRAY_LOCK_PATH):
    with open(TRAY_LOCK_PATH, encoding="utf-8") as f:
        check_pid = int(f.read())

    tray_is_running = utils.is_process_running(check_pid, compare_process_name="python.exe")
    if tray_is_running:
        subprocess.run("cls", shell=True)
        print("After you seems to be running, please try to close it and retry.")
        print()
        print(f"PID: {check_pid}")
        sys.exit()
    else:
        try:
            os.remove(TRAY_LOCK_PATH)
        except FileNotFoundError:
            pass


# 全部向导的步骤数
ALLSTEPS = 3


# 画分割线的
def divider():
    print("\n--------------------------------------------------------------------\n")


# 画抬头的
def print_header(step=1, toast=""):
    subprocess.run("cls", shell=True)
    print("Weclome to After you | 欢迎使用\n")
    print("Thanks for downloading! This Quick Wizard will help you set it up. \n感谢下载使用！本向导将协助你完成基础配置项。不用担心，所有选项之后都可以再次调整。")
    divider()
    print(step, "/", ALLSTEPS, toast)
    print("\n")


# ========================================================

subprocess.run("color 06", shell=True)

while True:
    print_header(step=1)
    print(
        f"""
    首先，请设置用户文件夹路径。
    First, please set the userdata folder path.

    它将包含你记录的所有数据。你可以在想放置文件夹的路径新建一个文件夹，然后将其拖入到这个窗口中，回车确认。你也可以直接回车确认，这样将会把用户文件夹设置在 app 目录下。
    It will contain all the data you recorded. You can create a new folder in the path where you want to place the folder, then drag it into this window and press Enter to confirm. You can also press Enter directly to confirm, which will set the user folder in the app directory.

    Press [ENTER] to keep on current userdata path: {config.userdata_filepath}
    """
    )

    divider()
    input_userdata_path = input("> ")
    input_userdata_path = input_userdata_path.rstrip()
    if input_userdata_path:
        file_utils.ensure_dir(input_userdata_path)
        config.set_and_save_config("userdata_filepath", input_userdata_path)
    else:
        pass
    break


while True:
    print_header(step=2)
    print(
        f"""
    水晶球是由语言模型驱动的伙伴，它会回复你的想法、写信给你。
    Crystal Ball is a language model-driven companion that responds to your thoughts and writes to you.

    你希望水晶球如何称呼你？
    What would you like the crystal ball to call you?

    Press [ENTER] to keep on current name: {config.username}
"""
    )

    divider()
    input_username = input("> ")
    input_username = input_username.rstrip()
    if input_username:
        config.set_and_save_config("username", input_username)
        break
    elif len(config.username) > 0:
        print(f"Your name remains {config.username}. Don't worry, you can change it anytime in settings.")
        break


while True:
    print_header(step=3)
    print(
        """
    基本设置已完成！接下来请打开 start_app.bat 即可开始记录你的想法。
    你可能需要在 app 中填写语言模型服务商或本地语言模型提供的 [api key] 等信息以供生成内容。

    Basic setup is complete! Next, you can open start_app.bat to write down your thoughts and ideas.
    You may need to fill in the [api key] etc. provided by the language model service provider or local language model in the app to generate content.
"""
    )

    divider()
    break

<h1 align="center"> 🧡 After you</h1>
<p align="center"> Your proactive AI diary, recording moods and musings, responding to your heart's call </p>
<p align="center">主动回应你心声 的 AI 日记本，记录心情与碎碎念</p>

![product-header.jpg](https://github.com/yuka-friends/after-you/blob/main/__assets__/product-header.jpg)

After You is an idea recording tool inspired by [心光](https://apps.apple.com/cn/app/%E5%BF%83%E5%85%89-%E8%AE%B0%E5%BD%95%E7%94%9F%E6%B4%BB%E6%97%A5%E5%B8%B8-ai-%E6%97%A5%E8%AE%B0-%E7%AC%94%E8%AE%B0). Leveraging the power of language models, it actively responds to your thoughts, understands your emotions, helps you find similar past ideas, and sends letters from the shimmering crystal ball. All data is stored locally, you can synchronize userdata folders to cloud like Dropbox or Onedrive.

After you 是一款受 [心光](https://apps.apple.com/cn/app/%E5%BF%83%E5%85%89-%E8%AE%B0%E5%BD%95%E7%94%9F%E6%B4%BB%E6%97%A5%E5%B8%B8-ai-%E6%97%A5%E8%AE%B0-%E7%AC%94%E8%AE%B0) 启发的碎片想法记录工具。通过语言模型接口，她可以主动回应你的想法、洞察你的情绪，帮助你寻找相似的过往想法，从水晶球煜煜微光送来信件。所有数据都存储在本地，你可以将数据文件夹同步于云盘。

![screenshot_daily.jpg](https://github.com/yuka-friends/after-you/blob/main/__assets__/screenshot_daily.jpg)

---

> [!WARNING]
> This project is still in the early stages of development, and you may encounter some minor problems in experience and use, feel free to submit issue feedback, follow updates, and initiate discussions or roadmap in [Discussions](https://github.com/yuka-friends/Windrecorder/discussions).You are also welcome to help us optimize and build the project, submit PR/review.

### 🚧 roadmap
- [ ] journal static
- [ ] responsive layout for mobile
- [ ] add imgae vision index
- [ ] add tag search and summary
- [ ] weather info to LLM
- [ ] tts


## 🧡 How to Install

- Install [Git](https://git-scm.com/download/win), just keep clicking next.

- Install [Python](https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe), make sure to check `Add python.exe to PATH` when installing.

- In file explorer, navigate to the directory where you want to install After-you, and download the tool through the terminal command `git clone https://github.com/yuka-friends/after-you`;

    - (on Windows) You can open the folder you want to install, enter `cmd` in the path bar and press Enter, you will be located into current directory in terminal, then paste the above command and press Enter to execute; 

    - Currently, if there are spaces in the installation path, an error may occur on app startup.

- Open `install_update.bat` in the directory as Administrator to install dependencies and configure the app. If everything goes well, you can start using it!

    - The script uses administrator rights to install fonts. You can also manually install the fonts in `__assets__` and then open the installation script with normal rights.

## 🧡 How to use

- Open `start_app.bat` in the directory, the tool will host a web server so you can visit by browser (usually at http://localhost:8501 ,The specific situation may be different, please check the CLI window.);

- You need to fill in the api info provided by the large language model service on the settings page, including base url, api key, and model name. You can find relevant information in the model service provider's backend or help documentation.
    - Currently accessed through an OpenAI-compatible interface. You can use [OpenAI](https://openai.com/), [Groq](https://console.groq.com/keys) (free for now), [Moonshot](https://platform.moonshot.cn/console/api-keys) (Provide free quota), [LM studio](https://lmstudio.ai/)/[Ollama](https://ollama.com/) (run local LLMs) and any other model service compatible with.

- After the service is started, devices under the same LAN can also access After you. In this way, you can record and browse on different devices.
    - Responsive layout for mobile is still under development


## 🧡 big thanks

Thanks to the following projects

- https://github.com/lxgw/LxgwWenKai-Screen
- https://github.com/unum-cloud/uform
- https://github.com/streamlit/streamlit

🧡 Like this tool? Also check out [YUKA NAGASE](https://www.youtube.com/channel/UCf-PcSHzYAtfcoiBr5C9DZA)'s gentle music on Youtube and streaming music platforms. The app's name comes from her same name song: [アフターユ](https://www.youtube.com/watch?v=Dy3veX16oYY&ab_channel=YUKANAGASE-Topic).
bilibili shell (B站视频下载器)

一个基于 Python 开发的轻量级爬虫工具，旨在研究和学习流媒体传输协议及音视频合成技术。

A lightweight Bilibili video downloader developed in Python, designed for researching and learning streaming protocols and audio-visual synthesis.

---

## 📖 项目简介 | Introduction

本项目利用 Python 的 `requests` 库及 `FFmpeg` 核心组件，实现了对 Bilibili 视频及音频流的解析与合并。其核心功能包括：
* 自动识别并获取视频的最高分辨率流 (DASH)。
* 自动识别并获取视频的最高音质音频流。
* 利用 FFmpeg 无损合并音视频。
* 支持清理文件名非法字符，确保多平台兼容。

This project utilizes the Python `requests` library and `FFmpeg` core components to parse and merge Bilibili video and audio streams. Key features include:
* Auto-detection of the highest resolution video streams (DASH).
* Auto-detection of the highest quality audio streams.
* Lossless merging of audio and video using FFmpeg.
* Sanitization of filenames for cross-platform compatibility.

---

## ⚖️ 免责声明 | Disclaimer (Crucial!)

**请务必仔细阅读以下条款：**

1.  **仅限学习与研究**：本项目仅供编程爱好者学习 Python 爬虫技术、流媒体传输协议（DASH）以及 FFmpeg 使用方法。严禁用于任何商业用途。
2.  **版权尊重**：所有通过本工具下载的内容，其版权均归原作者及平台所有。用户在下载后必须在 24 小时内删除，且不得进行二次分发、传播或用于非法盈利。
3.  **用户责任**：用户因违反相关法律法规、侵犯他人著作权而产生的任何后果，由用户本人承担，本项目作者不承担任何法律责任。
4.  **无侵权意图**：本项目通过公开接口获取数据，不包含任何破解、绕过技术手段或破坏数字版权管理（DRM）的行为。若相关平台认为本项目侵犯其权益，请联系作者删除。

**Please read the following terms carefully:**

1.  **Educational Purpose Only**: This project is intended for learning Python crawling techniques, streaming protocols (DASH), and FFmpeg usage. Commercial use is strictly prohibited.
2.  **Respect Copyright**: The copyright of all content downloaded through this tool belongs to the original creators and the platform. Users must delete the downloaded content within 24 hours and shall not redistribute, broadcast, or use it for illegal profit.
3.  **User Responsibility**: The user is solely responsible for any consequences arising from the violation of relevant laws, regulations, or copyrights. The author of this project assumes no legal liability.
4.  **No Infringement Intended**: This project retrieves data via public interfaces and does not involve cracking, bypassing technical measures, or damaging Digital Rights Management (DRM). If the relevant platform believes this project infringes upon its rights, please contact the author for removal.

---

## 🛠️ 环境要求 | Requirements

* **Python 3.x**
* **FFmpeg**: 必须安装并在系统 PATH 中，或放置在 `ffmpeg_bin` 文件夹内。
* **Python Libraries**: `pip install requests`

## 🚀 快速开始 | Quick Start

1.  克隆或下载本项目。
2.  运行脚本：`python bilibili.py`
3.  按提示输入视频链接即可。

1. Clone or download the project.
2. Run the script: `python bilibili.py`
3. Enter the video link as prompted.

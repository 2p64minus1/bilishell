import requests
import re
import os
import json
import subprocess
import sys
import time
from urllib.parse import unquote


def get_resource_path(relative_path):
    """获取资源的绝对路径。打包进exe后，能正确定位到临时解压目录的文件"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def find_ffmpeg():
    """查找可用的ffmpeg"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ 找到系统PATH中的ffmpeg")
        return 'ffmpeg'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    ffmpeg_path = get_resource_path(os.path.join("ffmpeg_bin", "ffmpeg.exe"))
    if os.path.exists(ffmpeg_path):
        print("✅ 找到本地ffmpeg_bin文件夹中的ffmpeg")
        return ffmpeg_path

    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg"),
        "./ffmpeg.exe",
        "./ffmpeg"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ 找到ffmpeg: {path}")
            return path

    print("❌ 未找到ffmpeg，请确保ffmpeg可用")
    return None


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    invalid_chars = r'[<>:"/\\|?*\s]'
    return re.sub(invalid_chars, '_', filename)


def safe_input(prompt=""):
    """安全的输入函数，避免打包后stdin问题"""
    try:
        # 尝试正常输入
        return input(prompt)
    except (EOFError, RuntimeError):
        # 如果出现错误，使用备用方法
        print(prompt, end='', flush=True)
        if sys.platform == "win32":
            # Windows系统使用msvcrt
            try:
                import msvcrt
                input_chars = []
                while True:
                    char = msvcrt.getwch()
                    if char in ('\r', '\n'):
                        print()
                        break
                    elif char == '\x08':  # 退格键
                        if input_chars:
                            input_chars.pop()
                            print('\b \b', end='', flush=True)
                    else:
                        input_chars.append(char)
                        print(char, end='', flush=True)
                return ''.join(input_chars)
            except ImportError:
                pass
        # 如果其他方法都失败，返回空字符串
        return ""


def wait_for_exit():
    """等待用户退出的安全方法"""
    print("\n程序将在5秒后自动退出...")
    for i in range(5, 0, -1):
        print(f"\r倒计时: {i}秒", end='', flush=True)
        time.sleep(1)
    print("\r程序退出！          ")


def get_video_info(bvid, url):
    """获取视频信息（标题、视频URL、音频URL）"""
    print("🎬 正在获取视频信息...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': url,
        'Origin': 'https://www.bilibili.com'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 提取视频标题
        title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text)
        if title_match:
            title = unquote(title_match.group(1).split('_哔哩哔哩')[0])
        else:
            title = f"B站视频_{bvid}"

        title = sanitize_filename(title)
        print(f"📝 视频标题: {title}")

        # 提取视频信息JSON
        playinfo_match = re.search(r'<script>window\.__playinfo__=({.*?})</script>', response.text)
        if not playinfo_match:
            raise Exception("无法提取视频播放信息")

        playinfo = json.loads(playinfo_match.group(1))

        # 从dash格式获取视频和音频流
        if 'dash' in playinfo['data']:
            video_url, audio_url, quality_info = extract_dash_streams(playinfo, headers, url)
        else:
            raise Exception("未找到dash格式视频流")

        return {
            'title': title,
            'video_url': video_url,
            'audio_url': audio_url,
            'quality_info': quality_info
        }

    except Exception as e:
        print(f"❌ 获取视频信息失败: {e}")
        return None


def extract_dash_streams(playinfo, headers, url):
    """从dash格式中提取最高画质视频和最高音质音频流"""

    print("🔍 分析可用视频流...")

    # 提取视频流
    video_streams = playinfo['data']['dash']['video']

    # 显示所有可用的视频流信息
    print("📊 可用视频流信息:")
    for i, stream in enumerate(video_streams):
        height = stream.get('height', 0)
        width = stream.get('width', 0)
        bandwidth = stream.get('bandwidth', 0)
        codecs = stream.get('codecs', '未知')
        print(f"  流 {i + 1}: {width}x{height} (码率: {bandwidth}, 编码: {codecs})")

    # 按分辨率（height）和码率（bandwidth）排序，选择最高的
    video_streams.sort(key=lambda x: (x.get('height', 0), x.get('bandwidth', 0)), reverse=True)
    target_video = video_streams[0] if video_streams else None

    if target_video:
        height = target_video.get('height', '未知')
        width = target_video.get('width', '未知')
        bandwidth = target_video.get('bandwidth', 0)
        print(f"🎥 选择最高画质视频 (分辨率: {width}x{height}, 码率: {bandwidth})")
    else:
        raise Exception("未找到可用的视频流")

    # 提取音频流
    audio_streams = playinfo['data']['dash']['audio']

    # 显示所有可用的音频流信息
    print("🔊 可用音频流信息:")
    for i, stream in enumerate(audio_streams):
        bandwidth = stream.get('bandwidth', 0)
        codecs = stream.get('codecs', '未知')
        print(f"  流 {i + 1}: 码率: {bandwidth}, 编码: {codecs}")

    if audio_streams:
        # 按码率排序，选择最高的
        audio_streams.sort(key=lambda x: x.get('bandwidth', 0), reverse=True)
        target_audio = audio_streams[0]
        print(f"🔊 选择最高音质音频 (码率: {target_audio.get('bandwidth', 0)})")
    else:
        raise Exception("未找到可用的音频流")

    quality_info = {
        'video_width': target_video.get('width', '未知'),
        'video_height': target_video.get('height', '未知'),
        'video_bandwidth': target_video.get('bandwidth', 0),
        'audio_bandwidth': target_audio.get('bandwidth', 0)
    }

    return target_video['baseUrl'], target_audio['baseUrl'], quality_info


def download_file(url, filename, headers, file_type):
    """下载文件并显示进度"""
    print(f"⏬ 开始下载{file_type}...")

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size > 0:
                        percent = (downloaded_size / total_size) * 100
                        print(f"\r📥 下载进度: {percent:.1f}% ({downloaded_size}/{total_size} bytes)", end='',
                              flush=True)

        print(f"\n✅ {file_type}下载完成!")
        return True

    except Exception as e:
        print(f"\n❌ {file_type}下载失败: {e}")
        return False


def merge_video_audio(video_file, audio_file, output_file, ffmpeg_path):
    """使用ffmpeg合并视频和音频"""
    print("🔄 正在合并音视频...")

    try:
        cmd = [
            ffmpeg_path,
            '-i', video_file,
            '-i', audio_file,
            '-c', 'copy',
            '-y',
            '-loglevel', 'error',
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
        print("✅ 音视频合并完成!")

        if os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(audio_file):
            os.remove(audio_file)
        print("🗑️  临时文件已清理")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 合并失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 合并过程中发生错误: {e}")
        return False


def main():
    print("🚀 B站视频下载器启动!")
    print("🎯 本次将下载最高画质和最高音质!")

    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        print("""
❌ 未找到ffmpeg，无法继续处理视频。

解决方法：
1. 请确保ffmpeg.exe位于程序所在目录的ffmpeg_bin文件夹中
2. 或者已将ffmpeg添加到系统PATH环境变量
        """)
        wait_for_exit()
        return

    video_url = safe_input("请输入B站视频链接: ").strip()
    if not video_url:
        print("❌ 未输入视频链接")
        wait_for_exit()
        return

    bvid_match = re.search(r'(BV[0-9A-Za-z]{10})', video_url)
    if not bvid_match:
        print("❌ 无效的B站视频链接")
        wait_for_exit()
        return

    bvid = bvid_match.group(1)
    print(f"🎯 目标视频: {bvid}")

    video_info = get_video_info(bvid, video_url)
    if not video_info:
        wait_for_exit()
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': video_url,
        'Origin': 'https://www.bilibili.com'
    }

    video_file = f"temp_video_{bvid}.mp4"
    if not download_file(video_info['video_url'], video_file, headers, "视频"):
        wait_for_exit()
        return

    audio_file = f"temp_audio_{bvid}.mp3"
    if not download_file(video_info['audio_url'], audio_file, headers, "音频"):
        if os.path.exists(video_file):
            os.remove(video_file)
        wait_for_exit()
        return

    output_file = f"{video_info['title']}_{bvid}.mp4"
    if merge_video_audio(video_file, audio_file, output_file, ffmpeg_path):
        print(f"🎉 视频下载并保存为: {output_file}")
        if 'quality_info' in video_info:
            quality = video_info['quality_info']
            print(f"📊 最终视频质量: {quality['video_width']}x{quality['video_height']}")
    else:
        print("❌ 下载过程完成但合并失败")

    wait_for_exit()


if __name__ == "__main__":
    main()
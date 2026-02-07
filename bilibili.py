import requests
import re
import os
import json
import subprocess
import sys
import time
from urllib.parse import unquote


def where_is_my_stuff(a):
    if getattr(sys, 'frozen', False):
        b = sys._MEIPASS
    else:
        b = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(b, a)


def find_that_magic_tool():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ 找到系统PATH中的ffmpeg")
        return 'ffmpeg'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    c = where_is_my_stuff(os.path.join("ffmpeg_bin", "ffmpeg.exe"))
    if os.path.exists(c):
        print("✅ 找到本地ffmpeg_bin文件夹中的ffmpeg")
        return c

    d = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg"),
        "./ffmpeg.exe",
        "./ffmpeg"
    ]

    for e in d:
        if os.path.exists(e):
            print(f"✅ 找到ffmpeg: {e}")
            return e

    print("❌ 未找到ffmpeg，请确保ffmpeg可用")
    return None


def clean_this_mess(f):
    g = r'[<>:"/\\|?*\s]'
    return re.sub(g, '_', f)


def gimme_input(h=""):
    try:
        return input(h)
    except (EOFError, RuntimeError):
        print(h, end='', flush=True)
        if sys.platform == "win32":
            try:
                import msvcrt
                i = []
                while True:
                    j = msvcrt.getwch()
                    if j in ('\r', '\n'):
                        print()
                        break
                    elif j == '\x08':
                        if i:
                            i.pop()
                            print('\b \b', end='', flush=True)
                    else:
                        i.append(j)
                        print(j, end='', flush=True)
                return ''.join(i)
            except ImportError:
                pass
        return ""


def bye_bye_timer():
    print("\n程序将在5秒后自动退出...")
    for k in range(5, 0, -1):
        print(f"\r倒计时: {k}秒", end='', flush=True)
        time.sleep(1)
    print("\r程序退出！          ")


def get_stupid_video_info(l, m):
    print("🎬 正在获取视频信息...")

    n = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': m,
        'Origin': 'https://www.bilibili.com'
    }

    try:
        o = requests.get(m, headers=n)
        o.raise_for_status()

        p = re.search(r'<title[^>]*>(.*?)</title>', o.text)
        if p:
            q = unquote(p.group(1).split('_哔哩哔哩')[0])
        else:
            q = f"B站视频_{l}"

        q = clean_this_mess(q)
        print(f"📝 视频标题: {q}")

        r = re.search(r'<script>window\.__playinfo__=({.*?})</script>', o.text)
        if not r:
            raise Exception("无法提取视频播放信息")

        s = json.loads(r.group(1))

        if 'dash' in s.get('data', {}):
            t, u, v = bilibili_do_not_kill_me(s, n, m)
        else:
            raise Exception("未找到dash格式视频流")

        return {
            'title': q,
            'video_url': t,
            'audio_url': u,
            'quality_info': v
        }

    except Exception as w:
        print(f"❌ 获取视频信息失败: {w}")
        return None


def bilibili_do_not_kill_me(x, y, z):
    print("🔍 分析可用视频流...")

    aa = x.get('data', {}).get('dash', {})
    ab = aa.get('video', [])

    print("📊 可用视频流信息:")
    for ac, ad in enumerate(ab):
        ae = ad.get('height', 0)
        af = ad.get('width', 0)
        ag = ad.get('bandwidth', 0)
        ah = ad.get('codecs', '未知')
        print(f"  流 {ac + 1}: {af}x{ae} (码率: {ag}, 编码: {ah})")

    ab.sort(key=lambda ai: (ai.get('height', 0), ai.get('bandwidth', 0)), reverse=True)
    aj = ab[0] if ab else None

    if aj:
        ae = aj.get('height', '未知')
        af = aj.get('width', '未知')
        ag = aj.get('bandwidth', 0)
        print(f"🎥 选择最高画质视频 (分辨率: {af}x{ae}, 码率: {ag})")
    else:
        raise Exception("未找到可用的视频流")

    ak = aa.get('audio', [])
    al = None
    am = 0

    if ak:
        print("🔊 可用音频流信息:")
        for ac, ad in enumerate(ak):
            ag = ad.get('bandwidth', 0)
            ah = ad.get('codecs', '未知')
            print(f"  流 {ac + 1}: 码率: {ag}, 编码: {ah}")

        ak.sort(key=lambda an: an.get('bandwidth', 0), reverse=True)
        ao = ak[0]
        al = ao['baseUrl']
        am = ao.get('bandwidth', 0)
        print(f"🔊 选择最高音质音频 (码率: {am})")
    else:
        print("⚠️ 该视频没有可用的音频流，将仅下载视频部分。")

    ap = {
        'video_width': aj.get('width', '未知'),
        'video_height': aj.get('height', '未知'),
        'video_bandwidth': aj.get('bandwidth', 0),
        'audio_bandwidth': am
    }

    return aj['baseUrl'], al, ap


def grab_it(aq, ar, as_headers, at):
    print(f"⏬ 开始下载{at}...")

    try:
        au = requests.get(aq, headers=as_headers, stream=True)
        au.raise_for_status()

        av = int(au.headers.get('content-length', 0))
        aw = 0

        with open(ar, 'wb') as ax:
            for ay in au.iter_content(chunk_size=8192):
                if ay:
                    ax.write(ay)
                    aw += len(ay)

                    if av > 0:
                        az = (aw / av) * 100
                        print(f"\r📥 下载进度: {az:.1f}% ({aw}/{av} bytes)", end='',
                              flush=True)

        print(f"\n✅ {at}下载完成!")
        return True

    except Exception as ba:
        print(f"\n❌ {at}下载失败: {ba}")
        return False


def mix_them_up(bb, bc, bd, be):
    print("🔄 正在处理音视频...")

    try:
        if bc and os.path.exists(bc):
            bf = [be, '-i', bb, '-i', bc, '-c', 'copy', '-y', '-loglevel', 'error', bd]
        else:
            bf = [be, '-i', bb, '-c', 'copy', '-y', '-loglevel', 'error', bd]

        bg = subprocess.run(bf, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
        print("✅ 处理完成!")

        if os.path.exists(bb):
            os.remove(bb)
        if bc and os.path.exists(bc):
            os.remove(bc)
        print("🗑️  临时文件已清理")

        return True

    except subprocess.CalledProcessError as bh:
        print(f"❌ 处理失败: {bh}")
        if bh.stderr:
            print(f"错误信息: {bh.stderr}")
        return False
    except Exception as bi:
        print(f"❌ 处理过程中发生错误: {bi}")
        return False


def main():
    print("🚀 B站视频下载器启动!")
    print("🎯 本次将下载最高画质和最高音质!")

    bj = find_that_magic_tool()
    if not bj:
        print("""
❌ 未找到ffmpeg，无法继续处理视频。

解决方法：
1. 请确保ffmpeg.exe位于程序所在目录的ffmpeg_bin文件夹中
2. 或者已将ffmpeg添加到系统PATH环境变量
        """)
        bye_bye_timer()
        return

    bk = gimme_input("请输入B站视频链接: ").strip()
    if not bk:
        print("❌ 未输入视频链接")
        bye_bye_timer()
        return

    bl = re.search(r'(BV[0-9A-Za-z]{10})', bk)
    if not bl:
        print("❌ 无效的B站视频链接")
        bye_bye_timer()
        return

    bm = bl.group(1)
    print(f"🎯 目标视频: {bm}")

    bn = get_stupid_video_info(bm, bk)
    if not bn:
        bye_bye_timer()
        return

    bo = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': bk,
        'Origin': 'https://www.bilibili.com'
    }

    bp = f"temp_video_{bm}.mp4"
    if not grab_it(bn['video_url'], bp, bo, "视频"):
        bye_bye_timer()
        return

    bq = None
    if bn['audio_url']:
        bq = f"temp_audio_{bm}.mp3"
        if not grab_it(bn['audio_url'], bq, bo, "音频"):
            if os.path.exists(bp):
                os.remove(bp)
            bye_bye_timer()
            return

    br = f"{bn['title']}_{bm}.mp4"
    if mix_them_up(bp, bq, br, bj):
        print(f"🎉 视频下载并保存为: {br}")
        if 'quality_info' in bn:
            bs = bn['quality_info']
            print(f"📊 最终视频质量: {bs['video_width']}x{bs['video_height']}")
    else:
        print("❌ 下载过程完成但合并失败")

    bye_bye_timer()


if __name__ == "__main__":
    main()

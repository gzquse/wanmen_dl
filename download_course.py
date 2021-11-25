import os
import sys
import requests
from config import CONFIG
from m3u8 import download
from utils import to_name, get_headers


def fetch_course(course_id: str, course_name: str, base_dir: str):
    course_name = to_name(course_name)
    base_dir = os.path.join(base_dir, course_name)

    print(f"开始获取 {course_name} 的课程信息")

    r = requests.get(f'https://api.wanmen.org/4.0/content/lectures?courseId={course_id}&debug=1', headers=get_headers())

    if r.status_code != 200:
        print("错误 - 无法获取课程信息")
        print(r.status_code, r.reason)
        exit(-1)

    chapters = r.json()

    print("获取成功，即将开始下载")
    for i, chapter in enumerate(chapters, 1):
        chapter_name = to_name(chapter['name'])

        print(f"开始下载第 {i} 章：{chapter_name}")
        chapter_dir = os.path.join(base_dir, f"{i} - {chapter_name}")
        os.makedirs(chapter_dir, exist_ok=True)
        for j, lecture in enumerate(chapter['children'], 1):
            fetch_single(f'{i}-{j}', lecture, chapter_dir)
    print(f"{course_name} 下载完成")


def fetch_single(lecture_index: str, lecture_info: dict, base_dir: str):
    lecture_id = lecture_info['_id']
    lecture_name = lecture_index + ' ' + to_name(lecture_info['name'])

    print(f"[{lecture_name}] 正在准备下载")

    save_to = os.path.join(base_dir, lecture_name + '.mp4')

    if os.path.exists(save_to):
        print(save_to, "已存在 -> 跳过")
        return

    r = requests.get(f'https://api.wanmen.org/4.0/content/lectures/{lecture_id}?routeId=main&debug=1', headers=get_headers())

    if r.status_code != 200:
        print("错误 - 无法获取课程信息")
        print(r.status_code, r.reason)
        exit(-1)

    lecture_info = r.json()

    # print(lecture_info)

    if lecture_info.get('video'):
        video_m3u8_url = lecture_info['video']['hls']['pcHigh']
        video_m3u8_url_mid = lecture_info['video']['hls']['pcMid']
    else:
        video_m3u8_url = lecture_info['hls']['pcHigh']
        video_m3u8_url_mid = lecture_info['hls']['pcMid']

    print(f"[{lecture_name}] 开始下载")
    download(video_m3u8_url, video_m3u8_url_mid, save_to)
    print(f"[{lecture_name}] 下载完成")


if __name__ == '__main__':
    course_id = sys.argv[1]

    if len(sys.argv) > 2:
        course_name = sys.argv[2]
    else:
        course_name = CONFIG['NameMap'][course_id]

    fetch_course(course_id, course_name, CONFIG['DownloadTo'])

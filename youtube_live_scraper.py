import os
import requests

# 从环境变量中获取 API 密钥
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("未找到 YOUTUBE_API_KEY，请设置环境变量。")

# 预定义的频道 URL 和分类
channels = {
    "台湾": [
        "https://www.youtube.com/@中天电视CtiTv",
        "https://www.youtube.com/@newsebc"
    ],
    "追剧": [
        "https://www.youtube.com/@gtv-drama"
    ],
    "娱乐": [
        # 添加其他娱乐频道 URL
    ],
    "国外": [
        # 添加其他国外频道 URL
    ]
}

# 获取频道 ID
def get_channel_id(channel_url):
    username = channel_url.split('@')[-1]
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=id&q={username}&type=channel&key={API_KEY}"
    response = requests.get(search_url).json()
    items = response.get('items')
    if items:
        return items[0]['id']['channelId']
    return None

# 获取直播视频
def get_live_videos(channel_id):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&eventType=live&type=video&key={API_KEY}"
    response = requests.get(search_url).json()
    items = response.get('items')
    live_videos = []
    if items:
        for item in items:
            title = item['snippet']['title']
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            live_videos.append(f"{title}, {video_url}")
    return live_videos

# 主函数
def main():
    results = {}
    for category, urls in channels.items():
        live_streams = []
        for url in urls:
            channel_id = get_channel_id(url)
            if channel_id:
                live_videos = get_live_videos(channel_id)
                live_streams.extend(live_videos)
        if live_streams:
            results[category] = live_streams

    # 将结果写入桌面上的文本文件
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_file = os.path.join(desktop_path, "youtube_live_streams.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        for category, streams in results.items():
            f.write(f"\n")
            for stream in streams:
                f.write(f"{stream}\n")
            f.write("\n")
    print(f"直播链接已保存到 {output_file}")

if __name__ == "__main__":
    main()

import os
import requests
import json

# 替换为你的 YouTube API Key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  

# 频道 ID 列表（可手动查询，也可用 API 获取）
CHANNELS = {
    "gtv-drama": "UCz5CQdzYG0i3SddABZuc8pg",
    "cti-tv": "UCJrOtniJ0-NWz37R30urifQ",
    "newsebc": "UCaM49wLkBQwQYzqg1PzpyAA"
}

# 直播分类
CATEGORIES = {
    "台灣": ["gtv-drama", "cti-tv", "newsebc"],
    "娛樂": [],
    "追劇": ["gtv-drama"],
    "國外": []
}

OUTPUT_FILE = "youtube_live_streams.txt"


def get_live_streams(channel_id):
    """查询频道是否有正在直播的视频"""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&eventType=live&type=video&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "items" not in data:
        return []

    live_streams = []
    for item in data["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        live_streams.append(f"{title}: https://www.youtube.com/watch?v={video_id}")

    return live_streams


def classify_and_save():
    """获取所有频道的直播信息，并分类存储"""
    categorized_streams = {key: [] for key in CATEGORIES}

    for name, channel_id in CHANNELS.items():
        streams = get_live_streams(channel_id)
        if streams:
            for category, channels in CATEGORIES.items():
                if name in channels:
                    categorized_streams[category].extend(streams)

    # 过滤掉没有直播的分类
    categorized_streams = {k: v for k, v in categorized_streams.items() if v}

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for category, streams in categorized_streams.items():
            f.write(f"【{category}】\n")
            f.write("\n".join(streams))
            f.write("\n\n")

    print(f"✅ 直播数据已更新：{OUTPUT_FILE}")


if __name__ == "__main__":
    classify_and_save()

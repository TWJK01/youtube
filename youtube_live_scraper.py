import os
import json
from googleapiclient.discovery import build


API_KEY = os.getenv('YOUTUBE_API_KEY')  # ✅ 讀取 GitHub Secrets
if not API_KEY:
    raise ValueError("❌ 錯誤：未找到 YOUTUBE_API_KEY，請確認 GitHub Secrets 設置")

git add .github/workflows/schedule.yml
git commit -m "修正 API Key 讀取方式"
git push origin main
# 🔹 建立 YouTube API 服務
youtube = build('youtube', 'v3', developerKey=API_KEY)

# 🔹 頻道分類
CHANNELS = {
    "台灣": [
        "https://www.youtube.com/@中天電視CtiTv",
        "https://www.youtube.com/@newsebc",
    ],
    "娛樂": [
        "https://www.youtube.com/@gtv-drama",
    ],
    "追劇": [
        "https://www.youtube.com/@gtv-drama",
    ],
    "國外": []
}

# 🔹 解析 YouTube 頻道網址，取得頻道 ID
def get_channel_id(channel_url):
    username = channel_url.split("@")[-1]
    response = youtube.search().list(
        part="snippet",
        type="channel",
        q=username
    ).execute()
    for item in response['items']:
        return item['id']['channelId']
    return None

# 🔹 查詢頻道是否有直播
def get_live_video(channel_id):
    response = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        eventType="live",
        type="video",
    ).execute()

    if response.get("items"):
        for item in response["items"]:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            return f"{title}, https://www.youtube.com/watch?v={video_id}"
    return None

# 🔹 抓取直播連結，分類儲存
def update_live_streams():
    results = {category: [] for category in CHANNELS}

    for category, urls in CHANNELS.items():
        for url in urls:
            channel_id = get_channel_id(url)
            if channel_id:
                live_video = get_live_video(channel_id)
                if live_video:
                    results[category].append(live_video)

    # 🔹 儲存為文字檔
    with open("live_streams.txt", "w", encoding="utf-8") as file:
        for category, videos in results.items():
            if videos:
                file.write(f"📌 {category} 直播:\n")
                for video in videos:
                    file.write(video + "\n")
                file.write("\n")

    print("✅ 直播連結已更新！")

# 🔹 執行更新
update_live_streams()

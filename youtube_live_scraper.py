import os
import time
from googleapiclient.discovery import build

# 讀取 API 金鑰
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("未讀取到 YOUTUBE_API_KEY，請設定 API 金鑰")

# 建立 YouTube API 服務物件
youtube = build('youtube', 'v3', developerKey=API_KEY)

# 設定頻道分類與對應頻道網址
# 根據需求您可以調整分類和頻道分配：
channels = {
    "台灣": [
        "https://www.youtube.com/@中天電視CtiTv",
        "https://www.youtube.com/@newsebc"
    ],
    "追劇": [
        "https://www.youtube.com/@gtv-drama"
    ],
    "娛樂": [
        "https://www.youtube.com/@新聞龍捲風NewsTornado"
    ],
    "國外": [
        # 如有其他國外頻道網址，請加入
    ]
}

# 輸出檔案路徑：嘗試寫入桌面（若存在），否則存到當前目錄
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
if os.path.isdir(desktop_path):
    OUTPUT_FILENAME = os.path.join(desktop_path, "youtube_live_streams.txt")
else:
    OUTPUT_FILENAME = "youtube_live_streams.txt"

def get_channel_id(channel_url):
    """
    從頻道 URL（例如 "https://www.youtube.com/@中天電視CtiTv"）
    解析出 "@" 後的名稱作為查詢關鍵字，返回搜尋結果中的頻道 ID。
    """
    try:
        if "@" in channel_url:
            query = channel_url.split("@")[-1].split("/")[0]
        else:
            query = channel_url
        response = youtube.search().list(
            part="snippet",
            type="channel",
            q=query,
            maxResults=1
        ).execute()
        items = response.get("items", [])
        if items:
            return items[0]["id"]["channelId"]
    except Exception as e:
        print(f"取得頻道 ID 失敗 ({channel_url}): {e}")
    return None

def get_live_video(channel_id):
    """
    查詢指定頻道是否有正在直播的影片。
    如果有，返回格式： "直播標題, https://www.youtube.com/watch?v=video_id"；否則返回 None。
    """
    try:
        response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            eventType="live",  # 只抓取正在直播的影片
            type="video",
            maxResults=1
        ).execute()
        items = response.get("items", [])
        if items:
            item = items[0]
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            return f"{title}, https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        print(f"取得直播資訊失敗 ({channel_id}): {e}")
    return None

def update_live_streams():
    """
    遍歷各分類的頻道網址，查詢是否有直播影片，
    只保留有直播的頻道，並將結果輸出成文字檔。
    """
    results = {}
    for category, url_list in channels.items():
        category_results = []
        for url in url_list:
            channel_id = get_channel_id(url)
            if channel_id:
                live_video = get_live_video(channel_id)
                if live_video:
                    category_results.append(live_video)
        if category_results:
            results[category] = category_results

    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write(f"更新時間：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            for category, videos in results.items():
                f.write(f"【{category}】\n")
                for video in videos:
                    f.write(video + "\n")
                f.write("\n")
        print(f"直播連結更新完成，結果已寫入 {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"寫入檔案失敗: {e}")

if __name__ == '__main__':
    update_live_streams()

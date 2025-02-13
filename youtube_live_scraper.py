import os
import time
from googleapiclient.discovery import build

# ==========================
# 設定區
# ==========================
API_KEY = os.getenv('AIzaSyCPpjo6Gd3Mwf9xFUHB2V1ZQJVia74-tE8')  # 讀取 GitHub Secrets 的 API 金鑰
OUTPUT_FILENAME = "youtube_live_streams.txt"

categories = {
    "台灣,#genre#": [
        "UC5q3xb4TCAyUOQ4Kw6pM_4w",  # 三立新聞
        "UCwbtZdhuhANYFNRPa99-16Q"   # 中天新聞
    ],
    "娛樂,#genre#": [
        "UCgrqsg_q3Ke9jBqUBRz1mLg",  # 娛樂百分百
        "UCO5H_yFl0d7G3hX8KoEdNtw"   # 綜藝大熱門
    ],
    "追劇,#genre#": [
        "UCcXfsEwXKjcRvshvjjzWZ0w",  # 愛奇藝台灣站
        "UC7dM8jN1h-j-a2a28OYzUlg"   # WeTV 直播
    ],
    "國外,#genre#": [
        "UCupvZG-5ko_eiXAupbDfxWw",  # CNN
        "UCBi2mrWuNuyYy4gbM6fU18Q"   # CBS News
    ]
}

# ==========================
# 功能函式
# ==========================
def get_live_stream_urls(youtube, channel_id):
    """查詢頻道是否正在直播，並回傳直播網址"""
    try:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            eventType="live",  # 只抓取正在直播的影片
            type="video"
        )
        response = request.execute()
        return [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in response.get("items", [])]
    except Exception as e:
        print(f"❌ 取得直播網址失敗 ({channel_id})：{e}")
        return []

def update_live_streams():
    """抓取正在直播的頻道，寫入文字檔"""
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    results = {}

    for category, channel_list in categories.items():
        results[category] = {}
        for channel_id in channel_list:
            live_urls = get_live_stream_urls(youtube, channel_id)
            if live_urls:  # 只有有直播時才記錄
                results[category][channel_id] = live_urls

    # ==========================
    # 輸出文字檔
    # ==========================
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write(f"📅 更新時間：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        for category, channel_info in results.items():
            if channel_info:  # 只寫入有直播的分類
                f.write(f"📌 分類：{category}\n")
                for channel_id, urls in channel_info.items():
                    for url in urls:
                        f.write(f"    🔗 {url}\n")
                    f.write("\n")
                f.write("-"*50 + "\n\n")

    print(f"✅ 直播網址更新完成！結果已寫入 {OUTPUT_FILENAME}")

# 執行抓取
update_live_streams()

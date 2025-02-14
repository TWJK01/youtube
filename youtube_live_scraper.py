import os
import time
from googleapiclient.discovery import build

# 從環境變數讀取 API 金鑰（請務必在 GitHub Secrets 中設定 YOUTUBE_API_KEY）
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("未讀取到 YOUTUBE_API_KEY，請檢查 GitHub Secrets 設定")

# 建立 YouTube API 服務
youtube = build('youtube', 'v3', developerKey=API_KEY)

# 設定各分類及對應的頻道網址
# ※ 請依需求修改，以下範例使用你提供的三個網址
categories = {
    "台灣": [
        "https://www.youtube.com/@中天電視CtiTv",
        "https://www.youtube.com/@newsebc"
    ],
    "娛樂": [
        "https://www.youtube.com/@gtv-drama"
    ],
    "追劇": [
        # 如有追劇類別的頻道，可加入網址
    ],
    "國外": [
        # 如有國外頻道，可加入網址
    ]
}

OUTPUT_FILENAME = "live_streams.txt"

def get_channel_id(channel_url):
    """
    由於網址為自訂名稱型態，利用查詢關鍵字取得頻道 ID。
    此方法會以 "@" 後的名稱作為查詢關鍵字，並回傳第一筆結果的頻道 ID。
    """
    # 取得 @ 之後的名稱
    if "@" in channel_url:
        query = channel_url.split("@")[-1].split("/")[0]
    else:
        query = channel_url
    # 利用 search API 查詢頻道
    response = youtube.search().list(
        part="snippet",
        type="channel",
        q=query,
        maxResults=1
    ).execute()
    items = response.get("items", [])
    if items:
        return items[0]["id"]["channelId"]
    return None

def get_live_video(channel_id):
    """
    查詢指定頻道是否有正在直播的影片，若有則回傳標題與連結的字串。
    """
    response = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        eventType="live",  # 僅查詢直播影片
        type="video",
        maxResults=1
    ).execute()

    items = response.get("items", [])
    if items:
        item = items[0]
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        return f"{title}, https://www.youtube.com/watch?v={video_id}"
    return None

def update_live_streams():
    """
    依分類抓取各頻道直播連結，並僅將有直播的頻道加入結果，
    最後將結果寫入 OUTPUT_FILENAME 文字檔中。
    """
    results = {}
    for category, url_list in categories.items():
        category_results = []
        for url in url_list:
            channel_id = get_channel_id(url)
            if channel_id:
                live_video = get_live_video(channel_id)
                if live_video:
                    category_results.append(live_video)
        if category_results:
            results[category] = category_results

    # 將結果寫入文字檔，覆蓋先前內容
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write(f"更新時間：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        for category, videos in results.items():
            f.write(f"【{category}】\n")
            for video in videos:
                f.write(video + "\n")
            f.write("\n")
    print(f"直播連結更新完成，結果已寫入 {OUTPUT_FILENAME}")

if __name__ == '__main__':
    update_live_streams()

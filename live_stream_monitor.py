import os
from googleapiclient.discovery import build

# 從環境變數中取得 API 金鑰（建議在 GitHub Secrets 中設定）
api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    raise Exception("請設定 YOUTUBE_API_KEY 環境變數。")

# 建立 YouTube API 客戶端
youtube = build('youtube', 'v3', developerKey=api_key)

# 頻道資訊設定：包含名稱、頻道網址（使用 handle 格式）與分類
# 請根據實際需求設定分類項目：例如「台灣」、「娛樂」、「追劇」、「國外」
channels = [
    {"name": "GTV Drama", "url": "https://www.youtube.com/@gtv-drama", "category": "追劇"},
    {"name": "中天電視CtiTv", "url": "https://www.youtube.com/@%E4%B8%AD%E5%A4%A9%E9%9B%BB%E8%A6%96CtiTv", "category": "娛樂"},
    {"name": "newsebc", "url": "https://www.youtube.com/@newsebc", "category": "台灣"}
]

def get_channel_id_from_url(url):
    """
    根據頻道網址 (格式如 https://www.youtube.com/@xxx) 取得頻道 ID
    由於 YouTube API 沒有直接透過 handle 查詢頻道 ID，故採用搜尋方式
    """
    handle = url.rstrip('/').split('/')[-1]
    try:
        request = youtube.search().list(
            part='snippet',
            q=handle,
            type='channel',
            maxResults=1
        )
        response = request.execute()
        items = response.get("items", [])
        if items:
            return items[0]["id"]["channelId"]
    except Exception as e:
        print(f"取得頻道 ID 失敗: {e}")
    return None

def is_live(channel_id):
    """
    檢查指定頻道 ID 是否有正在直播的影片
    """
    try:
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            eventType='live',
            type='video',
            maxResults=1
        )
        response = request.execute()
        return len(response.get('items', [])) > 0
    except Exception as e:
        print(f"檢查直播狀態失敗 (頻道ID: {channel_id}): {e}")
        return False

def update_live_streams():
    """
    檢查所有頻道是否有直播，依分類整理輸出成文字檔
    輸出格式：
      分類區塊（例如：台灣、娛樂、追劇、國外）
      每個區塊內以「名稱,網址」格式列出正在直播的頻道
      若無直播則該分類不列入結果
    """
    results = {}  # key 為分類，value 為該分類下正在直播的項目
    for channel in channels:
        channel_id = get_channel_id_from_url(channel["url"])
        if not channel_id:
            print(f"無法取得 {channel['name']} 的頻道 ID，跳過。")
            continue
        if is_live(channel_id):
            cat = channel["category"]
            results.setdefault(cat, []).append(f"{channel['name']}, {channel['url']}")
    
    # 組合輸出內容
    lines = []
    for cat, entries in results.items():
        lines.append(cat)  # 輸出分類名稱
        lines.extend(entries)
        lines.append("")  # 空行分隔不同分類
    
    file_content = "\n".join(lines)
    with open("live_streams.txt", "w", encoding="utf-8") as f:
        f.write(file_content)
    print("已更新 live_streams.txt")

if __name__ == '__main__':
    update_live_streams()

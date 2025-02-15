import os
from googleapiclient.discovery import build

# 從環境變數中取得 API 金鑰（建議在 GitHub Actions 中設置）
api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    raise Exception("請設定 YOUTUBE_API_KEY 環境變數。")

# 建立 YouTube API 客戶端
youtube = build('youtube', 'v3', developerKey=api_key)

# 頻道資訊設定，包含名稱、頻道網址（使用 handle 格式），以及您自訂的分類
# 請依需求自行調整分類文字 (這裡範例中將分類內容寫成 "台灣,追劇"、"台灣,娛樂"，您也可以根據需要設定 [台灣, #genre#]、[娛樂, #genre#]、[追劇, #genre#]、[國外, #genre#])
channels = [
    {"name": "GTV Drama", "url": "https://www.youtube.com/@gtv-drama", "category": "[台灣,追劇]"},
    {"name": "中天電視CtiTv", "url": "https://www.youtube.com/@%E4%B8%AD%E5%A4%A9%E9%9B%BB%E8%A6%96CtiTv", "category": "[台灣,娛樂]"},
    {"name": "newsebc", "url": "https://www.youtube.com/@newsebc", "category": "[台灣,娛樂]"}
]

def get_channel_id_from_url(url):
    """
    根據頻道網址（格式為 https://www.youtube.com/@xxx）取得頻道ID
    透過搜尋 handle (xxx) 得到頻道 ID
    """
    handle = url.rstrip('/').split('/')[-1]
    try:
        search_request = youtube.search().list(
            part='snippet',
            q=handle,
            type='channel',
            maxResults=1
        )
        search_response = search_request.execute()
        items = search_response.get("items", [])
        if items:
            return items[0]["id"]["channelId"]
    except Exception as e:
        print(f"取得頻道ID失敗: {e}")
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
    檢查所有頻道是否有正在直播，依分類整理輸出成文字檔
    輸出格式:
      分類區塊 (例如 [台灣,追劇])
      每列一個項目，格式為「名稱,網址」
    """
    results = {}  # 用分類作 key 儲存直播中的頻道資料
    for channel in channels:
        channel_id = get_channel_id_from_url(channel["url"])
        if not channel_id:
            print(f"無法取得 {channel['name']} 的頻道ID，跳過。")
            continue
        if is_live(channel_id):
            cat = channel["category"]
            if cat not in results:
                results[cat] = []
            results[cat].append(f"{channel['name']}, {channel['url']}")
    
    # 組合文字檔內容
    lines = []
    for cat, entries in results.items():
        lines.append(cat)  # 輸出分類名稱
        lines.extend(entries)
        lines.append("")  # 空行分隔各分類
    
    file_content = "\n".join(lines)
    with open("live_streams.txt", "w", encoding="utf-8") as f:
        f.write(file_content)
    print("已更新 live_streams.txt")

if __name__ == '__main__':
    update_live_streams()

import os
from googleapiclient.discovery import build

# 讀取 API 金鑰，請於 GitHub Secrets 中設定 YOUTUBE_API_KEY
api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    raise Exception("請設定 YOUTUBE_API_KEY 環境變數。")

# 建立 YouTube API 客戶端
youtube = build('youtube', 'v3', developerKey=api_key)

# 設定各頻道資訊：名稱、頻道網址（以 handle 表示）與分類
# 請依實際需求調整分類（台灣、娛樂、追劇、國外）
channels = [
    {"name": "GTV Drama", "url": "https://www.youtube.com/@gtv-drama", "category": "追劇"},
    {"name": "中天電視CtiTv", "url": "https://www.youtube.com/@%E4%B8%AD%E5%A4%A9%E9%9B%BB%E8%A6%96CtiTv", "category": "娛樂"},
    {"name": "newsebc", "url": "https://www.youtube.com/@newsebc", "category": "台灣"}
]

def get_channel_id_from_url(url):
    """
    依頻道網址（格式： https://www.youtube.com/@xxx）取得頻道 ID  
    ※ 由於 YouTube API 沒有直接以 handle 查詢頻道 ID，故以搜尋方式取得
    """
    handle = url.rstrip('/').split('/')[-1]
    try:
        req = youtube.search().list(
            part='snippet',
            q=handle,
            type='channel',
            maxResults=1
        )
        resp = req.execute()
        items = resp.get("items", [])
        if items:
            return items[0]["id"]["channelId"]
    except Exception as e:
        print(f"取得 {url} 的頻道 ID 失敗：{e}")
    return None

def is_live(channel_id):
    """
    檢查指定頻道 ID 是否有正在直播的影片
    """
    try:
        req = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            eventType='live',
            type='video',
            maxResults=1
        )
        resp = req.execute()
        return len(resp.get("items", [])) > 0
    except Exception as e:
        print(f"檢查頻道 {channel_id} 是否直播失敗：{e}")
        return False

def update_live_streams():
    """
    檢查各頻道是否有直播，並依分類整理輸出成文字檔  
    輸出格式：  
      分類標題  
      每行：名稱,網址  
    沒有直播的頻道不加入結果
    """
    results = {}  # key 為分類，value 為該分類下的直播項目（格式： 名稱,網址）
    for channel in channels:
        cid = get_channel_id_from_url(channel["url"])
        if not cid:
            print(f"無法取得 {channel['name']} 的頻道 ID，跳過。")
            continue
        if is_live(cid):
            cat = channel["category"]
            results.setdefault(cat, []).append(f"{channel['name']}, {channel['url']}")
    
    # 組合輸出內容
    lines = []
    for cat, items in results.items():
        lines.append(cat)
        lines.extend(items)
        lines.append("")  # 空行區隔不同分類
    
    output = "\n".join(lines)
    with open("live_streams.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print("已更新 live_streams.txt")

if __name__ == '__main__':
    update_live_streams()

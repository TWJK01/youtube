import os
import time
from googleapiclient.discovery import build

# 设置YouTube API密钥
api_key = 'YOUR_YOUTUBE_API_KEY'

# 创建YouTube API客户端
youtube = build('youtube', 'v3', developerKey=api_key)

# 频道信息
channels = [
    {"name": "GTV Drama", "url": "https://www.youtube.com/@gtv-drama", "category": "台灣, 追劇"},
    {"name": "中天電視CtiTv", "url": "https://www.youtube.com/@%E4%B8%AD%E5%A4%A9%E9%9B%BB%E8%A6%96CtiTv", "category": "台灣, 娛樂"},
    {"name": "newsebc", "url": "https://www.youtube.com/@newsebc", "category": "台灣, 娛樂"}
]

# 获取频道ID
def get_channel_id(channel_url):
    channel_id = channel_url.split('@')[-1]
    return channel_id

# 检查频道是否正在直播
def is_live(channel_id):
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        eventType='live',
        type='video',
        maxResults=1
    )
    response = request.execute()
    return len(response['items']) > 0

# 更新直播信息
def update_live_streams():
    live_streams = []
    for channel in channels:
        channel_id = get_channel_id(channel['url'])
        if is_live(channel_id):
            live_streams.append(f"[{channel['name']}, {channel['url']}]")
    
    # 保存到文本文件
    file_content = "\n".join(live_streams)
    with open("live_streams.txt", "w", encoding="utf-8") as file:
        file.write(file_content)

# 每两小时更新一次
while True:
    update_live_streams()
    time.sleep(7200)  # 休眠两小时
 

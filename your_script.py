import requests
from bs4 import BeautifulSoup

# 定义分类和对应的频道 URL
categories = {
    "台灣": [
        {"name": "中天新聞", "url": "https://www.youtube.com/@中天新聞CtiNews/streams"},
        {"name": "TVBS 频道", "url": "https://www.youtube.com/@tvbschannel/streams"},
        {"name": "東森新聞", "url": "https://www.youtube.com/@newsebc/streams"}
    ],
    "綜藝": [
        {"name": "Chop Chop Show", "url": "https://www.youtube.com/@chopchopshow/streams"}
    ]
}

# 存放直播信息
live_streams = []

# 遍历每个分类
for category, channels in categories.items():
    for channel in channels:
        response = requests.get(channel["url"])
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找直播标识
            live_tag = soup.find('span', string='LIVE')
            if live_tag:
                # 找到包含直播的父元素
                parent = live_tag.find_parent('a', href=True)
                if parent:
                    link = f"https://www.youtube.com{parent['href']}"
                    live_streams.append(f"{channel['name']},{link}")

# 将结果写入文件
if live_streams:
    with open('live_streams.txt', 'w', encoding='utf-8') as file:
        for stream in live_streams:
            file.write(f"{stream}\n")

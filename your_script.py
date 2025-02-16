import requests
from bs4 import BeautifulSoup

# 定义分类与对应的 YouTube streams 网页
categories = {
    "台灣": [
        "https://www.youtube.com/@中天新聞CtiNews/streams",
        "https://www.youtube.com/@tvbschannel/streams"
    ],
    "電影綜藝": [
        "https://www.youtube.com/@chopchopshow/streams"
    ]
}

# 存放所有抓到的直播影片 (格式：(直播名稱, 影片網址))
live_streams = []

# 逐分类读取每个网址
for genre, url_list in categories.items():
    for url in url_list:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找所有 <span> 元素，若内含 "LIVE" 或 "正在直播" 则视为直播标记
            spans = soup.find_all("span")
            for span in spans:
                text = span.get_text(strip=True)
                if "LIVE" in text.upper() or "正在直播" in text:
                    # 往上找最近的 <a> 元素，取得影片连结与名称
                    parent_anchor = span.find_parent("a")
                    if parent_anchor and parent_anchor.has_attr("href"):
                        video_url = parent_anchor["href"]
                        # 若为相对路径补上前缀
                        if not video_url.startswith("https://www.youtube.com"):
                            video_url = "https://www.youtube.com" + video_url
                        # 取得影片名称（优先使用 title 属性）
                        title = parent_anchor.get("title") or parent_anchor.get_text(strip=True) or "No Title"
                        # 避免重复加入
                        if (title, video_url) not in live_streams:
                            live_streams.append((title, video_url))

# 将抓取结果输出到文字档（每行格式：直播名称,网址）
with open("live_streams.txt", "w", encoding="utf-8") as f:
    for title, video_url in live_streams:
        f.write(f"{title},{video_url}\n")

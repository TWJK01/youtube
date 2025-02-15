import requests
from bs4 import BeautifulSoup

# 目標 YouTube 頻道
CHANNELS = {
    "GTV Drama": "https://www.youtube.com/@gtv-drama",
    "CTiTV": "https://www.youtube.com/@%E4%B8%AD%E5%A4%A9%E9%9B%BB%E8%A6%96CtiTv",
    "EBC News": "https://www.youtube.com/@newsebc",
}

# 分類
CATEGORY_MAPPING = {
    "GTV Drama": "追劇",
    "CTiTV": "台灣",
    "EBC News": "娛樂",
}

def get_live_video_url(channel_url):
    """取得頻道當前直播的網址"""
    response = requests.get(channel_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有 <a> 連結
    links = soup.find_all("a", href=True)
    for link in links:
        if "watch?v=" in link["href"]:
            return f"https://www.youtube.com{link['href']}"
    return None  # 無直播

def main():
    live_streams = {"台灣": [], "娛樂": [], "追劇": [], "國外": []}

    for name, url in CHANNELS.items():
        live_url = get_live_video_url(url)
        if live_url:
            category = CATEGORY_MAPPING.get(name, "國外")
            live_streams[category].append(f"{name}, {live_url}")

    # 輸出到文字檔
    with open("live_streams.txt", "w", encoding="utf-8") as f:
        for category, streams in live_streams.items():
            if streams:
                f.write(f"{category}:\n")
                f.write("\n".join(streams) + "\n\n")

if __name__ == "__main__":
    main()

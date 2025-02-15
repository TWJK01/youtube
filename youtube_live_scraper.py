import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 需要爬取的 YouTube 頻道網址
CHANNEL_URLS = {
    "gtv-drama": "https://www.youtube.com/@gtv-drama",
    "cti-tv": "https://www.youtube.com/@%E4%B8%AD%E5%A4%A9%E9%9B%BB%E8%A6%96CtiTv",
    "newsebc": "https://www.youtube.com/@newsebc"
}

# 分類標籤
CATEGORIES = {
    "台灣": ["gtv-drama", "cti-tv", "newsebc"],
    "娛樂": [],
    "追劇": ["gtv-drama"],
    "國外": []
}

OUTPUT_FILE = "youtube_live_streams.txt"

# 設置 Selenium 選項（無頭模式）
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")


def get_live_streams(channel_url):
    """使用 Selenium 爬取頻道的直播影片"""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(channel_url + "/live")
        time.sleep(3)  # 等待頁面加載

        # 取得頁面內容
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 查找直播影片的連結
        live_streams = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "watch?v=" in href:
                title = link.get_text(strip=True)
                full_url = f"https://www.youtube.com{href}"
                if full_url not in live_streams:
                    live_streams.append(f"{title}: {full_url}")

        return live_streams

    finally:
        driver.quit()


def classify_and_save():
    """分類並存儲 YouTube 直播連結"""
    categorized_streams = {key: [] for key in CATEGORIES}

    for name, url in CHANNEL_URLS.items():
        streams = get_live_streams(url)
        if streams:
            for category, channels in CATEGORIES.items():
                if name in channels:
                    categorized_streams[category].extend(streams)

    # 只保留有直播的分類
    categorized_streams = {k: v for k, v in categorized_streams.items() if v}

    # 寫入文字檔
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for category, streams in categorized_streams.items():
            f.write(f"【{category}】\n")
            f.write("\n".join(streams))
            f.write("\n\n")

    print(f"✅ 直播數據已更新：{OUTPUT_FILE}")


if __name__ == "__main__":
    classify_and_save()

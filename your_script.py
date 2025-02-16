import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 定義分類與對應的 YouTube streams 網頁
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

# 設定 Chromium 無頭模式
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# 指定 Chromium 執行檔位置
chrome_options.binary_location = "/usr/bin/chromium-browser"

# 初始化 WebDriver
driver = webdriver.Chrome(options=chrome_options)

# 逐分類讀取每個網址
for genre, url_list in categories.items():
    for url in url_list:
        driver.get(url)
        # 等待網頁載入，根據網速調整等待秒數
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        # 搜尋所有 <span> 元素，若內含 "LIVE" 或 "正在直播" 則視為直播標記
        spans = soup.find_all("span")
        for span in spans:
            text = span.get_text(strip=True)
            if "LIVE" in text.upper() or "正在直播" in text:
                # 往上找最近的 <a> 元素，取得影片連結與名稱
                parent_anchor = span.find_parent("a")
                if parent_anchor and parent_anchor.has_attr("href"):
                    video_url = parent_anchor["href"]
                    # 若為相對路徑補上前綴
                    if not video_url.startswith("https://www.youtube.com"):
                        video_url = "https://www.youtube.com" + video_url
                    # 取得影片名稱（優先使用 title 屬性）
                    title = parent_anchor.get("title") or parent_anchor.get_text(strip=True) or "No Title"
                    # 避免重複加入
                    if (title, video_url) not in live_streams:
                        live_streams.append((title, video_url))

driver.quit()

# 將抓取結果輸出到文字檔（每行格式：直播名稱,網址）
with open("output.txt", "w", encoding="utf-8") as f:
    for title, video_url in live_streams:
        f.write(f"{title},{video_url}\n")

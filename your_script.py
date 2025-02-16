import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 定義分類與對應的 YouTube streams 頁面
categories = {
    "台灣": [
        "https://www.youtube.com/@中天新聞CtiNews/streams",
        "https://www.youtube.com/@tvbschannel/streams"
    ],
    "電影綜藝": [
        "https://www.youtube.com/@chopchopshow/streams"
    ]
}

# 存放所有抓到的直播影片 (格式：(標題, 影片網址))
live_streams = []

# 設定無頭 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 初始化 Chrome WebDriver（請確保 GitHub Actions Runner 有安裝 Chrome 與 chromedriver）
driver = webdriver.Chrome(options=chrome_options)

# 依分類與網址依序處理
for category, url_list in categories.items():
    for url in url_list:
        driver.get(url)
        # 等待網頁載入，依網速可調整等待秒數
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # 搜尋所有 <span> 標籤，檢查是否包含 "LIVE" 或 "正在直播"
        spans = soup.find_all("span")
        for span in spans:
            text = span.get_text(strip=True)
            if "LIVE" in text.upper() or "正在直播" in text:
                # 往上找包含影片連結的 <a> 元素
                parent_anchor = span.find_parent("a")
                if parent_anchor and parent_anchor.has_attr("href"):
                    video_url = parent_anchor["href"]
                    if not video_url.startswith("https://www.youtube.com"):
                        video_url = "https://www.youtube.com" + video_url
                    # 優先從 title 屬性取得影片名稱，否則使用連結文字
                    title = parent_anchor.get("title") or parent_anchor.get_text(strip=True) or "No Title"
                    # 加入清單（重覆的可利用 set() 去除）
                    live_streams.append((title, video_url))

driver.quit()

# 排除重複項目
live_streams = list(set(live_streams))

# 輸出結果到文字檔，每行格式為「名稱,網址」
with open("output.txt", "w", encoding="utf-8") as f:
    for title, video_url in live_streams:
        f.write(f"{title},{video_url}\n")

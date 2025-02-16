import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 要抓取的 YouTube streams 頁面網址列表
urls = [
    "https://www.youtube.com/@中天新聞CtiNews/streams",
    "https://www.youtube.com/@tvbschannel/streams"
]

# 存放抓到的直播影片 (格式：(標題, 影片網址))
live_streams = []

# 設定無頭 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 初始化 Chrome WebDriver
driver = webdriver.Chrome(options=chrome_options)

# 依序處理每個頻道頁面
for url in urls:
    driver.get(url)
    # 等待網頁載入，根據網速可調整秒數
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    # 解析頁面中所有 <span> 標籤，尋找包含 "LIVE" 或 "正在直播" 的文字
    spans = soup.find_all("span")
    for span in spans:
        text = span.get_text(strip=True)
        if "LIVE" in text.upper() or "正在直播" in text:
            # 往上查找包含影片連結的 <a> 標籤
            parent_anchor = span.find_parent("a")
            if parent_anchor and parent_anchor.has_attr("href"):
                video_url = parent_anchor["href"]
                if not video_url.startswith("https://www.youtube.com"):
                    video_url = "https://www.youtube.com" + video_url
                # 嘗試從 title 屬性取得影片名稱，若無則以連結內文字補充
                title = parent_anchor.get("title") or parent_anchor.get_text(strip=True) or "No Title"
                live_streams.append((title, video_url))

driver.quit()

# 排除重複項目
live_streams = list(set(live_streams))

# 輸出結果至文字檔 (每行格式：名稱,網址)
with open("output.txt", "w", encoding="utf-8") as f:
    for title, video_url in live_streams:
        f.write(f"{title},{video_url}\n")

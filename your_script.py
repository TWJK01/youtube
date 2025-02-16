import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 設定無頭 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 初始化 WebDriver (請確認 GitHub Actions runner 有安裝 Chrome 及 chromedriver)
driver = webdriver.Chrome(options=chrome_options)

# 目標 URL：中天新聞的 streams 頁面
url = "https://www.youtube.com/@中天新聞CtiNews/streams"
driver.get(url)

# 等待頁面載入 (可依網速調整等待秒數)
time.sleep(5)

# 取得頁面 HTML
html = driver.page_source
driver.quit()

# 解析 HTML
soup = BeautifulSoup(html, 'html.parser')
live_videos = []

# 解析邏輯：
# 由於 YouTube 頁面中，直播影片通常會有特殊標示（例如顯示 "LIVE" 或「正在直播」），
# 這裡以尋找含有 "LIVE" 或 "正在直播" 的元素為例。
# 注意：實際結構可能因 YouTube 更新而不同，可能需要調整搜尋方式。

# 尋找所有可能包含直播標示的 span 元素
badges = soup.find_all("span")
for badge in badges:
    text = badge.get_text(strip=True)
    if "LIVE" in text.upper() or "正在直播" in text:
        # 往上找包含影片連結的 <a> 元素
        a_tag = badge.find_parent("a")
        if a_tag and a_tag.has_attr("href"):
            video_url = "https://www.youtube.com" + a_tag["href"]
            # 嘗試取得影片標題，可由 a_tag 的 title 屬性或其內部文字取得
            title = a_tag.get("title") or a_tag.get_text(strip=True) or "No Title"
            # 避免重覆加入
            if (title, video_url) not in live_videos:
                live_videos.append((title, video_url))

# 輸出結果至文字檔，若無直播則清空檔案
if live_videos:
    with open("output.txt", "w", encoding="utf-8") as f:
        for title, video_url in live_videos:
            f.write(f"{title},{video_url}\n")
else:
    # 沒有直播就清空檔案（也可選擇不建立檔案）
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write("")

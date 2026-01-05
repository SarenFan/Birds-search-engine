from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json

THREAD_URL = "https://voz.vn/t/chung-ket-the-gioi-2025-vuong-mien-vinh-quang-se-danh-cho-ai.1152473/"

def crawl_voz_raw(limit_posts=20):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(THREAD_URL)
    time.sleep(5)  # chờ JS render

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    posts = soup.select("article.message")[:limit_posts]

    data = []

    for post in posts:
        post_id = post.get("data-content", "")
        user = post.select_one(".message-name")
        content = post.select_one(".message-body")

        data.append({
            "post_id": post_id,
            "user": user.text.strip() if user else None,
            "raw_html": str(content) if content else None
        })

    return data

if __name__ == "__main__":
    print("Crawling Voz (raw, with images/icons/tables)...")
    posts = crawl_voz_raw(limit_posts=20)

    with open("voz_raw_posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(posts)} posts to voz_raw_posts.json")

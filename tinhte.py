from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import sys
import io
import re

# Fix encoding cho Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

THREAD_URL = "https://tinhte.vn/thread/co-nen-mua-iphone-air-khong-hay-lay-iphone-17-pro.4087754/"


def crawl_tinhte(limit_posts=20):
    print("Dang crawl Tinhte voi Selenium...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get(THREAD_URL)
        print("Dang tai trang va cho load...")

        # Doi trang load
        time.sleep(8)

        # Scroll xuong de load comments
        for i in range(3):
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Scroll len lai
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Luu HTML de debug
        html_content = driver.page_source
        with open("tinhte_selenium.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Da luu HTML vao tinhte_selenium.html")

        soup = BeautifulSoup(html_content, "html.parser")

        # Thu TIM TAT CA cac dang selector co the
        print("\n=== DANG TIM KIEM COMMENTS ===")

        # Cach 1: Tim theo link profile
        profile_links = soup.find_all("a", href=re.compile(r'/profile/'))
        print(f"Tim thay {len(profile_links)} profile links")

        data = []
        processed = set()

        for link in profile_links[:limit_posts * 3]:  # Lay nhieu hon de loc
            username = link.get_text(strip=True)

            if not username or username in processed or len(username) < 3:
                continue

            # Tim parent container gan nhat
            parent = link.find_parent("div")
            if not parent:
                continue

            # Tim sibling hoac parent co chua noi dung text dai
            # Duyet len cac cap parent
            content_text = ""
            current = parent

            for _ in range(5):  # Thu 5 cap parent
                if current is None:
                    break

                # Lay tat ca text trong container
                text = current.get_text(separator="\n", strip=True)

                # Neu co text dai hon, lay no
                if len(text) > len(content_text):
                    content_text = text

                current = current.find_parent()

            if not content_text:
                continue

            # Tach content thanh cac dong
            lines = content_text.split('\n')

            # Tim dong dau tien SAU username va khong phai metadata
            content_lines = []
            found_user = False

            skip_words = ['GÀ', 'ĐẠI BÀNG', 'Báo xấu', 'ngày', 'giờ', 'Thích',
                          'Không thích', 'Share', 'FactTinhte', 'đã nói', 'said']

            for line in lines:
                line = line.strip()

                if not line:
                    continue

                # Neu gap username, bat dau ghi nhan
                if username in line:
                    found_user = True
                    continue

                # Sau khi gap username
                if found_user:
                    # Bo qua metadata
                    if any(word in line for word in skip_words):
                        continue

                    # Bo qua so don doc
                    if re.match(r'^\d+$', line):
                        continue

                    # Bo qua dong ngan (< 10 ky tu)
                    if len(line) < 10:
                        continue

                    # Day la noi dung
                    content_lines.append(line)

                    # Chi lay toi da 3 dong
                    if len(content_lines) >= 3:
                        break

            # Gop noi dung
            content = ' '.join(content_lines).strip()

            # Lam sach
            content = re.sub(r'@\w+', '', content)
            content = re.sub(r'[↑→←↓]', '', content)
            content = re.sub(r'\s+', ' ', content)

            # Chi them neu co noi dung hop le
            if content and len(content) > 15:
                processed.add(username)

                data.append({
                    "index": len(data) + 1,
                    "username": username,
                    "content": content
                })

                print("=" * 60)
                print(f"Post #{len(data)} | {username}")
                print(content[:200])

                if len(data) >= limit_posts:
                    break

        return data

    except Exception as e:
        print(f"Loi: {e}")
        import traceback
        traceback.print_exc()
        return []

    finally:
        driver.quit()


if __name__ == "__main__":
    print("Bat dau crawl Tinhte.vn...")
    posts = crawl_tinhte(limit_posts=20)

    if posts:
        with open("tinhte_posts.json", "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"\nDa luu {len(posts)} posts vao tinhte_posts.json")
    else:
        print("\nKhong crawl duoc du lieu!")
        print("Hay kiem tra file tinhte_selenium.html")

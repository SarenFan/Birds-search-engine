import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import json
from selenium.common.exceptions import TimeoutException

THREAD_URL = "https://voz.vn/t/chung-ket-the-gioi-2025-vuong-mien-vinh-quang-se-danh-cho-ai.1152473/"

def crawl_voz_raw(limit_posts=20, limit=20, max_retries=2, use_headless=False):
    """
    Crawl Voz.vn comments using undetected-chromedriver

    Args:
        limit_posts: Number of posts (backward compatibility)
        limit: Number of posts to crawl
        max_retries: Number of retries if failed
    """
    # Support both parameter names for compatibility
    actual_limit = limit if limit != 20 else limit_posts

    for attempt in range(max_retries + 1):
        driver = None
        try:
            print(f"\n[Attempt {attempt + 1}/{max_retries + 1}]")
            print("[1] Setting up undetected Chrome for Voz...")

            options = uc.ChromeOptions()
            if use_headless:
                options.add_argument('--headless=new')
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--window-size=1920,1080")

            print("[2] Launching Chrome...")
            driver = uc.Chrome(options=options, version_main=143)

            print("[3] Opening Voz page...")
            driver.set_page_load_timeout(90)

            try:
                driver.get(THREAD_URL)
            except TimeoutException:
                print("    ⚠ Page load timeout, checking partial content...")

            print("[4] Waiting for content to load (20 seconds)...")
            time.sleep(20)  # Longer wait for Voz

            # Scroll to load more
            print("[5] Scrolling to load content...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            print("[6] Parsing HTML...")
            soup = BeautifulSoup(driver.page_source, "html.parser")


            # Save debug HTML
            with open('voz_debug.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("    Saved HTML to voz_debug.html")

            # Try multiple selectors
            posts = soup.select("article.message")
            if len(posts) == 0:
                print("    Trying selector .message-main...")
                posts = soup.select(".message-main")
            if len(posts) == 0:
                print("    Trying selector [data-content]...")
                posts = soup.select("[data-content]")

            print(f"[7] Found {len(posts)} posts")

            if len(posts) == 0:
                if attempt < max_retries:
                    print("    No posts found, retrying...")
                    time.sleep(5)
                    continue
                else:
                    print("    ⚠ No posts found after all retries")
                    return []

            posts = posts[:actual_limit]
            data = []

            for i, post in enumerate(posts, start=1):
                post_id = post.get("data-content", "")
                user_elem = post.select_one(".message-name, .username")
                username = user_elem.text.strip() if user_elem else "UNKNOWN"

                content_elem = post.select_one(".message-body, .bbWrapper")
                # Extract plain text instead of HTML
                content = content_elem.get_text("\n", strip=True) if content_elem else ""

                data.append({
                    "index": i,
                    "post_id": post_id,
                    "username": username,
                    "user": username,  # backward compatibility
                    "content": content,
                    "raw_html": str(content_elem) if content_elem else None
                })

            print(f"[8] ✓ Successfully crawled {len(data)} posts")
            return data

        except Exception as e:
            print(f"    ERROR: {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries:
                print(f"    Retrying in 10 seconds...")
                time.sleep(10)
                continue
            else:
                return []
        finally:
            if driver:
                print("[9] Closing driver...")
                try:
                    driver.quit()
                except:
                    pass

    return []

if __name__ == "__main__":
    print("Crawling Voz (raw, with images/icons/tables)...")
    posts = crawl_voz_raw(limit_posts=20)

    with open("voz_raw_posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(posts)} posts to voz_raw_posts.json")

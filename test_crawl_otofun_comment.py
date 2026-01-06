import requests
from bs4 import BeautifulSoup

THREAD_URL = "https://www.otofun.net/threads/nga-mu-cach-nguoi-duc-nhuong-duong-cho-xe-cuu-hoa.1952879/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def crawl_otofun(limit=20):
    print("Crawling Otofun thread (raw)...")
    resp = requests.get(THREAD_URL, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    posts = soup.select("article.message.message--post")
    print(f"Found {len(posts)} posts")

    results = []

    for i, post in enumerate(posts[:limit], start=1):
        user_tag = post.select_one(".message-name a")
        username = user_tag.get_text(strip=True) if user_tag else "UNKNOWN"

        content_block = post.select_one(".bbWrapper")
        content = content_block.get_text("\n", strip=True) if content_block else ""

        results.append({
            "index": i,
            "username": username,
            "content": content
        })

        print("=" * 60)
        print(f"Post #{i} | {username}")
        print(content[:300])

    return results


if __name__ == "__main__":
    crawl_otofun(limit=20)

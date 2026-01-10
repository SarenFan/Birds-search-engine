"""
Debug script to analyze page structure
"""
from src.crawler.selenium_utils import SeleniumCrawler
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)


def analyze_voz():
    """Analyze Voz page structure"""
    url = 'https://voz.vn/f/tam-su-tam-tinh.17/'

    print(f"\n🔍 Analyzing: {url}\n")

    with SeleniumCrawler(headless=False) as crawler:
        html = crawler.get_page(url)

        if html:
            # Save for inspection
            with open('debug_voz_page.html', 'w', encoding='utf-8') as f:
                f.write(html)

            soup = BeautifulSoup(html, 'lxml')

            # Check for different possible selectors
            selectors_to_try = [
                ('a.PreviewTooltip', 'PreviewTooltip links'),
                ('a[data-tp-primary="on"]', 'data-tp-primary links'),
                ('div.structItem-title a', 'structItem-title links'),
                ('a[href*="/t/"]', 'Links containing /t/'),
                ('article.structItem', 'structItem articles'),
                ('div.structItem', 'structItem divs'),
            ]

            print("📊 Selector Analysis:")
            print("="*80)

            for selector, description in selectors_to_try:
                elements = soup.select(selector)
                print(f"{description:40} found: {len(elements):3}")
                if elements and len(elements) > 0:
                    # Show first example
                    first = elements[0]
                    print(f"  Example: {str(first)[:100]}...")

            print("\n" + "="*80)

            # Look for any links
            all_links = soup.find_all('a', href=True)
            thread_links = [a for a in all_links if '/t/' in a.get('href', '')]
            print(f"\n📌 Total links on page: {len(all_links)}")
            print(f"📌 Links with '/t/' pattern: {len(thread_links)}")

            if thread_links:
                print(f"\n✓ Sample thread links found:")
                for link in thread_links[:3]:
                    print(f"  - {link.get('href')}")

            print(f"\n💾 Full HTML saved to: debug_voz_page.html")
            print(f"📏 Page size: {len(html)} bytes\n")
        else:
            print("❌ Failed to load page")


if __name__ == '__main__':
    analyze_voz()

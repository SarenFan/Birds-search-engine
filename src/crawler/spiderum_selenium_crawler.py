"""
Improved Spiderum Crawler with Selenium
"""
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import jsonlines
import logging
from datetime import datetime
import os

from src.crawler.selenium_utils import SeleniumCrawler
from src.crawler.utils import (
    calculate_hash, is_valid_document,
    clean_text, save_checkpoint, load_checkpoint
)
from src.crawler.parser import remove_html_tags, clean_vietnamese_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedSpiderumCrawler:
    """Improved Spiderum crawler with Selenium"""

    def __init__(self, output_file: str = 'data_sample/spiderum_selenium_data.jsonl',
                 checkpoint_file: str = 'data_sample/spiderum_selenium_checkpoint.json',
                 max_docs: int = 100,
                 headless: bool = True):
        self.base_url = 'https://spiderum.com'
        self.categories = [
            f'{self.base_url}/chuyen-muc/tam-su',
            f'{self.base_url}/chuyen-muc/cong-nghe',
        ]
        self.output_file = output_file
        self.checkpoint_file = checkpoint_file
        self.max_docs = max_docs
        self.headless = headless
        self.collected_docs = []
        self.seen_hashes = set()

        checkpoint = load_checkpoint(checkpoint_file)
        self.seen_hashes = set(checkpoint.get('seen_hashes', []))

    def parse_article(self, html: str, article_url: str) -> list:
        """Parse article and extract content"""
        soup = BeautifulSoup(html, 'lxml')
        documents = []

        try:
            # Get article title
            title_elem = soup.find('h1')
            article_title = title_elem.text.strip() if title_elem else 'Unknown'

            # Get author
            author_elem = soup.find('a', class_='author-name')
            if not author_elem:
                author_elem = soup.find('span', class_='author')
            author = author_elem.text.strip() if author_elem else 'Anonymous'

            # Get article content
            content_elem = soup.find('div', class_='post-content')
            if not content_elem:
                content_elem = soup.find('article')
            if not content_elem:
                # Try finding by id
                content_elem = soup.find('div', {'id': 'content'})

            if content_elem:
                content_html = str(content_elem)
                content_text = remove_html_tags(content_html)
                content_text = clean_vietnamese_text(content_text)
                content_text = clean_text(content_text)

                if is_valid_document(content_text, min_words=50):
                    doc_hash = calculate_hash(content_text)

                    if doc_hash not in self.seen_hashes:
                        document = {
                            'id': doc_hash,
                            'source': 'spiderum_selenium',
                            'url': article_url,
                            'title': article_title,
                            'author': author,
                            'content': content_text,
                            'type': 'article',
                            'word_count': len(content_text.split()),
                            'crawled_at': datetime.now().isoformat()
                        }
                        documents.append(document)
                        self.seen_hashes.add(doc_hash)

        except Exception as e:
            logger.error(f"Error parsing article {article_url}: {e}")

        return documents

    def crawl_category(self, crawler: SeleniumCrawler, category_url: str, max_scrolls: int = 5):
        """Crawl a specific category (Spiderum uses infinite scroll)"""
        logger.info(f"Crawling {category_url}...")

        html = crawler.get_page(category_url)
        if not html:
            logger.warning(f"Failed to load {category_url}")
            return

        # Scroll to load more articles
        for scroll in range(max_scrolls):
            if len(self.collected_docs) >= self.max_docs:
                break

            logger.info(f"Scroll {scroll + 1}/{max_scrolls}")
            crawler.scroll_page(3)
            crawler.human_like_delay(2, 4)

        # Get final page source
        html = crawler.driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # Find article links
        article_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/bai-dang/' in href:
                if href.startswith('/'):
                    href = self.base_url + href
                if href not in article_links:
                    article_links.append(href)

        logger.info(f"Found {len(article_links)} articles")

        # Process articles
        for i, article_url in enumerate(article_links):
            if len(self.collected_docs) >= self.max_docs:
                break

            logger.info(f"Processing article {i+1}/{len(article_links)}")

            article_html = crawler.get_page(article_url)
            if article_html:
                documents = self.parse_article(article_html, article_url)
                self.collected_docs.extend(documents)
                logger.info(f"Collected {len(documents)} docs. Total: {len(self.collected_docs)}")

            crawler.human_like_delay(2, 4)

    def save_data(self):
        """Save collected documents"""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        with jsonlines.open(self.output_file, mode='w') as writer:
            for doc in self.collected_docs:
                writer.write(doc)

        logger.info(f"Saved {len(self.collected_docs)} documents to {self.output_file}")

    def run(self):
        """Main crawling process"""
        start_time = datetime.now()
        logger.info(f"Starting Spiderum Selenium crawler (target: {self.max_docs} docs)...")

        with SeleniumCrawler(headless=self.headless) as crawler:
            for category_url in self.categories:
                if len(self.collected_docs) >= self.max_docs:
                    break
                self.crawl_category(crawler, category_url, max_scrolls=10)

        self.save_data()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"\n{'='*60}")
        logger.info(f"Spiderum Selenium Crawling Summary:")
        logger.info(f"Documents collected: {len(self.collected_docs)}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Speed: {len(self.collected_docs)/duration:.2f} docs/second")
        logger.info(f"{'='*60}\n")

        return {
            'source': 'spiderum_selenium',
            'docs_collected': len(self.collected_docs),
            'duration': duration,
            'docs_per_second': len(self.collected_docs) / duration if duration > 0 else 0
        }


def main():
    crawler = ImprovedSpiderumCrawler(max_docs=25, headless=False)
    stats = crawler.run()
    print(f"\nStats: {stats}")


if __name__ == '__main__':
    main()

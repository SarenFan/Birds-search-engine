"""
Improved TinhTe Forum Crawler with Selenium
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


class ImprovedTinhTeCrawler:
    """Improved TinhTe crawler with Selenium"""

    def __init__(self, output_file: str = 'data_sample/tinhte_selenium_data.jsonl',
                 checkpoint_file: str = 'data_sample/tinhte_selenium_checkpoint.json',
                 max_docs: int = 100,
                 headless: bool = True):
        self.base_url = 'https://tinhte.vn'
        self.forums = [
            f'{self.base_url}/forums/tin-tuc-cong-nghe.65/',
            f'{self.base_url}/forums/doi-song-so.194/',
        ]
        self.output_file = output_file
        self.checkpoint_file = checkpoint_file
        self.max_docs = max_docs
        self.headless = headless
        self.collected_docs = []
        self.seen_hashes = set()

        checkpoint = load_checkpoint(checkpoint_file)
        self.seen_hashes = set(checkpoint.get('seen_hashes', []))

    def parse_thread_content(self, html: str, thread_url: str) -> list:
        """Parse thread and extract posts"""
        soup = BeautifulSoup(html, 'lxml')
        documents = []

        # Get thread title
        title_elem = soup.find('h1', class_='p-title-value')
        if not title_elem:
            title_elem = soup.find('h1')
        thread_title = title_elem.text.strip() if title_elem else 'Unknown'

        # Find all posts
        posts = soup.find_all('article', class_='message')

        for post in posts:
            try:
                # Extract author
                author_elem = post.find('a', class_='username')
                if not author_elem:
                    author_elem = post.find('h4', class_='message-name')
                author = author_elem.text.strip() if author_elem else 'Anonymous'

                # Extract timestamp
                time_elem = post.find('time')
                timestamp = time_elem.get('datetime', '') if time_elem else ''

                # Extract content
                content_elem = post.find('div', class_='message-body')
                if not content_elem:
                    content_elem = post.find('div', class_='bbWrapper')

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
                                'source': 'tinhte_selenium',
                                'url': thread_url,
                                'thread_title': thread_title,
                                'author': author,
                                'content': content_text,
                                'timestamp': timestamp,
                                'word_count': len(content_text.split()),
                                'crawled_at': datetime.now().isoformat()
                            }
                            documents.append(document)
                            self.seen_hashes.add(doc_hash)

            except Exception as e:
                logger.error(f"Error parsing post: {e}")
                continue

        return documents

    def crawl_forum(self, crawler: SeleniumCrawler, forum_url: str, max_pages: int = 5):
        """Crawl a specific forum"""
        logger.info(f"Crawling {forum_url}...")

        for page in range(1, max_pages + 1):
            if len(self.collected_docs) >= self.max_docs:
                break

            logger.info(f"Processing page {page}...")
            page_url = f"{forum_url}page-{page}"

            html = crawler.get_page(page_url)
            if not html:
                logger.warning(f"Failed to load page {page}")
                continue

            soup = BeautifulSoup(html, 'lxml')
            thread_links = []

            for link in soup.find_all('a', class_='structItem-title'):
                href = link.get('href')
                if href and '/threads/' in href:
                    if href.startswith('/'):
                        href = self.base_url + href
                    thread_links.append(href)

            if not thread_links:
                logger.warning(f"No threads found on page {page}")
                continue

            logger.info(f"Found {len(thread_links)} threads")

            for i, thread_url in enumerate(thread_links):
                if len(self.collected_docs) >= self.max_docs:
                    break

                logger.info(f"Processing thread {i+1}/{len(thread_links)}")

                thread_html = crawler.get_page(thread_url)
                if thread_html:
                    documents = self.parse_thread_content(thread_html, thread_url)
                    self.collected_docs.extend(documents)
                    logger.info(f"Collected {len(documents)} docs. Total: {len(self.collected_docs)}")

                crawler.human_like_delay(2, 4)

            crawler.human_like_delay(3, 5)

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
        logger.info(f"Starting TinhTe Selenium crawler (target: {self.max_docs} docs)...")

        with SeleniumCrawler(headless=self.headless) as crawler:
            for forum_url in self.forums:
                if len(self.collected_docs) >= self.max_docs:
                    break
                self.crawl_forum(crawler, forum_url, max_pages=10)

        self.save_data()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"\n{'='*60}")
        logger.info(f"TinhTe Selenium Crawling Summary:")
        logger.info(f"Documents collected: {len(self.collected_docs)}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Speed: {len(self.collected_docs)/duration:.2f} docs/second")
        logger.info(f"{'='*60}\n")

        return {
            'source': 'tinhte_selenium',
            'docs_collected': len(self.collected_docs),
            'duration': duration,
            'docs_per_second': len(self.collected_docs) / duration if duration > 0 else 0
        }


def main():
    crawler = ImprovedTinhTeCrawler(max_docs=25, headless=False)
    stats = crawler.run()
    print(f"\nStats: {stats}")


if __name__ == '__main__':
    main()

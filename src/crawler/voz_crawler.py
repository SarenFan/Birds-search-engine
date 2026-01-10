"""
Voz Forum Crawler (F17/F33)
Crawl threads and quality comments (> 50 words)
"""
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import jsonlines
from typing import List, Dict, Optional
from tqdm.asyncio import tqdm
import logging
from datetime import datetime
import os

from src.crawler.utils import (
    get_headers, calculate_hash, is_valid_document,
    clean_text, rate_limit_sleep, save_checkpoint, load_checkpoint
)
from src.crawler.parser import remove_html_tags, clean_vietnamese_text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VozCrawler:
    """Crawler for Voz.vn forum"""

    def __init__(self, output_file: str = 'data_sample/voz_data.jsonl',
                 checkpoint_file: str = 'data_sample/voz_checkpoint.json',
                 max_docs: int = 100):
        self.base_url = 'https://voz.vn'
        self.forums = {
            'f17': f'{self.base_url}/f/tam-su-tam-tinh.17/',
            'f33': f'{self.base_url}/f/chuyen-tro.33/'
        }
        self.output_file = output_file
        self.checkpoint_file = checkpoint_file
        self.max_docs = max_docs
        self.collected_docs = []
        self.seen_hashes = set()
        self.session: Optional[aiohttp.ClientSession] = None

        # Load checkpoint if exists
        checkpoint = load_checkpoint(checkpoint_file)
        self.seen_hashes = set(checkpoint.get('seen_hashes', []))
        self.start_page = checkpoint.get('last_page', 1)

    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page with retry logic"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                async with self.session.get(url, headers=get_headers()) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:
                        logger.warning(f"Rate limited, waiting...")
                        await asyncio.sleep(5)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        return None

    async def get_thread_urls(self, forum_url: str, page: int = 1) -> List[str]:
        """Get all thread URLs from a forum page"""
        url = f"{forum_url}page-{page}"
        html = await self.fetch_page(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        thread_links = []

        # Find thread links (Voz structure)
        for link in soup.find_all('a', class_='PreviewTooltip'):
            href = link.get('href')
            if href and '/t/' in href:
                if href.startswith('/'):
                    href = self.base_url + href
                thread_links.append(href)

        return thread_links

    async def parse_thread(self, thread_url: str) -> List[Dict]:
        """Parse a thread and extract posts/comments"""
        html = await self.fetch_page(thread_url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        documents = []

        # Get thread title
        title_elem = soup.find('h1', class_='p-title-value')
        thread_title = title_elem.text.strip() if title_elem else 'Unknown'

        # Find all posts
        posts = soup.find_all('article', class_='message')

        for post in posts:
            try:
                # Extract author
                author_elem = post.find('a', class_='username')
                author = author_elem.text.strip() if author_elem else 'Anonymous'

                # Extract timestamp
                time_elem = post.find('time')
                timestamp = time_elem.get('datetime', '') if time_elem else ''

                # Extract content
                content_elem = post.find('div', class_='message-body')
                if content_elem:
                    # Get text content
                    content_html = str(content_elem)
                    content_text = remove_html_tags(content_html)
                    content_text = clean_vietnamese_text(content_text)
                    content_text = clean_text(content_text)

                    # Validate document
                    if is_valid_document(content_text, min_words=50):
                        doc_hash = calculate_hash(content_text)

                        if doc_hash not in self.seen_hashes:
                            document = {
                                'id': doc_hash,
                                'source': 'voz',
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

    async def crawl_forum(self, forum_name: str, forum_url: str, max_pages: int = 10):
        """Crawl a specific forum"""
        logger.info(f"Crawling {forum_name}...")

        for page in range(self.start_page, max_pages + 1):
            if len(self.collected_docs) >= self.max_docs:
                break

            logger.info(f"Processing {forum_name} page {page}...")
            thread_urls = await self.get_thread_urls(forum_url, page)

            if not thread_urls:
                logger.warning(f"No threads found on page {page}")
                break

            # Process threads with progress bar
            for thread_url in tqdm(thread_urls, desc=f"{forum_name} Page {page}"):
                if len(self.collected_docs) >= self.max_docs:
                    break

                documents = await self.parse_thread(thread_url)
                self.collected_docs.extend(documents)

                # Rate limiting
                await asyncio.sleep(0.5)

            # Save checkpoint after each page
            self.save_checkpoint(page)

            # Rate limiting between pages
            await asyncio.sleep(1)

    def save_checkpoint(self, last_page: int):
        """Save progress checkpoint"""
        checkpoint = {
            'last_page': last_page,
            'seen_hashes': list(self.seen_hashes),
            'docs_collected': len(self.collected_docs),
            'timestamp': datetime.now().isoformat()
        }
        save_checkpoint(checkpoint, self.checkpoint_file)

    def save_data(self):
        """Save collected documents to JSONL file"""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        with jsonlines.open(self.output_file, mode='w') as writer:
            for doc in self.collected_docs:
                writer.write(doc)

        logger.info(f"Saved {len(self.collected_docs)} documents to {self.output_file}")

    async def run(self):
        """Main crawling process"""
        start_time = datetime.now()
        logger.info(f"Starting Voz crawler (target: {self.max_docs} docs)...")

        # Crawl both forums
        for forum_name, forum_url in self.forums.items():
            if len(self.collected_docs) >= self.max_docs:
                break
            await self.crawl_forum(forum_name, forum_url, max_pages=20)

        # Save results
        self.save_data()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"\n{'='*60}")
        logger.info(f"Voz Crawling Summary:")
        logger.info(f"Documents collected: {len(self.collected_docs)}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Speed: {len(self.collected_docs)/duration:.2f} docs/second")
        logger.info(f"{'='*60}\n")

        return {
            'source': 'voz',
            'docs_collected': len(self.collected_docs),
            'duration': duration,
            'docs_per_second': len(self.collected_docs) / duration if duration > 0 else 0
        }


async def main():
    """Test the crawler"""
    async with VozCrawler(max_docs=100) as crawler:
        stats = await crawler.run()
        print(f"\nStats: {stats}")


if __name__ == '__main__':
    asyncio.run(main())

"""
Otofun Forum Crawler
Crawl automobile discussion threads and quality comments (> 50 words)
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
    clean_text, save_checkpoint, load_checkpoint
)
from src.crawler.parser import remove_html_tags, clean_vietnamese_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OtofunCrawler:
    """Crawler for Otofun.net forum"""

    def __init__(self, output_file: str = 'data_sample/otofun_data.jsonl',
                 checkpoint_file: str = 'data_sample/otofun_checkpoint.json',
                 max_docs: int = 100):
        self.base_url = 'https://otofun.net'
        # Popular forums on Otofun
        self.forums = [
            f'{self.base_url}/forums/tam-su-cua-biker.70/',
            f'{self.base_url}/forums/dinh-duong-suc-khoe.71/',
            f'{self.base_url}/forums/oto-xe-may.1/',
        ]
        self.output_file = output_file
        self.checkpoint_file = checkpoint_file
        self.max_docs = max_docs
        self.collected_docs = []
        self.seen_hashes = set()
        self.session: Optional[aiohttp.ClientSession] = None

        checkpoint = load_checkpoint(checkpoint_file)
        self.seen_hashes = set(checkpoint.get('seen_hashes', []))

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page with retry"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                async with self.session.get(url, headers=get_headers()) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:
                        await asyncio.sleep(5)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)

        return None

    async def get_thread_urls(self, forum_url: str, page: int = 1) -> List[str]:
        """Get thread URLs from forum page"""
        url = f"{forum_url}page-{page}"
        html = await self.fetch_page(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        thread_links = []

        # Otofun uses XenForo structure
        for link in soup.find_all('a', class_='structItem-title'):
            href = link.get('href')
            if href and ('/threads/' in href or '/t/' in href):
                if href.startswith('/'):
                    href = self.base_url + href
                thread_links.append(href)

        # Also try alternative structure
        if not thread_links:
            for link in soup.find_all('a', {'data-preview-url': True}):
                href = link.get('href')
                if href and ('/threads/' in href or '/t/' in href):
                    if href.startswith('/'):
                        href = self.base_url + href
                    thread_links.append(href)

        return thread_links

    async def parse_thread(self, thread_url: str) -> List[Dict]:
        """Parse thread and extract posts"""
        html = await self.fetch_page(thread_url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        documents = []

        # Get thread title
        title_elem = soup.find('h1', class_='p-title-value')
        if not title_elem:
            title_elem = soup.find('h1')
        thread_title = title_elem.text.strip() if title_elem else 'Unknown'

        # Find all posts
        posts = soup.find_all('article', class_='message')
        if not posts:
            posts = soup.find_all('div', class_='message-main')

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
                if not content_elem:
                    content_elem = post.find('article', class_='message-body')

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
                                'source': 'otofun',
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

    async def crawl_forum(self, forum_url: str, max_pages: int = 10):
        """Crawl a specific forum"""
        logger.info(f"Crawling {forum_url}...")

        for page in range(1, max_pages + 1):
            if len(self.collected_docs) >= self.max_docs:
                break

            logger.info(f"Processing page {page}...")
            thread_urls = await self.get_thread_urls(forum_url, page)

            if not thread_urls:
                break

            for thread_url in tqdm(thread_urls, desc=f"Page {page}"):
                if len(self.collected_docs) >= self.max_docs:
                    break

                documents = await self.parse_thread(thread_url)
                self.collected_docs.extend(documents)
                await asyncio.sleep(0.5)

            await asyncio.sleep(1)

    def save_data(self):
        """Save collected documents"""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        with jsonlines.open(self.output_file, mode='w') as writer:
            for doc in self.collected_docs:
                writer.write(doc)

        logger.info(f"Saved {len(self.collected_docs)} documents to {self.output_file}")

    async def run(self):
        """Main crawling process"""
        start_time = datetime.now()
        logger.info(f"Starting Otofun crawler (target: {self.max_docs} docs)...")

        for forum_url in self.forums:
            if len(self.collected_docs) >= self.max_docs:
                break
            await self.crawl_forum(forum_url, max_pages=20)

        self.save_data()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"\n{'='*60}")
        logger.info(f"Otofun Crawling Summary:")
        logger.info(f"Documents collected: {len(self.collected_docs)}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Speed: {len(self.collected_docs)/duration:.2f} docs/second")
        logger.info(f"{'='*60}\n")

        return {
            'source': 'otofun',
            'docs_collected': len(self.collected_docs),
            'duration': duration,
            'docs_per_second': len(self.collected_docs) / duration if duration > 0 else 0
        }


async def main():
    async with OtofunCrawler(max_docs=100) as crawler:
        stats = await crawler.run()
        print(f"\nStats: {stats}")


if __name__ == '__main__':
    asyncio.run(main())

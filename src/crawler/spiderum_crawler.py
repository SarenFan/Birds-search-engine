"""
Spiderum Crawler
Crawl articles and quality comments (> 50 words)
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


class SpiderumCrawler:
    """Crawler for Spiderum.com"""

    def __init__(self, output_file: str = 'data_sample/spiderum_data.jsonl',
                 checkpoint_file: str = 'data_sample/spiderum_checkpoint.json',
                 max_docs: int = 100):
        self.base_url = 'https://spiderum.com'
        # Spiderum categories
        self.categories = [
            f'{self.base_url}/chuyen-muc/tam-su',
            f'{self.base_url}/chuyen-muc/cong-nghe',
            f'{self.base_url}/chuyen-muc/van-hoa',
            f'{self.base_url}/chuyen-muc/khoa-hoc'
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

    async def get_article_urls(self, category_url: str, page: int = 1) -> List[str]:
        """Get article URLs from category page"""
        # Spiderum might use infinite scroll, so try different approaches
        url = category_url if page == 1 else f"{category_url}?page={page}"
        html = await self.fetch_page(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        article_links = []

        # Find article links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/bai-dang/' in href:
                if href.startswith('/'):
                    href = self.base_url + href
                if href not in article_links:
                    article_links.append(href)

        return article_links

    async def parse_article(self, article_url: str) -> List[Dict]:
        """Parse article and extract content + comments"""
        html = await self.fetch_page(article_url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        documents = []

        try:
            # Get article title
            title_elem = soup.find('h1')
            article_title = title_elem.text.strip() if title_elem else 'Unknown'

            # Get article author
            author_elem = soup.find('a', class_='author-name')
            if not author_elem:
                author_elem = soup.find('span', class_='author')
            author = author_elem.text.strip() if author_elem else 'Anonymous'

            # Get article content (main body)
            content_elem = soup.find('div', class_='post-content')
            if not content_elem:
                content_elem = soup.find('article')
            if not content_elem:
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
                            'source': 'spiderum',
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

            # Get comments
            comments = soup.find_all('div', class_='comment-content')
            if not comments:
                comments = soup.find_all('div', class_='comment')

            for comment in comments:
                try:
                    comment_text = remove_html_tags(str(comment))
                    comment_text = clean_vietnamese_text(comment_text)
                    comment_text = clean_text(comment_text)

                    if is_valid_document(comment_text, min_words=50):
                        doc_hash = calculate_hash(comment_text)

                        if doc_hash not in self.seen_hashes:
                            document = {
                                'id': doc_hash,
                                'source': 'spiderum',
                                'url': article_url,
                                'title': article_title,
                                'author': 'Comment User',
                                'content': comment_text,
                                'type': 'comment',
                                'word_count': len(comment_text.split()),
                                'crawled_at': datetime.now().isoformat()
                            }
                            documents.append(document)
                            self.seen_hashes.add(doc_hash)

                except Exception as e:
                    logger.error(f"Error parsing comment: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing article {article_url}: {e}")

        return documents

    async def crawl_category(self, category_url: str, max_pages: int = 10):
        """Crawl a specific category"""
        logger.info(f"Crawling {category_url}...")

        for page in range(1, max_pages + 1):
            if len(self.collected_docs) >= self.max_docs:
                break

            logger.info(f"Processing page {page}...")
            article_urls = await self.get_article_urls(category_url, page)

            if not article_urls:
                break

            for article_url in tqdm(article_urls, desc=f"Page {page}"):
                if len(self.collected_docs) >= self.max_docs:
                    break

                documents = await self.parse_article(article_url)
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
        logger.info(f"Starting Spiderum crawler (target: {self.max_docs} docs)...")

        for category_url in self.categories:
            if len(self.collected_docs) >= self.max_docs:
                break
            await self.crawl_category(category_url, max_pages=20)

        self.save_data()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"\n{'='*60}")
        logger.info(f"Spiderum Crawling Summary:")
        logger.info(f"Documents collected: {len(self.collected_docs)}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Speed: {len(self.collected_docs)/duration:.2f} docs/second")
        logger.info(f"{'='*60}\n")

        return {
            'source': 'spiderum',
            'docs_collected': len(self.collected_docs),
            'duration': duration,
            'docs_per_second': len(self.collected_docs) / duration if duration > 0 else 0
        }


async def main():
    async with SpiderumCrawler(max_docs=100) as crawler:
        stats = await crawler.run()
        print(f"\nStats: {stats}")


if __name__ == '__main__':
    asyncio.run(main())

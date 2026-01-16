"""
Production Voz Forum Crawler - 1 Million Documents
Optimized Version (NO tokenization during crawl)
Features:
- Multi-threading with configurable workers (default 20)
- Checkpoint/Resume mechanism
- Progress logging
- Rate limiting & error handling
- Multiple forum categories
- Data cleaning (tokenization done separately)
- Statistics reporting
"""

import cloudscraper
from bs4 import BeautifulSoup
import json
import time
import random
import os
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import logging
from collections import defaultdict
from typing import Dict, List, Set, Optional, Tuple
import pickle
import hashlib

# Tokenization is done in post-processing, not during crawl
# This significantly speeds up the crawler


class CrawlCheckpoint:
    """Checkpoint manager for resume capability"""
    
    def __init__(self, checkpoint_path: str = 'data/crawl_checkpoint.pkl'):
        self.checkpoint_path = checkpoint_path
        self.crawled_threads: Set[str] = set()
        self.crawled_posts: Set[str] = set()
        self.total_docs = 0
        self.failed_urls: List[str] = []
        self.last_forum_page: Dict[str, int] = {}
        self.last_save_time = datetime.now()
        
    def load(self) -> bool:
        """Load checkpoint from disk"""
        if os.path.exists(self.checkpoint_path):
            try:
                with open(self.checkpoint_path, 'rb') as f:
                    data = pickle.load(f)
                self.crawled_threads = data.get('crawled_threads', set())
                self.crawled_posts = data.get('crawled_posts', set())
                self.total_docs = data.get('total_docs', 0)
                self.failed_urls = data.get('failed_urls', [])
                self.last_forum_page = data.get('last_forum_page', {})
                return True
            except Exception as e:
                logging.warning(f"Failed to load checkpoint: {e}")
                return False
        return False
    
    def save(self):
        """Save checkpoint to disk"""
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
        data = {
            'crawled_threads': self.crawled_threads,
            'crawled_posts': self.crawled_posts,
            'total_docs': self.total_docs,
            'failed_urls': self.failed_urls,
            'last_forum_page': self.last_forum_page,
            'save_time': datetime.now().isoformat()
        }
        with open(self.checkpoint_path, 'wb') as f:
            pickle.dump(data, f)
        self.last_save_time = datetime.now()
    
    def should_save(self, interval_seconds: int = 60) -> bool:
        """Check if we should save checkpoint"""
        return (datetime.now() - self.last_save_time).seconds >= interval_seconds
    
    def is_thread_crawled(self, thread_id: str) -> bool:
        return thread_id in self.crawled_threads
    
    def is_post_crawled(self, post_id: str) -> bool:
        return post_id in self.crawled_posts
    
    def mark_thread_crawled(self, thread_id: str):
        self.crawled_threads.add(thread_id)
    
    def mark_post_crawled(self, post_id: str):
        self.crawled_posts.add(post_id)


class CrawlStatistics:
    """Statistics collector for crawl insights"""
    
    def __init__(self):
        self.lock = Lock()
        self.total_docs = 0
        self.total_words = 0
        self.word_freq: Dict[str, int] = defaultdict(int)
        self.doc_lengths: List[int] = []
        self.authors: Set[str] = set()
        self.threads: Set[str] = set()
        self.start_time = None
        self.requests_made = 0
        self.requests_failed = 0
        self.duplicates_skipped = 0
        
    def add_document(self, doc: dict, tokens: List[str]):
        """Add document statistics"""
        with self.lock:
            self.total_docs += 1
            doc_len = len(tokens)
            self.total_words += doc_len
            self.doc_lengths.append(doc_len)
            self.authors.add(doc.get('author', 'unknown'))
            self.threads.add(doc.get('thread_id', ''))
            
            # Word frequency (sample to save memory)
            if self.total_docs <= 100000:  # Only track for first 100k
                for token in tokens[:100]:  # Limit per doc
                    self.word_freq[token] += 1
    
    def get_report(self) -> dict:
        """Generate statistics report"""
        with self.lock:
            avg_length = sum(self.doc_lengths) / max(1, len(self.doc_lengths))
            
            # Get top words
            top_words = sorted(self.word_freq.items(), key=lambda x: x[1], reverse=True)[:100]
            
            return {
                'total_documents': self.total_docs,
                'total_words': self.total_words,
                'vocabulary_size': len(self.word_freq),
                'avg_doc_length': round(avg_length, 2),
                'unique_authors': len(self.authors),
                'unique_threads': len(self.threads),
                'requests_made': self.requests_made,
                'requests_failed': self.requests_failed,
                'duplicates_skipped': self.duplicates_skipped,
                'top_words': top_words[:50],
                'doc_length_distribution': {
                    'min': min(self.doc_lengths) if self.doc_lengths else 0,
                    'max': max(self.doc_lengths) if self.doc_lengths else 0,
                    'median': sorted(self.doc_lengths)[len(self.doc_lengths)//2] if self.doc_lengths else 0
                }
            }


class VozProductionCrawler:
    """
    Production-grade Voz Forum Crawler
    Designed for crawling 1,000,000+ documents
    """
    
    BASE_URL = "https://voz.vn"
    
    # Multiple forum categories to crawl from
    FORUMS = {
        'f17': '/f/chuyen-tro-linh-tinh.17/',  # Chuyện trò linh tinh
        'f33': '/f/the-gioi-game.33/',  # Thế giới game
        'f10': '/f/may-tinh.10/',  # Máy tính
        'f11': '/f/dien-thoai.11/',  # Điện thoại
        'f249': '/f/mot-goc-rieng.249/',  # Một góc riêng
        'f594': '/f/kinh-te-tai-chinh.594/',  # Kinh tế tài chính
        'f595': '/f/bat-dong-san.595/',  # Bất động sản
        'f174': '/f/oto-xe-may.174/',  # Ô tô xe máy
    }
    
    def __init__(self, 
                 num_workers: int = 20,
                 delay_range: tuple = (0.1, 0.3),
                 checkpoint_interval: int = 60,
                 min_word_count: int = 50):
        """
        Initialize production crawler
        
        Args:
            num_workers: Number of concurrent threads
            delay_range: Random delay between requests
            checkpoint_interval: Seconds between checkpoint saves
            min_word_count: Minimum words for quality filter
        """
        self.num_workers = num_workers
        self.delay_range = delay_range
        self.checkpoint_interval = checkpoint_interval
        self.min_word_count = min_word_count
        
        # Thread-safe components
        self.write_lock = Lock()
        self.stats_lock = Lock()
        self.checkpoint_lock = Lock()
        
        # Initialize components
        self.checkpoint = CrawlCheckpoint()
        self.stats = CrawlStatistics()
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(f'logs/crawl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_scraper(self):
        """Create a cloudscraper instance with connection pooling"""
        import requests.adapters
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        # Add connection pooling to reuse connections
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        scraper.mount('https://', adapter)
        scraper.mount('http://', adapter)
        return scraper
    
    def _random_delay(self):
        """Add random delay between requests"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _get_page(self, scraper, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch a page with retries"""
        for attempt in range(max_retries):
            try:
                with self.stats_lock:
                    self.stats.requests_made += 1
                
                response = scraper.get(url, timeout=30)
                
                if "Just a moment" in response.text:
                    self.logger.warning(f"Cloudflare challenge on {url}")
                    time.sleep(5)
                    continue
                
                if response.status_code == 200:
                    return response.text
                
                if response.status_code == 429:  # Rate limited
                    self.logger.warning("Rate limited, sleeping 30s")
                    time.sleep(30)
                    continue
                
                with self.stats_lock:
                    self.stats.requests_failed += 1
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error fetching {url}: {e}")
                with self.stats_lock:
                    self.stats.requests_failed += 1
                time.sleep(3)
        
        # Add to failed URLs for later retry
        with self.checkpoint_lock:
            self.checkpoint.failed_urls.append(url)
        
        return None
    
    def _simple_word_count(self, text: str) -> int:
        """Simple word count using whitespace split (fast)"""
        words = text.lower().split()
        # Filter: min 2 chars, not pure digits
        count = sum(1 for w in words if len(w) >= 2 and not w.isdigit())
        return count
    
    def _clean_content(self, text: str) -> str:
        """Clean and normalize content"""
        import re
        import unicodedata
        
        # Normalize unicode
        text = unicodedata.normalize('NFC', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove HTML entities
        text = re.sub(r'&\w+;', ' ', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_thread_list(self, scraper, forum_url: str, page: int = 1) -> Tuple[List[dict], int]:
        """Get thread list from a forum page. Returns (threads_to_crawl, total_threads_on_page)"""
        url = f"{self.BASE_URL}{forum_url}page-{page}" if page > 1 else f"{self.BASE_URL}{forum_url}"
        
        html = self._get_page(scraper, url)
        if not html:
            return [], 0
        
        self._random_delay()
        
        soup = BeautifulSoup(html, 'lxml')
        threads = []
        total_on_page = 0
        
        for item in soup.select('div.structItem'):
            title_elem = item.select_one('div.structItem-title a')
            if not title_elem:
                continue
            
            href = title_elem.get('href', '')
            if not href.startswith('/t/'):
                continue
            
            total_on_page += 1  # Count all threads on page
            thread_id = self._extract_thread_id(href)
            
            # Skip already crawled threads
            if self.checkpoint.is_thread_crawled(thread_id):
                continue
            
            threads.append({
                'title': title_elem.get_text(strip=True),
                'url': self.BASE_URL + href,
                'thread_id': thread_id
            })
        
        return threads, total_on_page
    
    def _extract_thread_id(self, url: str) -> str:
        """Extract thread ID from URL"""
        try:
            parts = url.rstrip('/').split('.')
            return parts[-1]
        except:
            return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def crawl_thread(self, thread: dict, max_pages: int = 10) -> List[dict]:
        """Crawl a single thread - called by worker threads"""
        scraper = self._create_scraper()
        documents = []
        thread_id = thread['thread_id']
        thread_title = thread['title']
        thread_url = thread['url']
        
        for page in range(1, max_pages + 1):
            url = f"{thread_url}page-{page}" if page > 1 else thread_url
            
            html = self._get_page(scraper, url)
            if not html:
                break
            
            self._random_delay()
            
            soup = BeautifulSoup(html, 'lxml')
            posts = soup.select('article.message--post')
            
            if not posts:
                break
            
            for post in posts:
                doc = self._parse_post(post, thread_id, thread_title, thread_url)
                if doc:
                    # Check quality with simple word count (fast)
                    content_clean = self._clean_content(doc['content'])
                    word_count = self._simple_word_count(content_clean)
                    
                    if word_count >= self.min_word_count:
                        doc['content_clean'] = content_clean
                        doc['word_count'] = word_count
                        documents.append(doc)
            
            # Check for next page
            next_btn = soup.select_one('a.pageNav-jump--next')
            if not next_btn:
                break
        
        # Mark thread as crawled
        with self.checkpoint_lock:
            self.checkpoint.mark_thread_crawled(thread_id)
        
        return documents
    
    def _parse_post(self, post_elem, thread_id: str, thread_title: str, thread_url: str) -> Optional[dict]:
        """Parse a single post"""
        try:
            post_id = post_elem.get('data-content', '').replace('post-', '')
            
            # Skip already crawled posts
            if self.checkpoint.is_post_crawled(post_id):
                with self.stats_lock:
                    self.stats.duplicates_skipped += 1
                return None
            
            content_elem = post_elem.select_one('div.bbWrapper')
            if not content_elem:
                return None
            
            # Handle quotes
            has_quote = False
            quoted_author = None
            quoted_content = None
            
            quote_elem = content_elem.select_one('blockquote.bbCodeBlock--quote')
            if quote_elem:
                has_quote = True
                quote_title = quote_elem.select_one('div.bbCodeBlock-title')
                if quote_title:
                    quoted_author = quote_title.get_text(strip=True).replace(' said:', '').replace(' nói:', '')
                quote_content_elem = quote_elem.select_one('div.bbCodeBlock-content')
                if quote_content_elem:
                    quoted_content = quote_content_elem.get_text(strip=True)[:500]  # Limit quote length
                quote_elem.decompose()
            
            content_raw = content_elem.get_text(separator=' ', strip=True)
            
            author_elem = post_elem.select_one('.message-name .username')
            author = author_elem.get_text(strip=True) if author_elem else "unknown"
            
            time_elem = post_elem.select_one('.message-attribution-main time')
            timestamp = time_elem.get('datetime', '') if time_elem else ""
            
            # Mark post as crawled
            with self.checkpoint_lock:
                self.checkpoint.mark_post_crawled(post_id)
            
            return {
                'doc_id': f"voz_t{thread_id}_p{post_id}",
                'thread_id': f"t{thread_id}",
                'thread_title': thread_title,
                'content': content_raw,
                'author': author,
                'timestamp': timestamp,
                'has_quote': has_quote,
                'quoted_author': quoted_author,
                'quoted_content': quoted_content,
                'source': 'voz',
                'url': f"{self.BASE_URL}/p/{post_id}/"
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing post: {e}")
            return None
    
    def crawl(self, 
              target_docs: int = 1000000,
              output_file: str = 'data/voz_1m.jsonl',
              resume: bool = True) -> dict:
        """
        Main crawl function
        
        Args:
            target_docs: Target number of documents
            output_file: Output JSONL file path
            resume: Whether to resume from checkpoint
            
        Returns:
            Statistics dict
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Load checkpoint if resuming
        if resume and self.checkpoint.load():
            self.logger.info(f"📂 Resumed from checkpoint: {self.checkpoint.total_docs} docs already crawled")
            mode = 'a'  # Append mode
        else:
            self.logger.info("🆕 Starting fresh crawl")
            mode = 'w'  # Write mode
        
        self.stats.start_time = datetime.now()
        self.logger.info(f"🚀 Starting production crawler at {self.stats.start_time.strftime('%H:%M:%S')}")
        self.logger.info(f"🔧 Workers: {self.num_workers}")
        self.logger.info(f"🎯 Target: {target_docs:,} documents")
        self.logger.info(f"⚡ Optimized mode: NO tokenization during crawl")
        
        # Test connection
        scraper = self._create_scraper()
        test_url = f"{self.BASE_URL}{list(self.FORUMS.values())[0]}"
        test_html = self._get_page(scraper, test_url)
        
        if not test_html or "Just a moment" in test_html:
            self.logger.error("❌ Cannot connect to Voz or Cloudflare blocking")
            return self.stats.get_report()
        
        self.logger.info("✅ Connected to Voz!")
        
        total_docs = self.checkpoint.total_docs
        
        with open(output_file, mode, encoding='utf-8') as f:
            pbar = tqdm(total=target_docs, initial=total_docs, desc="Documents")
            
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                # Cycle through forums
                forum_cycle = list(self.FORUMS.items())
                forum_idx = 0
                
                while total_docs < target_docs:
                    # Get current forum
                    forum_id, forum_url = forum_cycle[forum_idx % len(forum_cycle)]
                    forum_idx += 1
                    
                    # Get starting page for this forum
                    start_page = self.checkpoint.last_forum_page.get(forum_id, 1)
                    
                    self.logger.info(f"📂 Crawling {forum_id} from page {start_page}")
                    
                    # Collect threads from forum
                    for page in range(start_page, start_page + 50):  # 50 pages per batch
                        if total_docs >= target_docs:
                            break
                        
                        threads, total_on_page = self.get_thread_list(scraper, forum_url, page)
                        
                        if total_on_page == 0:
                            # No threads on page = end of forum
                            self.logger.info(f"   End of forum at page {page}")
                            break
                        
                        if not threads:
                            # Page has threads but all already crawled, continue to next page
                            self.logger.debug(f"   Page {page}: all {total_on_page} threads already crawled")
                            continue
                        
                        # Submit threads to workers
                        futures = {}
                        for thread in threads[:20]:  # Limit concurrent threads
                            future = executor.submit(self.crawl_thread, thread)
                            futures[future] = thread
                        
                        # Process completed futures
                        for future in as_completed(futures):
                            if total_docs >= target_docs:
                                break
                            
                            thread = futures[future]
                            try:
                                docs = future.result()
                                
                                for doc in docs:
                                    if total_docs >= target_docs:
                                        break
                                    
                                    # Update statistics (simple word count)
                                    word_count = doc.get('word_count', 0)
                                    with self.stats_lock:
                                        self.stats.total_docs += 1
                                        self.stats.total_words += word_count
                                        self.stats.doc_lengths.append(word_count)
                                        self.stats.authors.add(doc.get('author', 'unknown'))
                                        self.stats.threads.add(doc.get('thread_id', ''))
                                    
                                    # Output doc (no tokens field)
                                    output_doc = doc
                                    
                                    with self.write_lock:
                                        f.write(json.dumps(output_doc, ensure_ascii=False) + '\n')
                                        f.flush()  # Ensure data is written
                                    
                                    total_docs += 1
                                    pbar.update(1)
                                
                                if docs:
                                    tqdm.write(f"✓ {thread['title'][:40]}... ({len(docs)} docs)")
                                
                            except Exception as e:
                                self.logger.error(f"Error processing thread: {e}")
                        
                        # Save checkpoint periodically
                        if self.checkpoint.should_save(self.checkpoint_interval):
                            with self.checkpoint_lock:
                                self.checkpoint.total_docs = total_docs
                                self.checkpoint.last_forum_page[forum_id] = page
                                self.checkpoint.save()
                            self.logger.info(f"💾 Checkpoint saved: {total_docs:,} docs")
                    
                    # Brief pause between forums
                    time.sleep(2)
            
            pbar.close()
        
        # Final checkpoint
        with self.checkpoint_lock:
            self.checkpoint.total_docs = total_docs
            self.checkpoint.save()
        
        # Generate report
        end_time = datetime.now()
        duration = (end_time - self.stats.start_time).total_seconds()
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info("📊 FINAL CRAWL STATISTICS")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"⏱️  Total time: {duration/60:.1f} minutes ({duration/3600:.2f} hours)")
        self.logger.info(f"📄 Documents collected: {total_docs:,}")
        self.logger.info(f"📝 Vocabulary size: {len(self.stats.word_freq):,}")
        self.logger.info(f"📏 Avg doc length: {self.stats.get_report()['avg_doc_length']:.1f} words")
        self.logger.info(f"🌐 Requests made: {self.stats.requests_made:,}")
        self.logger.info(f"✗  Failed: {self.stats.requests_failed:,}")
        self.logger.info(f"🔄 Duplicates skipped: {self.stats.duplicates_skipped:,}")
        self.logger.info(f"⚡ Speed: {total_docs/max(1, duration)*60:.1f} docs/minute")
        self.logger.info(f"{'='*60}")
        
        # Save statistics report
        stats_report = self.stats.get_report()
        stats_report['duration_seconds'] = duration
        stats_report['start_time'] = self.stats.start_time.isoformat()
        stats_report['end_time'] = end_time.isoformat()
        
        stats_path = output_file.replace('.jsonl', '_stats.json')
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats_report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"\n📁 Data saved to: {output_file}")
        self.logger.info(f"📊 Stats saved to: {stats_path}")
        
        return stats_report


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Voz Production Crawler')
    parser.add_argument('--target', '-t', type=int, default=1000000,
                       help='Target number of documents')
    parser.add_argument('--workers', '-w', type=int, default=20,
                       help='Number of worker threads (default 20)')
    parser.add_argument('--output', '-o', default='data/voz_1m.jsonl',
                       help='Output file path')
    parser.add_argument('--no-resume', action='store_true',
                       help='Do not resume from checkpoint')
    parser.add_argument('--min-words', type=int, default=30,
                       help='Minimum word count per document')
    
    args = parser.parse_args()
    
    crawler = VozProductionCrawler(
        num_workers=args.workers,
        min_word_count=args.min_words
    )
    
    stats = crawler.crawl(
        target_docs=args.target,
        output_file=args.output,
        resume=not args.no_resume
    )
    
    print(f"\n✅ Crawl completed! {stats['total_documents']:,} documents collected")


if __name__ == "__main__":
    main()

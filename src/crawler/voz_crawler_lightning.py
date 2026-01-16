#!/usr/bin/env python3
"""
Voz Crawler for Lightning AI
Standalone version - no external dependencies except cloudscraper, bs4, lxml, tqdm

Usage:
    pip install cloudscraper beautifulsoup4 lxml tqdm
    python voz_crawler_lightning.py --target 600000 --workers 10
"""

import json
import os
import re
import time
import random
import pickle
import logging
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Optional, List
from tqdm import tqdm

try:
    import cloudscraper
except ImportError:
    print("Installing cloudscraper...")
    os.system("pip install cloudscraper beautifulsoup4 lxml tqdm")
    import cloudscraper


class CrawlCheckpoint:
    """Checkpoint to resume crawling"""
    
    def __init__(self, checkpoint_file: str = 'data/crawl_checkpoint.pkl'):
        self.checkpoint_file = checkpoint_file
        self.crawled_threads = set()
        self.crawled_posts = set()
        self.last_forum = None
        self.last_page = 1
        self.total_docs = 0
        self._lock = Lock()
        
    def save(self):
        """Save checkpoint to file"""
        os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)
        with self._lock:
            data = {
                'crawled_threads': self.crawled_threads,
                'crawled_posts': self.crawled_posts,
                'last_forum': self.last_forum,
                'last_page': self.last_page,
                'total_docs': self.total_docs
            }
            with open(self.checkpoint_file, 'wb') as f:
                pickle.dump(data, f)
                
    def load(self) -> bool:
        """Load checkpoint from file"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        self.crawled_threads = data.get('crawled_threads', set())
                        self.crawled_posts = data.get('crawled_posts', set())
                        self.last_forum = data.get('last_forum')
                        self.last_page = data.get('last_page', 1)
                        self.total_docs = data.get('total_docs', 0)
                    return True
            except Exception as e:
                print(f"Warning: Could not load checkpoint: {e}")
        return False
    
    def add_thread(self, thread_id: str):
        with self._lock:
            self.crawled_threads.add(thread_id)
            
    def add_post(self, post_id: str):
        with self._lock:
            self.crawled_posts.add(post_id)
            self.total_docs += 1
            
    def is_thread_crawled(self, thread_id: str) -> bool:
        return thread_id in self.crawled_threads
    
    def is_post_crawled(self, post_id: str) -> bool:
        return post_id in self.crawled_posts


class VozCrawler:
    """Voz Forum Crawler optimized for Lightning AI"""
    
    BASE_URL = "https://voz.vn"
    
    # Forums to crawl (expanded list for 1M+ docs)
    # Ordered by estimated content volume
    FORUMS = [
        # HIGH VOLUME - Main discussion forums
        '/f/chuyen-tro-linh-tinh.17/',      # Chuyện trò linh tinh (HUGE)
        '/f/kinh-te-tai-chinh.33/',         # Kinh tế tài chính
        '/f/mot-goc-rieng.249/',            # Một góc riêng (personal stories)
        '/f/suc-khoe.53/',                  # Sức khỏe
        '/f/tin-trong-nuoc.102/',           # Tin trong nước
        '/f/tin-the-gioi.101/',             # Tin thế giới
        
        # TECH forums
        '/f/cong-nghe.2/',                  # Công nghệ chung
        '/f/may-tinh.3/',                   # Máy tính
        '/f/dien-thoai-tablet.4/',          # Điện thoại & Tablet
        '/f/lap-trinh.37/',                 # Lập trình
        '/f/mang-va-bao-mat.38/',           # Mạng & Bảo mật
        '/f/phan-mem.39/',                  # Phần mềm
        '/f/linux.40/',                     # Linux
        '/f/gaming.41/',                    # Gaming
        
        # AUTOMOTIVE
        '/f/o-to.174/',                     # Ô tô
        '/f/xe-may.175/',                   # Xe máy
        
        # LIFESTYLE
        '/f/the-thao.33/',                  # Thể thao
        '/f/am-thuc.56/',                   # Ẩm thực
        '/f/du-lich.57/',                   # Du lịch
        '/f/giai-tri.34/',                  # Giải trí
        '/f/phim-anh.296/',                 # Phim ảnh
        '/f/am-nhac.297/',                  # Âm nhạc
        
        # EDUCATION & CAREER
        '/f/giao-duc.103/',                 # Giáo dục
        '/f/du-hoc.104/',                   # Du học
        '/f/nghe-nghiep.105/',              # Nghề nghiệp
        
        # REAL ESTATE & FINANCE
        '/f/bat-dong-san.595/',             # Bất động sản
        '/f/chung-khoan.594/',              # Chứng khoán
        '/f/thi-truong.5/',                 # Thị trường
        
        # OTHER HIGH-ACTIVITY
        '/f/sach.58/',                      # Sách
        '/f/hoi-dap.111/',                  # Hỏi đáp
        '/f/rao-vat.7/',                    # Rao vặt (marketplace - lots of posts)
    ]
    
    def __init__(self, 
                 num_workers: int = 10,
                 delay_range: tuple = (0.1, 0.3),
                 min_word_count: int = 50,
                 start_page: int = 1):
        
        self.num_workers = num_workers
        self.delay_range = delay_range
        self.min_word_count = min_word_count
        self.start_page = start_page
        
        self.checkpoint = CrawlCheckpoint()
        self.stats_lock = Lock()
        self.file_lock = Lock()
        
        self.total_docs = 0
        self.requests_made = 0
        self.requests_failed = 0
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_scraper(self):
        """Create cloudscraper with connection pooling"""
        import requests.adapters
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=3)
        scraper.mount('https://', adapter)
        scraper.mount('http://', adapter)
        return scraper
    
    def _get_page(self, scraper, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch page with retries"""
        for attempt in range(max_retries):
            try:
                with self.stats_lock:
                    self.requests_made += 1
                
                response = scraper.get(url, timeout=30)
                
                if "Just a moment" in response.text:
                    self.logger.warning(f"Cloudflare challenge on {url}")
                    time.sleep(5)
                    continue
                
                if response.status_code == 200:
                    return response.text
                
                if response.status_code == 429:
                    self.logger.warning("Rate limited, sleeping 30s")
                    time.sleep(30)
                    continue
                
                with self.stats_lock:
                    self.requests_failed += 1
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error fetching {url}: {e}")
                time.sleep(2)
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _extract_thread_id(self, href: str) -> str:
        """Extract thread ID from URL"""
        match = re.search(r'/t/[^.]+\.(\d+)', href)
        return f"t{match.group(1)}" if match else ""
    
    def get_thread_list(self, scraper, forum_url: str, page: int = 1) -> tuple:
        """Get thread list from forum page. Returns (threads, total_on_page)"""
        url = f"{self.BASE_URL}{forum_url}page-{page}" if page > 1 else f"{self.BASE_URL}{forum_url}"
        
        html = self._get_page(scraper, url)
        if not html:
            return [], 0
        
        time.sleep(random.uniform(*self.delay_range))
        
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
            
            total_on_page += 1
            thread_id = self._extract_thread_id(href)
            
            if self.checkpoint.is_thread_crawled(thread_id):
                continue
            
            threads.append({
                'title': title_elem.get_text(strip=True),
                'url': self.BASE_URL + href,
                'thread_id': thread_id
            })
        
        return threads, total_on_page
    
    def crawl_thread(self, thread: dict, max_thread_pages: int = 10) -> List[dict]:
        """Crawl a single thread (multiple pages)"""
        scraper = self._create_scraper()
        documents = []
        base_url = thread['url']
        
        try:
            for page_num in range(1, max_thread_pages + 1):
                # Construct page URL
                if page_num == 1:
                    url = base_url
                else:
                    url = f"{base_url}page-{page_num}"
                
                html = self._get_page(scraper, url)
                if not html:
                    break
                
                soup = BeautifulSoup(html, 'lxml')
                posts_found = 0
                
                for article in soup.select('article.message'):
                    try:
                        post_id = article.get('data-content', '').replace('post-', '')
                        if not post_id or self.checkpoint.is_post_crawled(post_id):
                            continue
                        
                        content_elem = article.select_one('div.bbWrapper')
                        if not content_elem:
                            continue
                        
                        content = self._clean_text(content_elem.get_text())
                        word_count = len(content.split())
                        
                        if word_count >= self.min_word_count:
                            # Get author
                            author_elem = article.select_one('a.username')
                            author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                            
                            # Get timestamp
                            time_elem = article.select_one('time.u-dt')
                            timestamp = time_elem.get('datetime', '') if time_elem else ""
                            
                            doc = {
                                'doc_id': f"voz_{thread['thread_id']}_{post_id}",
                                'thread_id': thread['thread_id'],
                                'thread_title': thread['title'],
                                'content': content,
                                'author': author,
                                'timestamp': timestamp,
                                'source': 'voz',
                                'url': f"{self.BASE_URL}/p/{post_id}/",
                                'word_count': word_count
                            }
                            
                            documents.append(doc)
                            self.checkpoint.add_post(post_id)
                            posts_found += 1
                            
                    except Exception as e:
                        continue
                
                # Check for next page
                next_btn = soup.select_one('a.pageNav-jump--next')
                if not next_btn:
                    break
                    
                # Small delay between thread pages
                time.sleep(random.uniform(0.1, 0.2))
            
            self.checkpoint.add_thread(thread['thread_id'])
            
        except Exception as e:
            self.logger.error(f"Error processing thread: {e}")
        
        return documents
    
    def crawl(self, target_docs: int = 600000, output_file: str = 'data/voz_lightning.jsonl'):
        """Main crawl function"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Load checkpoint
        if self.checkpoint.load():
            self.logger.info(f"📂 Resumed from checkpoint: {self.checkpoint.total_docs} docs")
            mode = 'a'
        else:
            self.logger.info("🆕 Starting fresh crawl")
            mode = 'w'
        
        self.total_docs = self.checkpoint.total_docs
        start_time = datetime.now()
        
        self.logger.info(f"🚀 Starting crawler at {start_time.strftime('%H:%M:%S')}")
        self.logger.info(f"🔧 Workers: {self.num_workers}")
        self.logger.info(f"🎯 Target: {target_docs:,} documents")
        
        # Test connection
        scraper = self._create_scraper()
        test_html = self._get_page(scraper, self.BASE_URL)
        if not test_html or "Just a moment" in test_html:
            self.logger.error("❌ Cannot connect to Voz or Cloudflare blocking")
            return
        
        self.logger.info("✅ Connected to Voz!")
        
        # Find starting forum and page from checkpoint OR command line
        start_forum_idx = 0
        start_page = self.start_page  # Use command line arg first
        if start_page == 1 and self.checkpoint.last_forum:
            # Only use checkpoint if no explicit start-page given
            for idx, forum in enumerate(self.FORUMS):
                if forum == self.checkpoint.last_forum:
                    start_forum_idx = idx
                    start_page = self.checkpoint.last_page
                    break
        
        if start_page > 1:
            self.logger.info(f"📂 Starting from page {start_page}")
        
        with open(output_file, mode, encoding='utf-8') as f:
            with tqdm(total=target_docs, initial=self.total_docs, desc="Documents") as pbar:
                with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                    
                    for forum_idx, forum_url in enumerate(self.FORUMS):
                        if forum_idx < start_forum_idx:
                            continue
                        if self.total_docs >= target_docs:
                            break
                        
                        page = start_page if forum_idx == start_forum_idx else 1
                        start_page = 1  # Reset for next forums
                        max_pages = 5000  # Increased for 1M+ target
                        
                        while page <= max_pages and self.total_docs < target_docs:
                            self.logger.info(f"📂 Crawling {forum_url.split('/')[2]} page {page}")
                            
                            threads, total_on_page = self.get_thread_list(scraper, forum_url, page)
                            
                            if total_on_page == 0:
                                self.logger.info(f"   End of forum at page {page}")
                                break
                            
                            if not threads:
                                page += 1
                                continue
                            
                            # Submit threads to workers
                            futures = {executor.submit(self.crawl_thread, t): t for t in threads[:20]}
                            
                            for future in as_completed(futures):
                                if self.total_docs >= target_docs:
                                    break
                                
                                try:
                                    docs = future.result(timeout=60)
                                    for doc in docs:
                                        with self.file_lock:
                                            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
                                            f.flush()
                                        
                                        with self.stats_lock:
                                            self.total_docs += 1
                                        pbar.update(1)
                                        
                                except Exception as e:
                                    continue
                            
                            # Save checkpoint periodically
                            if page % 10 == 0:
                                self.checkpoint.total_docs = self.total_docs
                                self.checkpoint.last_forum = forum_url
                                self.checkpoint.last_page = page
                                self.checkpoint.save()
                                self.logger.info(f"💾 Checkpoint saved: {self.total_docs:,} docs (page {page})")
                            
                            page += 1
        
        # Final checkpoint
        self.checkpoint.total_docs = self.total_docs
        self.checkpoint.save()
        
        duration = (datetime.now() - start_time).total_seconds() / 60
        self.logger.info(f"\n✅ Crawl completed! {self.total_docs:,} documents in {duration:.1f} minutes")
        self.logger.info(f"📁 Output: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Voz Crawler for Lightning AI')
    parser.add_argument('--target', type=int, default=1200000, help='Target documents (default: 1.2M)')
    parser.add_argument('--workers', type=int, default=10, help='Number of workers')
    parser.add_argument('--output', type=str, default='data/voz_lightning.jsonl', help='Output file')
    parser.add_argument('--min-words', type=int, default=50, help='Minimum word count')
    parser.add_argument('--start-page', type=int, default=1, help='Start from this page (skip earlier pages)')
    
    args = parser.parse_args()
    
    crawler = VozCrawler(
        num_workers=args.workers,
        min_word_count=args.min_words,
        start_page=args.start_page
    )
    
    crawler.crawl(target_docs=args.target, output_file=args.output)


if __name__ == "__main__":
    main()

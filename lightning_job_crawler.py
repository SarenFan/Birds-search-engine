#!/usr/bin/env python3
"""
Lightning.ai Job Crawler - Optimized cho background execution
Chạy script này trên Lightning Studios để crawl data background

Author: Phan Minh Tai
Date: 2026-01-10
"""
import os
import sys
import json
import time
import signal
from pathlib import Path
from datetime import datetime
import multiprocessing as mp

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.crawler.voz_selenium_crawler import ImprovedVozCrawler
from src.crawler.tinhte_selenium_crawler import ImprovedTinhTeCrawler
from src.crawler.spiderum_selenium_crawler import ImprovedSpiderumCrawler
from src.crawler.selenium_utils import SeleniumCrawler


class LightningJobCrawler:
    """
    Crawler Manager cho Lightning.ai Jobs
    - Tự động lưu data vào thư mục artifacts
    - Checkpoint system cho resume
    - Multi-process crawling
    """

    def __init__(self):
        # Lightning.ai tự động tạo /data và /checkpoints
        # Data sẽ được lưu tại đây để download sau
        self.data_dir = Path("/tmp/lightning_artifacts/data")
        self.checkpoint_dir = Path("/tmp/lightning_artifacts/checkpoints")

        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.processes = []
        self.start_time = time.time()

        print("=" * 80)
        print("🚀 LIGHTNING.AI JOB CRAWLER")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data directory: {self.data_dir}")
        print(f"Checkpoint directory: {self.checkpoint_dir}")
        print(f"Process ID: {os.getpid()}")
        print("=" * 80)

    def run_voz_crawler(self, max_docs=400000):
        """Crawl Voz forum"""
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔵 Starting Voz Crawler...")
            print(f"Target: {max_docs:,} documents")

            crawler = ImprovedVozCrawler(
                output_file=str(self.data_dir / 'voz_data.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'voz_checkpoint.json'),
                max_docs=max_docs,
                headless=True  # Always headless on cloud
            )

            driver = SeleniumCrawler(headless=True)

            # Crawl multiple forums
            forums = [
                ("F17-OffTopic", "https://voz.vn/f/chuyen-tro-linh-tinh.17/", 1500),
                ("F33-AutoMoto", "https://voz.vn/f/xe-co.33/", 1000),
            ]

            for forum_name, forum_url, max_pages in forums:
                print(f"\n📁 Crawling {forum_name}...")
                crawler.crawl_forum(
                    crawler=driver,
                    forum_name=forum_name,
                    forum_url=forum_url,
                    max_pages=max_pages
                )

                # Check if reached max docs
                if crawler.docs_collected >= max_docs:
                    print(f"✅ Reached max docs: {crawler.docs_collected:,}")
                    break

            driver.close()

            elapsed = time.time() - self.start_time
            print(f"\n✅ Voz Crawler COMPLETED!")
            print(f"   Documents: {crawler.docs_collected:,}")
            print(f"   Time: {elapsed/3600:.2f} hours")
            print(f"   Output: {self.data_dir / 'voz_data.jsonl'}")

        except Exception as e:
            print(f"\n❌ Voz Crawler ERROR: {e}")
            import traceback
            traceback.print_exc()

    def run_tinhte_crawler(self, max_docs=300000):
        """Crawl TinhTe forum"""
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🟢 Starting TinhTe Crawler...")
            print(f"Target: {max_docs:,} documents")

            crawler = ImprovedTinhTeCrawler(
                output_file=str(self.data_dir / 'tinhte_data.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'tinhte_checkpoint.json'),
                max_docs=max_docs,
                headless=True
            )

            driver = SeleniumCrawler(headless=True)

            crawler.crawl_forum(
                crawler=driver,
                forum_url="https://tinhte.vn/forums/",
                max_pages=1500
            )

            driver.close()

            elapsed = time.time() - self.start_time
            print(f"\n✅ TinhTe Crawler COMPLETED!")
            print(f"   Documents: {crawler.docs_collected:,}")
            print(f"   Time: {elapsed/3600:.2f} hours")
            print(f"   Output: {self.data_dir / 'tinhte_data.jsonl'}")

        except Exception as e:
            print(f"\n❌ TinhTe Crawler ERROR: {e}")
            import traceback
            traceback.print_exc()

    def run_spiderum_crawler(self, max_docs=200000):
        """Crawl Spiderum articles"""
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🟣 Starting Spiderum Crawler...")
            print(f"Target: {max_docs:,} documents")

            crawler = ImprovedSpiderumCrawler(
                output_file=str(self.data_dir / 'spiderum_data.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'spiderum_checkpoint.json'),
                max_docs=max_docs,
                headless=True
            )

            driver = SeleniumCrawler(headless=True)

            # Crawl multiple categories
            categories = [
                "https://spiderum.com/khoa-hoc",
                "https://spiderum.com/cong-nghe",
                "https://spiderum.com/kinh-doanh",
            ]

            for category_url in categories:
                print(f"\n📁 Crawling {category_url}...")
                crawler.crawl_category(
                    crawler=driver,
                    category_url=category_url
                )

                if crawler.docs_collected >= max_docs:
                    break

            driver.close()

            elapsed = time.time() - self.start_time
            print(f"\n✅ Spiderum Crawler COMPLETED!")
            print(f"   Documents: {crawler.docs_collected:,}")
            print(f"   Time: {elapsed/3600:.2f} hours")
            print(f"   Output: {self.data_dir / 'spiderum_data.jsonl'}")

        except Exception as e:
            print(f"\n❌ Spiderum Crawler ERROR: {e}")
            import traceback
            traceback.print_exc()

    def run_sequential(self):
        """
        Run crawlers sequentially (safer for limited resources)
        """
        print("\n🔄 Running crawlers SEQUENTIALLY...")
        print("This ensures stable execution on limited resources\n")

        # Run one by one
        self.run_voz_crawler(max_docs=400000)
        time.sleep(10)  # Cooldown

        self.run_tinhte_crawler(max_docs=300000)
        time.sleep(10)

        self.run_spiderum_crawler(max_docs=200000)

        self.print_summary()

    def run_parallel(self, num_workers=2):
        """
        Run crawlers in parallel (faster but needs more resources)

        Args:
            num_workers: Number of parallel crawlers
                        2 for FREE 4-core Studio
                        3-4 for Paid 8+ core Studio
        """
        print(f"\n⚡ Running {num_workers} crawlers in PARALLEL...")
        print("This is faster but requires adequate CPU/RAM\n")

        # Select crawlers based on num_workers
        crawler_configs = [
            (self.run_voz_crawler, {"max_docs": 400000}),
            (self.run_tinhte_crawler, {"max_docs": 300000}),
            (self.run_spiderum_crawler, {"max_docs": 200000}),
        ][:num_workers]

        # Start processes
        for func, kwargs in crawler_configs:
            p = mp.Process(target=func, kwargs=kwargs, name=func.__name__)
            p.start()
            self.processes.append(p)
            print(f"✓ Started {func.__name__} (PID: {p.pid})")
            time.sleep(5)  # Stagger starts

        # Monitor
        self.monitor_processes()
        self.print_summary()

    def monitor_processes(self):
        """Monitor running processes"""
        print("\n📊 Monitoring crawlers...")
        print("Press Ctrl+C to stop all crawlers gracefully\n")

        try:
            while any(p.is_alive() for p in self.processes):
                time.sleep(60)  # Check every minute

                # Print status
                alive = [p.name for p in self.processes if p.is_alive()]
                if alive:
                    elapsed = time.time() - self.start_time
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Running: {', '.join(alive)} | "
                          f"Elapsed: {elapsed/3600:.1f}h")

                    # Print progress from checkpoints
                    self.print_checkpoint_progress()

            print("\n✅ All crawlers completed!")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user - stopping crawlers...")
            self.stop_all()

    def print_checkpoint_progress(self):
        """Print progress from checkpoint files"""
        total_docs = 0

        for checkpoint_file in self.checkpoint_dir.glob('*_checkpoint.json'):
            try:
                with open(checkpoint_file) as f:
                    data = json.load(f)
                    docs = data.get('docs_collected', 0)
                    total_docs += docs
                    print(f"   {checkpoint_file.stem}: {docs:,} docs")
            except:
                pass

        print(f"   TOTAL: {total_docs:,} docs")

    def print_summary(self):
        """Print final summary"""
        elapsed = time.time() - self.start_time

        print("\n" + "=" * 80)
        print("📊 CRAWLING SUMMARY")
        print("=" * 80)

        total_docs = 0
        total_size = 0

        # Count docs and size
        for data_file in self.data_dir.glob('*.jsonl'):
            if data_file.exists():
                size_mb = data_file.stat().st_size / (1024 * 1024)
                total_size += size_mb

                # Count lines
                with open(data_file) as f:
                    num_docs = sum(1 for _ in f)
                    total_docs += num_docs

                print(f"✓ {data_file.name}:")
                print(f"  - Documents: {num_docs:,}")
                print(f"  - Size: {size_mb:.2f} MB")

        print(f"\nTOTAL:")
        print(f"  - Documents: {total_docs:,}")
        print(f"  - Size: {total_size:.2f} MB")
        print(f"  - Time: {elapsed/3600:.2f} hours")
        print(f"  - Speed: {total_docs/(elapsed/3600):.0f} docs/hour")

        print(f"\n📁 Data location: {self.data_dir}")
        print("To download: See Lightning.ai dashboard → Artifacts")
        print("=" * 80)

    def stop_all(self):
        """Stop all processes gracefully"""
        for p in self.processes:
            if p.is_alive():
                print(f"Stopping {p.name}...")
                p.terminate()
                p.join(timeout=30)
        print("✓ All crawlers stopped")


def main():
    """Main entry point"""
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Lightning.ai Job Crawler for SEG301 Project'
    )
    parser.add_argument(
        '--mode',
        choices=['sequential', 'parallel'],
        default='sequential',
        help='Run mode: sequential (safer) or parallel (faster)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=2,
        help='Number of parallel workers (only for parallel mode)'
    )

    args = parser.parse_args()

    # Create crawler manager
    manager = LightningJobCrawler()

    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        print("\n⚠️  Signal received - stopping...")
        manager.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run based on mode
    if args.mode == 'sequential':
        manager.run_sequential()
    else:
        manager.run_parallel(num_workers=args.workers)

    print("\n🎉 Job completed successfully!")
    print("Check /tmp/lightning_artifacts/data/ for output files")


if __name__ == "__main__":
    # Set multiprocessing start method
    mp.set_start_method('spawn', force=True)
    main()

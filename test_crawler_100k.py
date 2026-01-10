#!/usr/bin/env python3
"""
Test Crawler - 100K docs với 4 luồng song song
Chạy trên Lightning.ai để verify setup trước khi chạy production

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


class TestCrawler100K:
    """
    Test crawler cho 100K docs
    - VOZ: 40K docs
    - TinhTe: 30K docs
    - Spiderum: 20K docs
    - Otofun: 10K docs (optional)
    """

    def __init__(self):
        self.data_dir = Path("/tmp/lightning_artifacts/test_data")
        self.checkpoint_dir = Path("/tmp/lightning_artifacts/test_checkpoints")

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.processes = []
        self.start_time = time.time()

        print("=" * 80)
        print("🧪 TEST CRAWLER - 100K DOCUMENTS")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data directory: {self.data_dir}")
        print(f"Checkpoint directory: {self.checkpoint_dir}")
        print("")
        print("Target Distribution:")
        print("  - VOZ:      40,000 docs")
        print("  - TinhTe:   30,000 docs")
        print("  - Spiderum: 20,000 docs")
        print("  - Otofun:   10,000 docs")
        print("  TOTAL:     100,000 docs")
        print("=" * 80)

    def run_voz_test(self):
        """Crawl VOZ - Target 40K docs"""
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔵 Starting VOZ Test Crawler...")
            print(f"Target: 40,000 documents")

            crawler = ImprovedVozCrawler(
                output_file=str(self.data_dir / 'test_voz.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'test_voz_checkpoint.json'),
                max_docs=40000,
                headless=True
            )

            # Create driver inside each process to avoid pickle issues
            # Use system ChromeDriver on Lightning.ai
            from src.crawler.selenium_utils import SeleniumCrawler
            driver = SeleniumCrawler(headless=True, driver_path=f"{Path.home()}/.local/bin/chromedriver")

            try:
                # Crawl F17 only (most active forum)
                crawler.crawl_forum(
                    crawler=driver,
                    forum_name="F17-OffTopic-Test",
                    forum_url="https://voz.vn/f/chuyen-tro-linh-tinh.17/",
                    max_pages=200  # Limit pages for test
                )
            finally:
                if driver and driver.driver:
                    driver.driver.quit()

            elapsed = time.time() - self.start_time
            print(f"\n✅ VOZ Test COMPLETED!")
            print(f"   Documents: {crawler.docs_collected:,}")
            print(f"   Time: {elapsed/3600:.2f} hours")

        except Exception as e:
            print(f"\n❌ VOZ Test ERROR: {e}")
            import traceback
            traceback.print_exc()

    def run_tinhte_test(self):
        """Crawl TinhTe - Target 30K docs"""
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🟢 Starting TinhTe Test Crawler...")
            print(f"Target: 30,000 documents")

            crawler = ImprovedTinhTeCrawler(
                output_file=str(self.data_dir / 'test_tinhte.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'test_tinhte_checkpoint.json'),
                max_docs=30000,
                headless=True
            )

            from src.crawler.selenium_utils import SeleniumCrawler
            driver = SeleniumCrawler(headless=True, driver_path=f"{Path.home()}/.local/bin/chromedriver")

            try:
                crawler.crawl_forum(
                    crawler=driver,
                    forum_url="https://tinhte.vn/forums/",
                    max_pages=150
                )
            finally:
                if driver and driver.driver:
                    driver.driver.quit()

            elapsed = time.time() - self.start_time
            print(f"\n✅ TinhTe Test COMPLETED!")
            print(f"   Documents: {crawler.docs_collected:,}")
            print(f"   Time: {elapsed/3600:.2f} hours")

        except Exception as e:
            print(f"\n❌ TinhTe Test ERROR: {e}")
            import traceback
            traceback.print_exc()

    def run_spiderum_test(self):
        """Crawl Spiderum - Target 20K docs"""
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🟣 Starting Spiderum Test Crawler...")
            print(f"Target: 20,000 documents")

            crawler = ImprovedSpiderumCrawler(
                output_file=str(self.data_dir / 'test_spiderum.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'test_spiderum_checkpoint.json'),
                max_docs=20000,
                headless=True
            )

            from src.crawler.selenium_utils import SeleniumCrawler
            driver = SeleniumCrawler(headless=True, driver_path=f"{Path.home()}/.local/bin/chromedriver")

            try:
                # Crawl main categories
                crawler.crawl_category(
                    crawler=driver,
                    category_url="https://spiderum.com/khoa-hoc"
                )
            finally:
                if driver and driver.driver:
                    driver.driver.quit()

            elapsed = time.time() - self.start_time
            print(f"\n✅ Spiderum Test COMPLETED!")
            print(f"   Documents: {crawler.docs_collected:,}")
            print(f"   Time: {elapsed/3600:.2f} hours")

        except Exception as e:
            print(f"\n❌ Spiderum Test ERROR: {e}")
            import traceback
            traceback.print_exc()

    def run_otofun_test(self):
        """Crawl Otofun - Target 10K docs (optional)"""
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🟠 Starting Otofun Test Crawler...")
            print(f"Target: 10,000 documents")
            print("⚠️  Otofun may have anti-scraping - this is a test")

            # Mock crawl for now (Otofun có thể khó crawl)
            time.sleep(5)
            print("\n⚠️  Otofun crawler skipped in test (difficult to crawl)")
            print("   Will focus on VOZ/TinhTe/Spiderum for 90K docs")

        except Exception as e:
            print(f"\n❌ Otofun Test ERROR: {e}")

    def run_parallel_test(self):
        """Run 4 test crawlers in parallel"""
        print("\n⚡ Starting 4 test crawlers in PARALLEL...")
        print("This will run in background. Check progress with:")
        print("  tail -f /tmp/test_crawler.log")
        print("  cat /tmp/lightning_artifacts/test_checkpoints/*.json")
        print("")

        # Start 3 main crawlers (skip Otofun for test)
        crawler_configs = [
            (self.run_voz_test, "VOZ"),
            (self.run_tinhte_test, "TinhTe"),
            (self.run_spiderum_test, "Spiderum"),
        ]

        for func, name in crawler_configs:
            p = mp.Process(target=func, name=f'Test-{name}')
            p.start()
            self.processes.append(p)
            print(f"✓ Started {name} test crawler (PID: {p.pid})")
            time.sleep(5)  # Stagger starts

        print(f"\n✅ All {len(self.processes)} test crawlers started!")
        print("\nYou can now disconnect - crawlers will run in background")

        # Monitor
        self.monitor_test()

    def monitor_test(self):
        """Monitor test crawler progress"""
        print("\n📊 Monitoring test crawlers...")
        print("Press Ctrl+C to stop monitoring (crawlers will continue)\n")

        try:
            while any(p.is_alive() for p in self.processes):
                time.sleep(60)  # Check every minute

                alive = [p.name for p in self.processes if p.is_alive()]
                if alive:
                    elapsed = time.time() - self.start_time
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Running: {', '.join(alive)} | "
                          f"Elapsed: {elapsed/3600:.1f}h")

                    # Print progress
                    self.print_progress()

            print("\n✅ All test crawlers completed!")
            self.print_summary()

        except KeyboardInterrupt:
            print("\n⚠️  Monitoring stopped (crawlers still running)")
            print("To check status: ssh into Studio and run:")
            print("  ps aux | grep Test-")
            print("  cat /tmp/lightning_artifacts/test_checkpoints/*.json")

    def print_progress(self):
        """Print progress from checkpoints"""
        total_docs = 0

        for checkpoint_file in self.checkpoint_dir.glob('*_checkpoint.json'):
            try:
                with open(checkpoint_file) as f:
                    data = json.load(f)
                    docs = data.get('docs_collected', 0)
                    total_docs += docs
                    name = checkpoint_file.stem.replace('test_', '').replace('_checkpoint', '')
                    print(f"   {name}: {docs:,} docs")
            except:
                pass

        print(f"   TOTAL: {total_docs:,} / 100,000 docs ({total_docs/1000:.1f}%)")

    def print_summary(self):
        """Print final summary"""
        elapsed = time.time() - self.start_time

        print("\n" + "=" * 80)
        print("📊 TEST CRAWLING SUMMARY")
        print("=" * 80)

        total_docs = 0
        total_size = 0

        for data_file in self.data_dir.glob('test_*.jsonl'):
            if data_file.exists():
                size_mb = data_file.stat().st_size / (1024 * 1024)
                total_size += size_mb

                with open(data_file) as f:
                    num_docs = sum(1 for _ in f)
                    total_docs += num_docs

                name = data_file.stem.replace('test_', '')
                print(f"✓ {name}:")
                print(f"  - Documents: {num_docs:,}")
                print(f"  - Size: {size_mb:.2f} MB")

        print(f"\nTOTAL:")
        print(f"  - Documents: {total_docs:,} / 100,000 ({total_docs/1000:.1f}%)")
        print(f"  - Size: {total_size:.2f} MB")
        print(f"  - Time: {elapsed/3600:.2f} hours")

        if total_docs > 0:
            print(f"  - Speed: {total_docs/(elapsed/3600):.0f} docs/hour")

            # Extrapolate to 1M
            if total_docs >= 10000:  # At least 10K for reasonable estimate
                hours_for_1m = (1000000 / total_docs) * (elapsed / 3600)
                days_for_1m = hours_for_1m / 24
                print(f"\n📈 Extrapolation to 1M docs:")
                print(f"  - Estimated time: {days_for_1m:.1f} days")
                print(f"  - At current speed: {total_docs/(elapsed/3600):.0f} docs/hour")

        print(f"\n📁 Data location: {self.data_dir}")
        print("=" * 80)

    def stop_all(self):
        """Stop all test crawlers"""
        for p in self.processes:
            if p.is_alive():
                print(f"Stopping {p.name}...")
                p.terminate()
                p.join(timeout=30)
        print("✓ All test crawlers stopped")


def main():
    """Main entry point"""
    print("\n🧪 TEST MODE: 100K Documents with 4 Parallel Crawlers\n")

    manager = TestCrawler100K()

    # Handle signals
    def signal_handler(sig, frame):
        print("\n⚠️  Signal received - stopping...")
        manager.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run test
    manager.run_parallel_test()

    print("\n🎉 Test completed!")
    print("Check results in /tmp/lightning_artifacts/test_data/")


if __name__ == "__main__":
    mp.set_start_method('spawn', force=True)
    main()

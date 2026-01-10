#!/usr/bin/env python3
"""
Simple 100K Test Crawler - Standalone functions for multiprocessing
Runs 3 crawlers in parallel: VOZ (40K), TinhTe (30K), Spiderum (20K)
"""
import sys
import time
import multiprocessing as mp
from pathlib import Path
from datetime import datetime


def crawl_voz_standalone():
    """Standalone VOZ crawler for multiprocessing"""
    try:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔵 VOZ Crawler Started (PID: {mp.current_process().pid})")
        
        # Import here to avoid pickle issues
        from src.crawler.voz_selenium_crawler import ImprovedVozCrawler
        from src.crawler.selenium_utils import SeleniumCrawler
        
        data_dir = Path("/tmp/lightning_artifacts/test_data")
        checkpoint_dir = Path("/tmp/lightning_artifacts/test_checkpoints")
        data_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        crawler = ImprovedVozCrawler(
            output_file=str(data_dir / 'test_voz.jsonl'),
            checkpoint_file=str(checkpoint_dir / 'test_voz_checkpoint.json'),
            max_docs=40000,
            headless=True
        )
        
        driver = SeleniumCrawler(headless=True, driver_path=f"{Path.home()}/.local/bin/chromedriver")
        
        try:
            crawler.crawl_forum(
                crawler=driver,
                forum_name="F17-OffTopic",
                forum_url="https://voz.vn/f/chuyen-tro-linh-tinh.17/",
                max_pages=200
            )
        finally:
            if driver and driver.driver:
                driver.driver.quit()
        
        print(f"\n✅ VOZ Crawler COMPLETED! Docs: {crawler.docs_collected:,}")
        
    except Exception as e:
        print(f"\n❌ VOZ Crawler ERROR: {e}")
        import traceback
        traceback.print_exc()


def crawl_tinhte_standalone():
    """Standalone TinhTe crawler for multiprocessing"""
    try:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🟢 TinhTe Crawler Started (PID: {mp.current_process().pid})")
        
        from src.crawler.tinhte_selenium_crawler import ImprovedTinhTeCrawler
        from src.crawler.selenium_utils import SeleniumCrawler
        
        data_dir = Path("/tmp/lightning_artifacts/test_data")
        checkpoint_dir = Path("/tmp/lightning_artifacts/test_checkpoints")
        data_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        crawler = ImprovedTinhTeCrawler(
            output_file=str(data_dir / 'test_tinhte.jsonl'),
            checkpoint_file=str(checkpoint_dir / 'test_tinhte_checkpoint.json'),
            max_docs=30000,
            headless=True
        )
        
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
        
        print(f"\n✅ TinhTe Crawler COMPLETED! Docs: {crawler.docs_collected:,}")
        
    except Exception as e:
        print(f"\n❌ TinhTe Crawler ERROR: {e}")
        import traceback
        traceback.print_exc()


def crawl_spiderum_standalone():
    """Standalone Spiderum crawler for multiprocessing"""
    try:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🟣 Spiderum Crawler Started (PID: {mp.current_process().pid})")
        
        from src.crawler.spiderum_selenium_crawler import ImprovedSpiderumCrawler
        from src.crawler.selenium_utils import SeleniumCrawler
        
        data_dir = Path("/tmp/lightning_artifacts/test_data")
        checkpoint_dir = Path("/tmp/lightning_artifacts/test_checkpoints")
        data_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        crawler = ImprovedSpiderumCrawler(
            output_file=str(data_dir / 'test_spiderum.jsonl'),
            checkpoint_file=str(checkpoint_dir / 'test_spiderum_checkpoint.json'),
            max_docs=20000,
            headless=True
        )
        
        driver = SeleniumCrawler(headless=True, driver_path=f"{Path.home()}/.local/bin/chromedriver")
        
        try:
            crawler.crawl_category(
                crawler=driver,
                category_url="https://spiderum.com/khoa-hoc"
            )
        finally:
            if driver and driver.driver:
                driver.driver.quit()
        
        print(f"\n✅ Spiderum Crawler COMPLETED! Docs: {crawler.docs_collected:,}")
        
    except Exception as e:
        print(f"\n❌ Spiderum Crawler ERROR: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to start all crawlers"""
    print("""
🧪 SIMPLE 100K TEST - 3 PARALLEL CRAWLERS
==========================================
Started at: {}
Target: 90,000 documents (VOZ 40K + TinhTe 30K + Spiderum 20K)

Data: /tmp/lightning_artifacts/test_data/
Checkpoints: /tmp/lightning_artifacts/test_checkpoints/
==========================================
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    # Start 3 crawlers
    processes = []
    
    crawlers = [
        (crawl_voz_standalone, "VOZ"),
        (crawl_tinhte_standalone, "TinhTe"),
        (crawl_spiderum_standalone, "Spiderum"),
    ]
    
    for func, name in crawlers:
        p = mp.Process(target=func, name=f'Crawler-{name}')
        p.start()
        processes.append(p)
        print(f"✓ Started {name} crawler (PID: {p.pid})")
        time.sleep(3)  # Stagger starts
    
    print(f"\n✅ All {len(processes)} crawlers started!")
    print("\n📊 Monitor progress:")
    print("  tail -f /tmp/test_crawler.log")
    print("  watch -n 5 'ls -lh /tmp/lightning_artifacts/test_data/'")
    print("  watch -n 5 'wc -l /tmp/lightning_artifacts/test_data/*.jsonl'")
    
    # Wait for all to complete
    for p in processes:
        p.join()
    
    print("\n✅ All crawlers finished!")


if __name__ == "__main__":
    main()

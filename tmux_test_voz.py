#!/usr/bin/env python3
"""
Single VOZ crawler test - chạy được trong tmux
"""
from pathlib import Path
from src.crawler.voz_selenium_crawler import ImprovedVozCrawler  
from src.crawler.selenium_utils import SeleniumCrawler
import sys

print('[VOZ] Starting test crawler...', flush=True)

data_dir = Path('/tmp/lightning_artifacts/test_data')
checkpoint_dir = Path('/tmp/lightning_artifacts/test_checkpoints')
data_dir.mkdir(parents=True, exist_ok=True)
checkpoint_dir.mkdir(parents=True, exist_ok=True)

print('[VOZ] Directories created', flush=True)

crawler = ImprovedVozCrawler(
    output_file=str(data_dir / 'voz_tmux_test.jsonl'),
    checkpoint_file=str(checkpoint_dir / 'voz_tmux_test.json'),
    max_docs=50,  # Test with 50 docs
    headless=True
)

print('[VOZ] Crawler initialized', flush=True)

driver = SeleniumCrawler(headless=True, driver_path=f'{Path.home()}/.local/bin/chromedriver')

print('[VOZ] Driver initialized', flush=True)

try:
    print('[VOZ] Starting crawl...', flush=True)
    crawler.crawl_forum(
        crawler=driver,
        forum_name='F17-Test',
        forum_url='https://voz.vn/f/chuyen-tro-linh-tinh.17/',
        max_pages=3
    )
    print(f'[VOZ] ✅ COMPLETED! Docs: {crawler.docs_collected}', flush=True)
except Exception as e:
    print(f'[VOZ] ❌ ERROR: {e}', flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    if driver and driver.driver:
        driver.driver.quit()
        print('[VOZ] Driver closed', flush=True)

print('[VOZ] Test finished successfully!', flush=True)

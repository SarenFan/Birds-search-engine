"""
Test improved Selenium-based crawlers
"""
from src.crawler.voz_selenium_crawler import ImprovedVozCrawler
from src.crawler.tinhte_selenium_crawler import ImprovedTinhTeCrawler
from src.crawler.spiderum_selenium_crawler import ImprovedSpiderumCrawler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_single_crawler(crawler_class, name: str, max_docs: int = 10):
    """Test a single crawler"""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing {name} Crawler")
    logger.info(f"{'='*80}\n")

    try:
        crawler = crawler_class(max_docs=max_docs, headless=True)
        stats = crawler.run()

        logger.info(f"\n{name} Results:")
        logger.info(f"  Documents collected: {stats['docs_collected']}")
        logger.info(f"  Duration: {stats['duration']:.2f}s")
        logger.info(f"  Success: {'✓' if stats['docs_collected'] > 0 else '✗'}")

        return stats
    except Exception as e:
        logger.error(f"{name} failed: {e}")
        return {'source': name, 'docs_collected': 0, 'duration': 0, 'docs_per_second': 0}


def main():
    """Test all improved crawlers"""
    print("\n" + "="*80)
    print("TESTING IMPROVED SELENIUM CRAWLERS")
    print("="*80 + "\n")

    results = []

    # Test Voz
    results.append(test_single_crawler(ImprovedVozCrawler, "Voz", max_docs=10))

    # Test TinhTe
    results.append(test_single_crawler(ImprovedTinhTeCrawler, "TinhTe", max_docs=10))

    # Test Spiderum
    results.append(test_single_crawler(ImprovedSpiderumCrawler, "Spiderum", max_docs=10))

    # Summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)

    total_docs = sum(r['docs_collected'] for r in results)
    total_time = sum(r['duration'] for r in results)

    for result in results:
        status = "✓ SUCCESS" if result['docs_collected'] > 0 else "✗ FAILED"
        print(f"{result['source']:20} {status:12} {result['docs_collected']:5} docs in {result['duration']:.1f}s")

    print("-"*80)
    print(f"{'TOTAL':20} {'':<12} {total_docs:5} docs in {total_time:.1f}s")

    if total_docs > 0:
        print(f"\n✅ Success! Collected {total_docs} documents")
        print(f"📈 Average speed: {total_docs/total_time:.2f} docs/second")
    else:
        print(f"\n❌ Failed to collect any documents. Check logs for errors.")

    print("="*80 + "\n")


if __name__ == '__main__':
    main()

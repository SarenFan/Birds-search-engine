"""
Master Crawler - Run all crawlers and analyze results
"""
import asyncio
from datetime import datetime
import json
from typing import Dict, List

from src.crawler.voz_crawler import VozCrawler
from src.crawler.tinhte_crawler import TinhTeCrawler
from src.crawler.otofun_crawler import OtofunCrawler
from src.crawler.spiderum_crawler import SpiderumCrawler


async def run_all_crawlers(max_docs_per_source: int = 100):
    """Run all crawlers concurrently"""
    print("="*80)
    print("STARTING SOCIAL LISTENING DATA COLLECTION")
    print("="*80)
    print(f"Target: {max_docs_per_source} documents per source")
    print(f"Total target: {max_docs_per_source * 4} documents")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    start_time = datetime.now()

    # Run all crawlers concurrently
    results = await asyncio.gather(
        run_voz_crawler(max_docs_per_source),
        run_tinhte_crawler(max_docs_per_source),
        run_otofun_crawler(max_docs_per_source),
        run_spiderum_crawler(max_docs_per_source),
        return_exceptions=True
    )

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    # Process results
    stats = []
    total_docs = 0

    for result in results:
        if isinstance(result, dict):
            stats.append(result)
            total_docs += result['docs_collected']
        else:
            print(f"Error in crawler: {result}")

    # Print summary
    print("\n" + "="*80)
    print("CRAWLING COMPLETED - SUMMARY REPORT")
    print("="*80)

    for stat in stats:
        print(f"\n{stat['source'].upper()}:")
        print(f"  Documents collected: {stat['docs_collected']}")
        print(f"  Duration: {stat['duration']:.2f} seconds")
        print(f"  Speed: {stat['docs_per_second']:.2f} docs/second")

    print("\n" + "-"*80)
    print(f"TOTAL DOCUMENTS: {total_docs}")
    print(f"TOTAL DURATION: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print(f"AVERAGE SPEED: {total_docs/total_duration:.2f} docs/second")

    # Calculate projection for 1 million docs
    print("\n" + "="*80)
    print("PROJECTION FOR 1,000,000 DOCUMENTS")
    print("="*80)

    if total_docs > 0:
        avg_speed = total_docs / total_duration
        time_for_1m = 1_000_000 / avg_speed

        hours = int(time_for_1m // 3600)
        minutes = int((time_for_1m % 3600) // 60)
        seconds = int(time_for_1m % 60)

        print(f"Average speed: {avg_speed:.2f} docs/second")
        print(f"Estimated time for 1M docs: {hours}h {minutes}m {seconds}s")
        print(f"Estimated time: {time_for_1m/3600:.2f} hours = {time_for_1m/86400:.2f} days")

        # Per source calculation
        docs_per_source = 250_000  # 1M / 4 sources
        time_per_source = docs_per_source / avg_speed
        print(f"\nPer source (250K docs each):")
        print(f"  Estimated time: {time_per_source/3600:.2f} hours = {time_per_source/86400:.2f} days")

        # Recommendations
        print("\n" + "-"*80)
        print("RECOMMENDATIONS:")
        print("-"*80)
        if time_for_1m > 86400 * 7:  # More than 7 days
            print("⚠️  Current speed is too slow for 1M docs in reasonable time!")
            print("💡 Suggestions:")
            print("   1. Increase concurrent requests (use semaphore with higher limit)")
            print("   2. Use multiple IP addresses/proxies")
            print("   3. Reduce sleep time between requests")
            print("   4. Use distributed crawling (multiple machines)")
            print("   5. Consider relaxing the 50-word minimum requirement")
        elif time_for_1m > 86400 * 3:  # 3-7 days
            print("✓  Speed is acceptable but can be improved")
            print("💡 Consider increasing concurrency for faster results")
        else:
            print("✓  Excellent speed! On track to complete in reasonable time")

    print("="*80 + "\n")

    # Save summary to JSON
    summary = {
        'test_date': datetime.now().isoformat(),
        'test_config': {
            'docs_per_source': max_docs_per_source,
            'total_target': max_docs_per_source * 4
        },
        'results': stats,
        'total': {
            'docs_collected': total_docs,
            'duration_seconds': total_duration,
            'avg_speed': total_docs / total_duration if total_duration > 0 else 0
        },
        'projection': {
            'target_docs': 1_000_000,
            'estimated_seconds': 1_000_000 / (total_docs / total_duration) if total_docs > 0 else 0,
            'estimated_hours': (1_000_000 / (total_docs / total_duration)) / 3600 if total_docs > 0 else 0,
            'estimated_days': (1_000_000 / (total_docs / total_duration)) / 86400 if total_docs > 0 else 0
        }
    }

    with open('data_sample/crawl_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("📊 Summary saved to data_sample/crawl_summary.json\n")

    return summary


async def run_voz_crawler(max_docs: int):
    """Run Voz crawler"""
    try:
        async with VozCrawler(max_docs=max_docs) as crawler:
            return await crawler.run()
    except Exception as e:
        print(f"Voz crawler error: {e}")
        return {'source': 'voz', 'docs_collected': 0, 'duration': 0, 'docs_per_second': 0}


async def run_tinhte_crawler(max_docs: int):
    """Run TinhTe crawler"""
    try:
        async with TinhTeCrawler(max_docs=max_docs) as crawler:
            return await crawler.run()
    except Exception as e:
        print(f"TinhTe crawler error: {e}")
        return {'source': 'tinhte', 'docs_collected': 0, 'duration': 0, 'docs_per_second': 0}


async def run_otofun_crawler(max_docs: int):
    """Run Otofun crawler"""
    try:
        async with OtofunCrawler(max_docs=max_docs) as crawler:
            return await crawler.run()
    except Exception as e:
        print(f"Otofun crawler error: {e}")
        return {'source': 'otofun', 'docs_collected': 0, 'duration': 0, 'docs_per_second': 0}


async def run_spiderum_crawler(max_docs: int):
    """Run Spiderum crawler"""
    try:
        async with SpiderumCrawler(max_docs=max_docs) as crawler:
            return await crawler.run()
    except Exception as e:
        print(f"Spiderum crawler error: {e}")
        return {'source': 'spiderum', 'docs_collected': 0, 'duration': 0, 'docs_per_second': 0}


def main():
    """Main entry point"""
    # Test with 100 docs per source
    asyncio.run(run_all_crawlers(max_docs_per_source=100))


if __name__ == '__main__':
    main()

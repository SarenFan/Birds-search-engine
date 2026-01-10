"""
Quick test crawler - Run all crawlers with smaller dataset
"""
import asyncio
from src.run_crawlers import run_all_crawlers


def main():
    """Test with smaller dataset (25 docs per source)"""
    asyncio.run(run_all_crawlers(max_docs_per_source=25))


if __name__ == '__main__':
    main()

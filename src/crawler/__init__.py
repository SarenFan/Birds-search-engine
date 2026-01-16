"""
Milestone 1: Data Acquisition
Web crawlers for Vietnamese forums

Successfully crawled 1,110,701 documents from Voz Forum

Crawlers:
- voz_crawler_1m.py: Production crawler with multi-threading, checkpoint/resume
- voz_crawler_lightning.py: Lightning AI optimized version (31 forums, multi-page threads)

Usage:
    # Local crawling
    python voz_crawler_1m.py --target 1000000 --workers 15

    # Lightning AI (no Cloudflare blocks)
    python voz_crawler_lightning.py --target 1200000 --workers 15
"""

from .voz_crawler_1m import VozProductionCrawler
from .voz_crawler_lightning import VozCrawler

__all__ = ['VozProductionCrawler', 'VozCrawler']

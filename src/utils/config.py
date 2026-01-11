"""
Configuration Management
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CrawlerConfig:
    """Configuration for a single crawler"""
    name: str
    target_docs: int
    start_url: str
    forums: list
    delay_range: tuple = (2, 5)
    headless: bool = True
    max_retries: int = 3


@dataclass
class Config:
    """Global configuration"""
    
    # Directories
    DATA_DIR: str = "data"
    CHECKPOINT_DIR: str = "checkpoints"
    
    # Crawling
    HEADLESS: bool = True
    DELAY_RANGE: tuple = (2, 5)
    MAX_RETRIES: int = 3
    
    # Document filtering
    MIN_WORDS: int = 50
    
    # VOZ configuration
    VOZ_CONFIG: CrawlerConfig = CrawlerConfig(
        name="voz",
        target_docs=500000,
        start_url="https://voz.vn",
        forums=[
            {"id": "F17", "name": "Chuyện trò linh tinh", "url": "https://voz.vn/f/chuyen-tro-linh-tinh.17/"},
            {"id": "F33", "name": "Khoa học - Công nghệ", "url": "https://voz.vn/f/khoa-hoc-cong-nghe.33/"}
        ]
    )
    
    # Otofun configuration
    OTOFUN_CONFIG: CrawlerConfig = CrawlerConfig(
        name="otofun",
        target_docs=300000,
        start_url="https://www.otofun.net",
        forums=[
            {"id": "automotive", "name": "Automotive", "url": "https://www.otofun.net/forums/o-to.17/"}
        ]
    )
    
    # TinhTe configuration
    TINHTE_CONFIG: CrawlerConfig = CrawlerConfig(
        name="tinhte",
        target_docs=200000,
        start_url="https://tinhte.vn",
        forums=[
            {"id": "tech", "name": "Technology", "url": "https://tinhte.vn/forums/thiet-bi-so-phan-cung.75/"}
        ]
    )
    
    @classmethod
    def get_crawler_config(cls, crawler_name: str) -> CrawlerConfig:
        """Get configuration for specific crawler"""
        configs = {
            'voz': cls.VOZ_CONFIG,
            'otofun': cls.OTOFUN_CONFIG,
            'tinhte': cls.TINHTE_CONFIG
        }
        return configs.get(crawler_name)

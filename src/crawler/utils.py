"""
Utility functions for crawlers
"""
import random
import time
from typing import List, Dict, Any
import hashlib
import re

# User agents pool for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def get_random_user_agent() -> str:
    """Get a random user agent from the pool"""
    return random.choice(USER_AGENTS)

def get_headers() -> Dict[str, str]:
    """Generate headers with random user agent"""
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def calculate_hash(text: str) -> str:
    """Calculate MD5 hash of text for deduplication"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def count_words(text: str) -> int:
    """Count words in Vietnamese text"""
    # Remove extra whitespace and split
    words = text.strip().split()
    return len(words)

def is_valid_document(text: str, min_words: int = 50) -> bool:
    """Check if document meets minimum word requirement"""
    return count_words(text) >= min_words

def clean_text(text: str) -> str:
    """Basic text cleaning"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep Vietnamese
    text = text.strip()
    return text

def rate_limit_sleep(min_delay: float = 0.5, max_delay: float = 2.0):
    """Sleep for random duration to avoid rate limiting"""
    time.sleep(random.uniform(min_delay, max_delay))

def extract_numbers_from_url(url: str) -> List[int]:
    """Extract all numbers from URL"""
    return [int(x) for x in re.findall(r'\d+', url)]

def save_checkpoint(checkpoint_data: Dict[str, Any], filename: str):
    """Save checkpoint for resume capability"""
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

def load_checkpoint(filename: str) -> Dict[str, Any]:
    """Load checkpoint data"""
    import json
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

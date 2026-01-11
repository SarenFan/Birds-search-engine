"""
Base Crawler with Anti-Scraping Mechanisms
"""

import time
import random
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import undetected_chromedriver as uc


class BaseCrawler(ABC):
    """
    Abstract base crawler with anti-scraping mechanisms
    
    Features:
    - Undetected ChromeDriver
    - Random delays (human-like behavior)
    - User-agent rotation
    - Retry mechanism with exponential backoff
    - Checkpoint & resume support
    """
    
    def __init__(self, headless: bool = True, delay_range: tuple = (2, 5)):
        """
        Initialize base crawler
        
        Args:
            headless: Run browser in headless mode
            delay_range: (min, max) seconds for random delays
        """
        self.headless = headless
        self.delay_range = delay_range
        self.ua = UserAgent()
        self.driver: Optional[webdriver.Chrome] = None
        
    def setup_driver(self) -> webdriver.Chrome:
        """
        Setup undetected Chrome driver with anti-scraping features
        
        Returns:
            Configured Chrome driver
        """
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        # Anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument(f'user-agent={self.ua.random}')
        
        # Performance optimizations
        options.add_argument('--disable-images')
        options.add_argument('--disable-css')
        options.add_argument('--disable-javascript')  # Enable if needed
        options.add_argument('--disk-cache-size=0')
        
        # Prefs to disable images
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,
                'javascript': 1  # 1=allow, 2=block
            }
        }
        options.add_experimental_option('prefs', prefs)
        
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        return driver
    
    def human_like_delay(self, min_sec: Optional[float] = None, 
                        max_sec: Optional[float] = None):
        """
        Random delay to simulate human behavior
        
        Args:
            min_sec: Minimum seconds (default: self.delay_range[0])
            max_sec: Maximum seconds (default: self.delay_range[1])
        """
        min_sec = min_sec or self.delay_range[0]
        max_sec = max_sec or self.delay_range[1]
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def retry_request(self, func, max_retries: int = 3, 
                     backoff_factor: float = 2.0):
        """
        Retry mechanism with exponential backoff
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            backoff_factor: Multiplier for delay between retries
            
        Returns:
            Result from func() if successful
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = (backoff_factor ** attempt) * random.uniform(1, 2)
                    print(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}")
                    time.sleep(delay)
        
        raise last_exception
    
    def scroll_page(self, scroll_pause: float = 0.5):
        """
        Scroll page to load dynamic content
        
        Args:
            scroll_pause: Seconds to wait between scrolls
        """
        if not self.driver:
            return
            
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
    
    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        self.driver = self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    @abstractmethod
    def crawl(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main crawl method to be implemented by subclasses
        
        Returns:
            Dictionary with crawled data
        """
        pass

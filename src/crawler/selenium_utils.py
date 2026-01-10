"""
Selenium-based crawler utilities for bypassing anti-scraping measures
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
import random
import time
import logging

logger = logging.getLogger(__name__)


class SeleniumCrawler:
    """Base class for Selenium-based web crawling"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.ua = UserAgent()

    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.driver:
            self.driver.quit()

    def setup_driver(self):
        """Setup undetected Chrome driver with anti-detection measures"""
        options = uc.ChromeOptions()

        if self.headless:
            options.add_argument('--headless=new')

        # Anti-detection arguments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument(f'user-agent={self.ua.random}')

        # Additional privacy/anti-tracking
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')

        # Set preferences (commented out experimental options that cause issues)
        # prefs = {
        #     'profile.default_content_setting_values': {
        #         'images': 2,  # Don't load images for speed
        #         'javascript': 1
        #     }
        # }
        # options.add_experimental_option('prefs', prefs)
        # options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = uc.Chrome(options=options)
            logger.info("Selenium driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize driver: {e}")
            raise

    def human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def scroll_page(self, scrolls: int = 3):
        """Scroll page like a human"""
        for i in range(scrolls):
            # Scroll to random position
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_to = random.randint(100, scroll_height // 2)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            time.sleep(random.uniform(0.5, 1.5))

    def get_page(self, url: str, wait_time: int = 10) -> str:
        """Get page content with wait for loading"""
        try:
            self.driver.get(url)
            self.human_like_delay(2, 4)

            # Wait for body to load
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Scroll to load dynamic content
            self.scroll_page(2)

            return self.driver.page_source

        except TimeoutException:
            logger.error(f"Timeout loading {url}")
            return None
        except Exception as e:
            logger.error(f"Error getting page {url}: {e}")
            return None

    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element {value} not found after {timeout}s")
            return None

    def find_elements_safe(self, by: By, value: str):
        """Safely find elements without throwing exception"""
        try:
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return []

    def click_element_safe(self, element):
        """Safely click element with human-like behavior"""
        try:
            # Move to element first
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.human_like_delay(0.5, 1.0)
            element.click()
            self.human_like_delay(1.0, 2.0)
            return True
        except Exception as e:
            logger.error(f"Failed to click element: {e}")
            return False


class RequestsWithRetry:
    """Enhanced requests with retry and anti-detection"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.ua = UserAgent()
        self.session = None

    def get_enhanced_headers(self):
        """Get headers that mimic real browser"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    def get_with_retry(self, url: str, use_session: bool = True):
        """Get URL with retry mechanism"""
        import requests

        for attempt in range(self.max_retries):
            try:
                if use_session:
                    if not self.session:
                        self.session = requests.Session()
                    response = self.session.get(
                        url,
                        headers=self.get_enhanced_headers(),
                        timeout=15,
                        allow_redirects=True
                    )
                else:
                    response = requests.get(
                        url,
                        headers=self.get_enhanced_headers(),
                        timeout=15,
                        allow_redirects=True
                    )

                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:
                    # Rate limited
                    wait_time = 2 ** attempt * 5
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)

        return None

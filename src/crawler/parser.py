"""
HTML parser utilities
"""
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re

def remove_html_tags(html: str) -> str:
    """Remove all HTML tags and scripts"""
    soup = BeautifulSoup(html, 'lxml')

    # Remove script and style elements
    for script in soup(["script", "style", "meta", "link"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text

def extract_links(html: str, base_url: str = '') -> List[str]:
    """Extract all links from HTML"""
    soup = BeautifulSoup(html, 'lxml')
    links = []

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('http'):
            links.append(href)
        elif href.startswith('/'):
            links.append(base_url + href)

    return links

def parse_thread_content(html: str) -> Dict[str, any]:
    """Parse thread/post content from HTML"""
    soup = BeautifulSoup(html, 'lxml')

    result = {
        'title': '',
        'author': '',
        'content': '',
        'timestamp': '',
        'replies': []
    }

    return result

def clean_vietnamese_text(text: str) -> str:
    """Clean and normalize Vietnamese text"""
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove quote markers
    text = re.sub(r'^[>\|]+\s*', '', text, flags=re.MULTILINE)

    return text.strip()

def extract_metadata(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract metadata from page"""
    metadata = {}

    # Try to get title
    title_tag = soup.find('title')
    if title_tag:
        metadata['page_title'] = title_tag.text.strip()

    # Try to get meta description
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag and desc_tag.get('content'):
        metadata['description'] = desc_tag['content']

    return metadata

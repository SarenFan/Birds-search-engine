#!/usr/bin/env python3
"""
Data Cleaning Pipeline for Voz Forum Data
==========================================

This script performs the following cleaning operations:
1. Remove HTML tags and script junk
2. Vietnamese word segmentation using underthesea
3. De-duplication by content hash
4. Teencode normalization
5. Filter by minimum word count (>= 50)
6. Preserve emojis and special characters

Input: Raw JSONL data from crawler
Output: Cleaned JSONL data with additional `text_segmented` field
"""

import json
import re
import hashlib
import logging
import argparse
import os
from pathlib import Path
from typing import Dict, Optional, Set, Generator
from datetime import datetime
from tqdm import tqdm

# Vietnamese word segmentation
try:
    from underthesea import word_tokenize
    SEGMENTER_AVAILABLE = True
except ImportError:
    SEGMENTER_AVAILABLE = False
    print("WARNING: underthesea not installed. Run: pip install underthesea")

# =============================================================================
# TEENCODE DICTIONARY
# =============================================================================
# Vietnamese teencode/slang to standard Vietnamese mapping
TEENCODE_DICT = {
    # ==========================================================================
    # SAFE ABBREVIATIONS (2+ characters, unambiguous)
    # ==========================================================================
    
    # Common teencode - HIGH CONFIDENCE
    'ko': 'không',
    'khong': 'không',
    'dc': 'được',
    'đc': 'được',
    'duoc': 'được',
    'mk': 'mình',
    'mik': 'mình',
    'rep': 'trả lời',
    'ib': 'inbox',
    'fb': 'facebook',
    
    # Pronouns - SAFE (2+ chars)
    'ae': 'anh em',
    'vk': 'vợ',
    'gf': 'bạn gái',
    'bf': 'bạn trai',
    'ny': 'người yêu',
    'ng': 'người',
    'ngta': 'người ta',
    'nguoita': 'người ta',
    'vkck': 'vợ chồng',
    
    # Actions - SAFE
    'bt': 'biết',
    'bth': 'bình thường',
    'nt': 'nhắn tin',
    'đt': 'điện thoại',
    'dt': 'điện thoại',
    'sd': 'sử dụng',
    'gtri': 'giá trị',
    'cty': 'công ty',
    'trc': 'trước',
    'truoc': 'trước',
    'tg': 'thời gian',
    
    # Locations - SAFE
    'vn': 'Việt Nam',
    'sg': 'Sài Gòn',
    'hn': 'Hà Nội',
    'hcm': 'Hồ Chí Minh',
    'tphcm': 'Thành phố Hồ Chí Minh',
    'tp.hcm': 'Thành phố Hồ Chí Minh',
    
    # Expressions - SAFE
    'cx': 'cũng',
    'vs': 'với',
    'thik': 'thích',
    'bik': 'biết',
    'bjt': 'biết',
    'hỉu': 'hiểu',
    'lun': 'luôn',
    'luon': 'luôn',
    'nhìu': 'nhiều',
    'nhiu': 'nhiêu',
    'iu': 'yêu',
    
    # Question words - SAFE
    'lsao': 'làm sao',
    'ntn': 'như thế nào',
    'ntnao': 'như thế nào',
    
    # Time - SAFE
    'hqua': 'hôm qua',
    'hnay': 'hôm nay',
    
    # ==========================================================================
    # VIETNAMESE ABBREVIATIONS (Official/Common - HIGH CONFIDENCE)
    # ==========================================================================
    
    # Insurance & Social
    'bhyt': 'bảo hiểm y tế',
    'bhxh': 'bảo hiểm xã hội',
    'bhtn': 'bảo hiểm thất nghiệp',
    
    # Work & Business
    'xkld': 'xuất khẩu lao động',
    'hdld': 'hợp đồng lao động',
    'tnhh': 'trách nhiệm hữu hạn',
    'ctcp': 'công ty cổ phần',
    
    # Education
    'thpt': 'trung học phổ thông',
    'thcs': 'trung học cơ sở',
    'đhqg': 'đại học quốc gia',
    'sv': 'sinh viên',
    'hs': 'học sinh',
    'gv': 'giáo viên',
    
    # Government & Legal
    'cmnd': 'chứng minh nhân dân',
    'cccd': 'căn cước công dân',
    
    # Real Estate
    'bđs': 'bất động sản',
    
    # Tech
    'cntt': 'công nghệ thông tin',
    
    # ==========================================================================
    # VOZ-SPECIFIC SLANG (SAFE)
    # ==========================================================================
    'thím': 'bạn',
    'thim': 'bạn',
    'vozer': 'thành viên voz',
    'thớt': 'topic',
    'tks': 'cảm ơn',
    'thanks': 'cảm ơn',
    'sr': 'xin lỗi',
    'sorry': 'xin lỗi',
    'pls': 'làm ơn',
    'plz': 'làm ơn',
    
    # Common typos - SAFE (2+ chars)
    'ak': 'à',
    'ah': 'à',
    'uk': 'ừ',
    'uh': 'ừ',
    'hem': 'không',
    'hok': 'không',
    'hông': 'không',
    'hong': 'không',
    'kh': 'không',
    
    # Tech terms
    'gg': 'google',
    'ytb': 'youtube',
    
    # ==========================================================================
    # REMOVED - RISKY SINGLE LETTERS (too ambiguous)
    # ==========================================================================
    # 'k': 'không',     # Could be "k" in names, "1k", etc.
    # 'e': 'em',        # Could be "E" in names, scientific notation
    # 'a': 'anh',       # Could be "A" in grades, names
    # 'j': 'gì',        # Could be "J" in names
    # 'z': 'vậy',       # Could be variable names, abbreviations  
    # 'v': 'vậy',       # Could be "V" in names, voltage
    # 'r': 'rồi',       # Could be "R" in names, units
    # 'ui': 'rồi',      # Could be "UI" (user interface)
}

# =============================================================================
# LOGGING SETUP
# =============================================================================
def setup_logging(log_dir: str) -> logging.Logger:
    """Setup logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"clean_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


# =============================================================================
# TEXT CLEANING FUNCTIONS
# =============================================================================

def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text while preserving content."""
    if not text:
        return ""
    
    # Remove script and style tags with content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode common HTML entities
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
        '&#x27;': "'",
        '&#x2F;': '/',
        '&hellip;': '...',
        '&ndash;': '-',
        '&mdash;': '—',
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    return text


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    if not text:
        return ""
    
    # Remove URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    text = re.sub(url_pattern, '', text)
    
    # Remove www links
    text = re.sub(r'www\.[^\s<>"{}|\\^`\[\]]+', '', text)
    
    return text


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace while preserving newlines for readability."""
    if not text:
        return ""
    
    # Replace all horizontal whitespace (space, tab, non-breaking space, etc.) with single space
    # [^\S\n] matches any whitespace that is NOT a newline
    text = re.sub(r'[^\S\n]+', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_teencode(text: str) -> str:
    """
    Normalize Vietnamese teencode to standard Vietnamese.
    Preserves emojis and special characters.
    Only replaces STANDALONE words (not parts of URLs, hashtags, or other words).
    """
    if not text:
        return ""
    
    # Create word boundary pattern for replacement
    # We need to be careful not to replace parts of words or URLs
    result = text
    
    # Characters that indicate the teencode is part of a URL, hashtag, or compound
    # These should NOT trigger replacement
    url_chars = r'a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
    special_chars = r'/:@#\-_'  # URL and hashtag characters (không bao gồm dấu câu)
    boundary_chars = url_chars + special_chars
    
    # Sort by length (longer first) to avoid partial replacements
    sorted_teencode = sorted(TEENCODE_DICT.items(), key=lambda x: len(x[0]), reverse=True)
    
    for teen, standard in sorted_teencode:
        # Word boundary matching (case insensitive)
        # Lookbehind: NOT preceded by letters, digits, or URL special chars
        # Lookahead: NOT followed by letters, digits, or URL special chars
        pattern = r'(?<![' + boundary_chars + r'0-9])' + \
                  re.escape(teen) + \
                  r'(?![' + boundary_chars + r'0-9])'
        
        try:
            result = re.sub(pattern, standard, result, flags=re.IGNORECASE)
        except re.error:
            # If regex fails, skip this replacement
            continue
    
    return result


def clean_text(text: str, normalize_teen: bool = True) -> str:
    """
    Main text cleaning function.
    Preserves emojis and special characters.
    """
    if not text:
        return ""
    
    # Step 1: Remove HTML tags
    text = remove_html_tags(text)
    
    # Step 2: Remove URLs
    text = remove_urls(text)
    
    # Step 3: Remove "Click to expand..." patterns from quotes
    text = re.sub(r'Click to expand\.{0,3}', '', text, flags=re.IGNORECASE)
    
    # Step 4: Remove "via theNEXTvoz for iPhone/Android" patterns
    text = re.sub(r'via\s+theNEXTvoz\s+for\s+(iPhone|Android)', '', text, flags=re.IGNORECASE)
    
    # Step 5: Normalize teencode (if enabled)
    if normalize_teen:
        text = normalize_teencode(text)
    
    # Step 6: Convert to lowercase (for case-insensitive search with BM25/SPIMI)
    text = text.lower()
    
    # Step 7: Normalize whitespace
    text = normalize_whitespace(text)
    
    return text


def segment_vietnamese(text: str) -> str:
    """
    Perform Vietnamese word segmentation using underthesea.
    Returns text with words separated by spaces and compound words joined by underscore.
    """
    if not SEGMENTER_AVAILABLE:
        return text
    
    if not text or not text.strip():
        return ""
    
    try:
        # word_tokenize returns list of tokens
        # Using format='text' to get string output with underscores for compound words
        segmented = word_tokenize(text, format='text')
        return segmented
    except Exception as e:
        # If segmentation fails, return original text
        return text


def count_words(text: str) -> int:
    """Count words in text (Vietnamese aware)."""
    if not text:
        return 0
    
    # Split by whitespace and count non-empty tokens
    words = text.split()
    return len([w for w in words if len(w) >= 1])


def compute_content_hash(content: str) -> str:
    """Compute MD5 hash of content for deduplication."""
    if not content:
        return ""
    
    # Normalize for hashing: lowercase, remove extra spaces
    normalized = ' '.join(content.lower().split())
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


# =============================================================================
# DATA PROCESSING
# =============================================================================

def read_jsonl(filepath: str) -> Generator[Dict, None, None]:
    """Read JSONL file line by line."""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                if line.strip():
                    yield json.loads(line)
            except json.JSONDecodeError as e:
                logging.warning(f"JSON decode error at line {line_num}: {e}")
                continue


def count_lines(filepath: str) -> int:
    """Count lines in a file efficiently."""
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for _ in f:
            count += 1
    return count


def process_document(doc: Dict, seen_hashes: Set[str], min_word_count: int = 50) -> Optional[Dict]:
    """
    Process a single document through the cleaning pipeline.
    
    Returns:
        Cleaned document dict or None if document should be filtered out.
    """
    # Get content to clean (prefer content_clean if available)
    original_content = doc.get('content', '')
    content_clean_original = doc.get('content_clean', original_content)
    
    # Step 1: Check for duplicates
    content_hash = compute_content_hash(content_clean_original)
    if content_hash in seen_hashes:
        return None  # Duplicate
    seen_hashes.add(content_hash)
    
    # Step 2: Clean the text
    cleaned_text = clean_text(content_clean_original, normalize_teen=True)
    
    # Step 3: Check minimum word count
    word_count = count_words(cleaned_text)
    if word_count < min_word_count:
        return None  # Too short
    
    # Step 4: Perform word segmentation
    segmented_text = segment_vietnamese(cleaned_text)
    
    # Step 5: Build output document (keep all original fields)
    output_doc = doc.copy()
    
    # Add new fields
    output_doc['text_cleaned'] = cleaned_text  # Cleaned but not segmented
    output_doc['text_segmented'] = segmented_text  # Cleaned AND segmented
    output_doc['word_count_clean'] = word_count  # Updated word count
    
    return output_doc


def run_cleaning_pipeline(
    input_path: str,
    output_dir: str,
    min_word_count: int = 50,
    batch_size: int = 10000
) -> Dict:
    """
    Run the full data cleaning pipeline.
    
    Args:
        input_path: Path to input JSONL file
        output_dir: Directory to save cleaned data
        min_word_count: Minimum word count threshold
        batch_size: Number of documents to process before writing
    
    Returns:
        Statistics dictionary
    """
    # Setup
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'voz_cleaned.jsonl')
    
    # Setup logging
    log_dir = os.path.join(output_dir, 'logs')
    logger = setup_logging(log_dir)
    
    logger.info(f"Starting data cleaning pipeline")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Min word count: {min_word_count}")
    
    # Check underthesea availability
    if not SEGMENTER_AVAILABLE:
        logger.error("underthesea not installed! Please run: pip install underthesea")
        return {}
    
    # Count total lines for progress bar
    logger.info("Counting input documents...")
    total_lines = count_lines(input_path)
    logger.info(f"Total documents to process: {total_lines:,}")
    
    # Statistics
    stats = {
        'total_input': 0,
        'duplicates_removed': 0,
        'too_short_removed': 0,
        'errors': 0,
        'total_output': 0,
    }
    
    # Track seen content hashes for deduplication
    seen_hashes: Set[str] = set()
    
    # Process documents
    buffer = []
    
    with open(output_path, 'w', encoding='utf-8') as out_file:
        for doc in tqdm(read_jsonl(input_path), total=total_lines, desc="Cleaning data"):
            stats['total_input'] += 1
            
            try:
                # Get content hash before processing for duplicate tracking
                original_content = doc.get('content_clean', doc.get('content', ''))
                content_hash = compute_content_hash(original_content)
                
                # Check duplicate
                if content_hash in seen_hashes:
                    stats['duplicates_removed'] += 1
                    continue
                
                # Process document
                cleaned_doc = process_document(doc, seen_hashes, min_word_count)
                
                if cleaned_doc is None:
                    # Either duplicate or too short
                    if content_hash not in seen_hashes:
                        stats['too_short_removed'] += 1
                    continue
                
                # Add to buffer
                buffer.append(json.dumps(cleaned_doc, ensure_ascii=False))
                stats['total_output'] += 1
                
                # Write buffer when full
                if len(buffer) >= batch_size:
                    out_file.write('\n'.join(buffer) + '\n')
                    buffer = []
                    
            except Exception as e:
                stats['errors'] += 1
                if stats['errors'] <= 10:  # Log first 10 errors
                    logger.warning(f"Error processing doc {doc.get('doc_id', 'unknown')}: {e}")
        
        # Write remaining buffer
        if buffer:
            out_file.write('\n'.join(buffer) + '\n')
    
    # Log statistics
    logger.info("=" * 50)
    logger.info("CLEANING COMPLETE - STATISTICS")
    logger.info("=" * 50)
    logger.info(f"Total input documents:    {stats['total_input']:,}")
    logger.info(f"Duplicates removed:       {stats['duplicates_removed']:,}")
    logger.info(f"Too short removed (<{min_word_count} words): {stats['too_short_removed']:,}")
    logger.info(f"Errors:                   {stats['errors']:,}")
    logger.info(f"Total output documents:   {stats['total_output']:,}")
    logger.info(f"Retention rate:           {stats['total_output']/stats['total_input']*100:.2f}%")
    logger.info("=" * 50)
    
    # Save statistics to JSON
    stats_path = os.path.join(output_dir, 'cleaning_stats.json')
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    logger.info(f"Statistics saved to: {stats_path}")
    
    return stats


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Clean and process Voz forum data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python data_cleaner.py --input data/raw/voz_1m.jsonl --output data/cleaned/
  python data_cleaner.py --input data/raw/voz_1m.jsonl --output data/cleaned/ --min-words 100
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='/home/kource/Projects/SEG301-test/data/data_raw/lightning_ai/data/voz_1m.jsonl',
        help='Path to input JSONL file'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='/home/kource/Projects/SEG301-test/data/data_clean',
        help='Output directory for cleaned data'
    )
    
    parser.add_argument(
        '--min-words', '-m',
        type=int,
        default=50,
        help='Minimum word count threshold (default: 50)'
    )
    
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=10000,
        help='Batch size for writing output (default: 10000)'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        return 1
    
    # Run pipeline
    stats = run_cleaning_pipeline(
        input_path=args.input,
        output_dir=args.output,
        min_word_count=args.min_words,
        batch_size=args.batch_size
    )
    
    if stats:
        print(f"\n✅ Cleaning complete! Output saved to: {args.output}")
        print(f"   - Total cleaned documents: {stats['total_output']:,}")
        return 0
    else:
        print("\n❌ Cleaning failed!")
        return 1


if __name__ == '__main__':
    exit(main())

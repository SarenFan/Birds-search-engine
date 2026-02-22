#!/usr/bin/env python3
"""
Query Processor for BM25 Search
===============================

Cleans search queries using the SAME logic as data_cleaner.py
to ensure consistency between indexed data and search queries.

This module imports and reuses functions from data_cleaner.py
to guarantee identical preprocessing.
"""

import sys
from pathlib import Path

# Add src to path to allow imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import cleaning functions from data_cleaner
from cleaner.data_cleaner import (
    clean_text,
    segment_vietnamese,
    normalize_teencode,
    TEENCODE_DICT
)


def clean_query(query: str) -> str:
    """
    Clean and tokenize a search query using the same logic as data_cleaner.py
    
    Pipeline (matches data_cleaner.py exactly):
    1. Remove HTML tags
    2. Remove URLs  
    3. Normalize teencode (ko -> không, dc -> được, etc.)
    4. Lowercase
    5. Normalize whitespace
    6. Vietnamese word segmentation (underthesea)
    
    Args:
        query: Raw search query from user
        
    Returns:
        Cleaned and segmented query string
        Format: "mua_nhà ở hà_nội giá rẻ"
    
    Example:
        >>> clean_query("Mua nhà ở HN thì cần bao nhiêu tiền?")
        "mua_nhà ở hà_nội thì cần bao_nhiêu tiền"
    """
    if not query or not query.strip():
        return ""
    
    # Step 1-5: Clean text (same as data_cleaner.py)
    # This includes: HTML removal, URL removal, teencode normalization, lowercase
    cleaned = clean_text(query, normalize_teen=True)
    
    # Step 6: Vietnamese word segmentation (same as data_cleaner.py)
    segmented = segment_vietnamese(cleaned)
    
    return segmented


def get_query_tokens(query: str) -> list:
    """
    Clean query and return as list of tokens
    
    Args:
        query: Raw search query
        
    Returns:
        List of tokens ready for BM25 matching
        
    Example:
        >>> get_query_tokens("Mua nhà ở HN giá bao nhiêu?")
        ['mua_nhà', 'ở', 'hà_nội', 'giá', 'bao_nhiêu']
    """
    cleaned = clean_query(query)
    if not cleaned:
        return []
    
    return cleaned.split()


if __name__ == "__main__":
    # Test query processing
    test_queries = [
        "Mua nhà ở HN thì cần bao nhiêu tiền?",
        "Ko bik nên mua laptop nào",
        "Vozer nào có kinh nghiệm xin visa Nhật ko ạ?",
        "Cty mình đang tuyển dev, ae nào có nhu cầu ib mk nhé",
        "BHXH với BHYT khác nhau ntn?",
    ]
    
    print("=" * 60)
    print("QUERY PROCESSOR TEST")
    print("=" * 60)
    
    for query in test_queries:
        cleaned = clean_query(query)
        tokens = get_query_tokens(query)
        
        print(f"\n📝 Raw query: {query}")
        print(f"✅ Cleaned:   {cleaned}")
        print(f"🔢 Tokens:    {tokens}")

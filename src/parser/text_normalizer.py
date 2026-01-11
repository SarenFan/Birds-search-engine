"""
Vietnamese Text Normalization
Handles teencode, slang, and text cleaning
"""

import re
from typing import Dict, List


class VietnameseTextNormalizer:
    """
    Normalize Vietnamese text from social media
    - Convert teencode to standard Vietnamese
    - Remove special characters
    - Normalize spacing
    """
    
    # Common teencode mappings
    TEENCODE_DICT = {
        'k': 'không',
        'ko': 'không',
        'kg': 'không',
        'hok': 'không',
        'bt': 'biết',
        'bik': 'biết',
        'dc': 'được',
        'đc': 'được',
        'r': 'rồi',
        'mk': 'mình',
        'mik': 'mình',
        'nv': 'như vậy',
        'ntn': 'như thế nào',
        'tl': 'trả lời',
        'rep': 'trả lời',
        'vs': 'với',
        'j': 'gì',
        'z': 'vậy',
        'v': 'vậy',
        'kh': 'khi',
        'ms': 'mới',
        'đag': 'đang',
        'fen': 'fan',
        'sr': 'sorry',
        'sory': 'xin lỗi',
        'tks': 'cảm ơn',
        'thanks': 'cảm ơn',
        'thank': 'cảm ơn',
        'oki': 'ok',
        'ok': 'được',
        'a': 'anh',
        'e': 'em',
        'cx': 'cũng',
        'hk': 'học',
        'nc': 'nói chuyện',
        'wa': 'quá',
        'zui': 'vui',
        'buồn': 'buồn',
        'vui': 'vui',
        'lun': 'luôn',
    }
    
    # Slang dictionary
    SLANG_DICT = {
        'ông mặt trời': 'admin',
        'gà': 'người chơi yếu',
        'pro': 'chuyên nghiệp',
        'noob': 'người mới',
        'buff': 'tăng cường',
        'nerf': 'làm yếu đi',
        'flex': 'khoe khoang',
        'low': 'thấp',
        'deal': 'giao dịch',
        'fake': 'giả',
        'real': 'thật',
    }
    
    def __init__(self):
        """Initialize normalizer with dictionaries"""
        self.teencode = self.TEENCODE_DICT
        self.slang = self.SLANG_DICT
    
    def normalize(self, text: str) -> str:
        """
        Full normalization pipeline
        
        Args:
            text: Raw text from social media
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase for processing
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove emoji (basic)
        text = re.sub(r'[^\w\s,.]', ' ', text)
        
        # Normalize teencode
        text = self.replace_teencode(text)
        
        # Normalize slang
        text = self.replace_slang(text)
        
        # Normalize spacing
        text = re.sub(r'\s+', ' ', text)
        
        # Strip whitespace
        text = text.strip()
        
        return text
    
    def replace_teencode(self, text: str) -> str:
        """
        Replace teencode with standard Vietnamese
        
        Args:
            text: Text containing teencode
            
        Returns:
            Text with teencode replaced
        """
        words = text.split()
        normalized_words = []
        
        for word in words:
            # Check if word is teencode
            if word in self.teencode:
                normalized_words.append(self.teencode[word])
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def replace_slang(self, text: str) -> str:
        """
        Replace slang with standard terms
        
        Args:
            text: Text containing slang
            
        Returns:
            Text with slang replaced
        """
        for slang, standard in self.slang.items():
            text = text.replace(slang, standard)
        
        return text
    
    def is_valid_doc(self, text: str, min_words: int = 50) -> bool:
        """
        Check if document meets quality criteria
        
        Args:
            text: Text to validate
            min_words: Minimum number of words required
            
        Returns:
            True if valid, False otherwise
        """
        if not text:
            return False
        
        # Count words
        words = text.split()
        
        return len(words) >= min_words
    
    def add_teencode(self, teencode: str, standard: str):
        """Add custom teencode mapping"""
        self.teencode[teencode] = standard
    
    def add_slang(self, slang: str, standard: str):
        """Add custom slang mapping"""
        self.slang[slang] = standard

"""
Vietnamese Tokenizer for SPIMI Indexing
Supports: underthesea (preferred) or simple whitespace tokenization
"""

import re
import unicodedata
from typing import List, Tuple

# Try to import underthesea for Vietnamese word segmentation
try:
    from underthesea import word_tokenize
    HAS_UNDERTHESEA = True
except ImportError:
    HAS_UNDERTHESEA = False
    print("⚠️ underthesea not installed, using simple tokenization")


class VietnameseTokenizer:
    """Tokenizer for Vietnamese text with position tracking"""
    
    # Vietnamese stopwords (common words to filter)
    STOPWORDS = {
        'và', 'của', 'có', 'là', 'được', 'cho', 'trong', 'để', 'với',
        'không', 'này', 'đã', 'các', 'một', 'những', 'người', 'thì',
        'khi', 'từ', 'như', 'về', 'còn', 'đến', 'ra', 'lên', 'xuống',
        'vào', 'theo', 'qua', 'lại', 'nên', 'mà', 'hay', 'hoặc', 'thế',
        'nhưng', 'cũng', 'đó', 'rồi', 'nữa', 'bị', 'tại', 'đây', 'sau',
        'trước', 'vì', 'nếu', 'thì', 'ở', 'do', 'bởi', 'chỉ', 'mới',
        'vẫn', 'rất', 'quá', 'lắm', 'nhiều', 'ít', 'hơn', 'nhất',
        'the', 'is', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'for',
    }
    
    def __init__(self, remove_stopwords: bool = True, min_length: int = 2):
        """
        Initialize tokenizer
        
        Args:
            remove_stopwords: Whether to remove stopwords
            min_length: Minimum token length to keep
        """
        self.remove_stopwords = remove_stopwords
        self.min_length = min_length
        self.use_underthesea = HAS_UNDERTHESEA
        
    def normalize(self, text: str) -> str:
        """Normalize text before tokenization"""
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove HTML entities
        text = re.sub(r'&\w+;', ' ', text)
        
        # Normalize unicode
        text = unicodedata.normalize('NFC', text)
        
        # Remove special characters but keep Vietnamese diacritics
        text = re.sub(r'[^\w\sàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        text = self.normalize(text)
        
        if self.use_underthesea:
            # Use underthesea for proper Vietnamese word segmentation
            tokens = word_tokenize(text, format="text").split()
        else:
            # Simple whitespace tokenization
            tokens = text.split()
        
        # Filter tokens
        filtered = []
        for token in tokens:
            # Skip short tokens
            if len(token) < self.min_length:
                continue
            
            # Skip stopwords
            if self.remove_stopwords and token in self.STOPWORDS:
                continue
            
            # Skip pure numbers
            if token.isdigit():
                continue
                
            filtered.append(token)
        
        return filtered
    
    def tokenize_with_positions(self, text: str) -> List[Tuple[str, int]]:
        """
        Tokenize text and return tokens with their positions
        
        Args:
            text: Input text
            
        Returns:
            List of (token, position) tuples
        """
        text = self.normalize(text)
        
        if self.use_underthesea:
            # Use underthesea for proper Vietnamese word segmentation
            tokens = word_tokenize(text, format="text").split()
        else:
            tokens = text.split()
        
        result = []
        position = 0
        
        for token in tokens:
            # Skip invalid tokens
            if len(token) < self.min_length:
                position += 1
                continue
            
            if self.remove_stopwords and token in self.STOPWORDS:
                position += 1
                continue
            
            if token.isdigit():
                position += 1
                continue
            
            result.append((token, position))
            position += 1
        
        return result


# Singleton instance for convenience
_default_tokenizer = None

def get_tokenizer() -> VietnameseTokenizer:
    """Get default tokenizer instance"""
    global _default_tokenizer
    if _default_tokenizer is None:
        _default_tokenizer = VietnameseTokenizer()
    return _default_tokenizer

def tokenize(text: str) -> List[str]:
    """Convenience function to tokenize text"""
    return get_tokenizer().tokenize(text)

def tokenize_with_positions(text: str) -> List[Tuple[str, int]]:
    """Convenience function to tokenize with positions"""
    return get_tokenizer().tokenize_with_positions(text)


if __name__ == "__main__":
    # Test tokenizer
    test_texts = [
        "Mua laptop gaming tầm 20 triệu thì nên chọn con nào các bác?",
        "Em đang tính mua nhà ở Hà Nội, có ai giới thiệu khu vực nào không?",
        "Vozer nào có kinh nghiệm xin visa Nhật không ạ?",
    ]
    
    tokenizer = VietnameseTokenizer()
    print(f"Using underthesea: {tokenizer.use_underthesea}\n")
    
    for text in test_texts:
        tokens = tokenizer.tokenize(text)
        print(f"Input: {text}")
        print(f"Tokens: {tokens}")
        print()

"""
Data Writer for JSONL and Parquet
"""

import json
import jsonlines
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd


class DataWriter:
    """
    Write crawled data to files
    
    Supports:
    - JSONL (streaming write)
    - Batch writing for performance
    - Parquet conversion for storage optimization
    """
    
    def __init__(self, output_dir: str = "data"):
        """
        Initialize data writer
        
        Args:
            output_dir: Directory to write data files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_jsonl(self, filename: str, data: List[Dict[str, Any]], 
                   mode: str = 'a'):
        """
        Write data to JSONL file
        
        Args:
            filename: Output filename
            data: List of documents to write
            mode: File mode ('a' for append, 'w' for overwrite)
        """
        filepath = self.output_dir / filename
        
        with jsonlines.open(filepath, mode=mode) as writer:
            for doc in data:
                writer.write(doc)
        
        print(f"✅ Written {len(data)} docs to {filepath}")
    
    def write_single_doc(self, filename: str, doc: Dict[str, Any]):
        """
        Write single document (append mode)
        
        Args:
            filename: Output filename
            doc: Document to write
        """
        filepath = self.output_dir / filename
        
        with jsonlines.open(filepath, mode='a') as writer:
            writer.write(doc)
    
    def read_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        """
        Read JSONL file
        
        Args:
            filename: Input filename
            
        Returns:
            List of documents
        """
        filepath = self.output_dir / filename
        
        if not filepath.exists():
            return []
        
        docs = []
        with jsonlines.open(filepath) as reader:
            for doc in reader:
                docs.append(doc)
        
        return docs
    
    def convert_to_parquet(self, jsonl_filename: str, 
                          parquet_filename: Optional[str] = None):
        """
        Convert JSONL to Parquet for compression
        
        Args:
            jsonl_filename: Input JSONL file
            parquet_filename: Output Parquet file (optional)
        """
        if not parquet_filename:
            parquet_filename = jsonl_filename.replace('.jsonl', '.parquet')
        
        jsonl_path = self.output_dir / jsonl_filename
        parquet_path = self.output_dir / parquet_filename
        
        # Read JSONL
        docs = self.read_jsonl(jsonl_filename)
        
        if not docs:
            print(f"⚠️  No data to convert")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(docs)
        
        # Write to Parquet
        df.to_parquet(parquet_path, compression='snappy', index=False)
        
        # Calculate compression ratio
        jsonl_size = jsonl_path.stat().st_size / (1024 * 1024)  # MB
        parquet_size = parquet_path.stat().st_size / (1024 * 1024)  # MB
        ratio = (1 - parquet_size / jsonl_size) * 100
        
        print(f"✅ Converted to Parquet:")
        print(f"   JSONL: {jsonl_size:.2f} MB")
        print(f"   Parquet: {parquet_size:.2f} MB")
        print(f"   Compression: {ratio:.1f}%")
    
    def get_doc_count(self, filename: str) -> int:
        """
        Count documents in JSONL file
        
        Args:
            filename: JSONL filename
            
        Returns:
            Number of documents
        """
        filepath = self.output_dir / filename
        
        if not filepath.exists():
            return 0
        
        count = 0
        with jsonlines.open(filepath) as reader:
            for _ in reader:
                count += 1
        
        return count

"""
Progress Monitoring and Reporting
"""

import time
from typing import Dict, Any
from datetime import datetime, timedelta


class ProgressMonitor:
    """
    Monitor crawling progress and generate reports
    
    Features:
    - Track documents collected
    - Calculate speed (docs/hour)
    - Estimate time remaining (ETA)
    - Generate progress reports
    """
    
    def __init__(self, crawler_name: str, target_docs: int):
        """
        Initialize monitor
        
        Args:
            crawler_name: Name of the crawler
            target_docs: Target number of documents
        """
        self.crawler_name = crawler_name
        self.target_docs = target_docs
        self.start_time = time.time()
        self.last_report_time = self.start_time
        self.docs_at_last_report = 0
    
    def report_progress(self, docs_collected: int):
        """
        Generate progress report
        
        Args:
            docs_collected: Current number of documents collected
        """
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Calculate speed
        if elapsed > 0:
            docs_per_second = docs_collected / elapsed
            docs_per_hour = docs_per_second * 3600
        else:
            docs_per_hour = 0
        
        # Calculate ETA
        remaining_docs = self.target_docs - docs_collected
        if docs_per_hour > 0:
            hours_remaining = remaining_docs / docs_per_hour
            eta = datetime.now() + timedelta(hours=hours_remaining)
        else:
            eta = None
        
        # Progress percentage
        progress = (docs_collected / self.target_docs) * 100
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * docs_collected / self.target_docs)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Print report
        print("\n" + "="*80)
        print(f"📊 {self.crawler_name.upper()} PROGRESS REPORT")
        print("="*80)
        print(f"[{bar}] {progress:.1f}%")
        print(f"\n📈 Stats:")
        print(f"   Collected: {docs_collected:,} / {self.target_docs:,} docs")
        print(f"   Speed: {docs_per_hour:.0f} docs/hour")
        print(f"   Elapsed: {self._format_time(elapsed)}")
        
        if eta:
            print(f"   ETA: {eta.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Remaining: {self._format_time(hours_remaining * 3600)}")
        
        print("="*80)
        
        self.last_report_time = current_time
        self.docs_at_last_report = docs_collected
    
    def should_report(self, docs_collected: int, 
                     interval_seconds: int = 300) -> bool:
        """
        Check if should generate report
        
        Args:
            docs_collected: Current docs collected
            interval_seconds: Report interval in seconds
            
        Returns:
            True if should report
        """
        current_time = time.time()
        time_elapsed = current_time - self.last_report_time
        
        return time_elapsed >= interval_seconds
    
    def get_stats(self, docs_collected: int) -> Dict[str, Any]:
        """
        Get current statistics
        
        Args:
            docs_collected: Current docs collected
            
        Returns:
            Statistics dictionary
        """
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        docs_per_hour = (docs_collected / elapsed * 3600) if elapsed > 0 else 0
        progress = (docs_collected / self.target_docs) * 100
        
        return {
            'crawler': self.crawler_name,
            'docs_collected': docs_collected,
            'target_docs': self.target_docs,
            'progress_percent': progress,
            'docs_per_hour': docs_per_hour,
            'elapsed_seconds': elapsed,
            'elapsed_formatted': self._format_time(elapsed)
        }
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to human readable string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

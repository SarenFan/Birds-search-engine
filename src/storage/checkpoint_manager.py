"""
Checkpoint Manager for Resume Mechanism
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CheckpointManager:
    """
    Manage checkpoints for resume capability
    
    Features:
    - Save crawl progress periodically
    - Resume from last checkpoint
    - Track collected documents
    - Deduplication using hashes
    """
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """
        Initialize checkpoint manager
        
        Args:
            checkpoint_dir: Directory to store checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self, crawler_name: str, data: Dict[str, Any]):
        """
        Save checkpoint for a crawler
        
        Args:
            crawler_name: Name of the crawler (e.g., 'voz', 'otofun')
            data: Checkpoint data to save
        """
        checkpoint_file = self.checkpoint_dir / f"{crawler_name}_checkpoint.json"
        
        # Add timestamp
        data['last_updated'] = datetime.now().isoformat()
        
        # Write checkpoint
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Checkpoint saved: {checkpoint_file}")
    
    def load_checkpoint(self, crawler_name: str) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint for a crawler
        
        Args:
            crawler_name: Name of the crawler
            
        Returns:
            Checkpoint data if exists, None otherwise
        """
        checkpoint_file = self.checkpoint_dir / f"{crawler_name}_checkpoint.json"
        
        if not checkpoint_file.exists():
            print(f"⚠️  No checkpoint found for {crawler_name}")
            return None
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ Checkpoint loaded: {checkpoint_file}")
            print(f"   Last updated: {data.get('last_updated', 'Unknown')}")
            print(f"   Progress: {data.get('docs_collected', 0)} docs")
            
            return data
        except Exception as e:
            print(f"❌ Error loading checkpoint: {e}")
            return None
    
    def delete_checkpoint(self, crawler_name: str):
        """Delete checkpoint file"""
        checkpoint_file = self.checkpoint_dir / f"{crawler_name}_checkpoint.json"
        
        if checkpoint_file.exists():
            os.remove(checkpoint_file)
            print(f"🗑️  Checkpoint deleted: {checkpoint_file}")
    
    def get_progress(self, crawler_name: str) -> Dict[str, Any]:
        """
        Get current progress for a crawler
        
        Returns:
            Progress information
        """
        checkpoint = self.load_checkpoint(crawler_name)
        
        if not checkpoint:
            return {
                'crawler': crawler_name,
                'status': 'not_started',
                'docs_collected': 0,
                'last_updated': None
            }
        
        return {
            'crawler': crawler_name,
            'status': 'in_progress',
            'docs_collected': checkpoint.get('docs_collected', 0),
            'last_page': checkpoint.get('last_page', 0),
            'last_updated': checkpoint.get('last_updated', None),
            'seen_hashes': len(checkpoint.get('seen_hashes', []))
        }
    
    def create_initial_checkpoint(self, crawler_name: str, 
                                  target_docs: int,
                                  config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create initial checkpoint for a new crawl
        
        Args:
            crawler_name: Name of the crawler
            target_docs: Target number of documents
            config: Additional configuration
            
        Returns:
            Initial checkpoint data
        """
        checkpoint = {
            'crawler_name': crawler_name,
            'target_docs': target_docs,
            'docs_collected': 0,
            'last_page': 0,
            'last_url': None,
            'seen_hashes': [],
            'config': config or {},
            'created_at': datetime.now().isoformat()
        }
        
        self.save_checkpoint(crawler_name, checkpoint)
        
        return checkpoint

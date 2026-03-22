"""
Vector Search using Sentence Transformers
Semantic search with Vietnamese document embeddings
"""

import json
import os
import pickle
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from tqdm import tqdm

# Lazy imports to handle missing dependencies
_sentence_transformers = None
_faiss = None


def _load_sentence_transformers():
    global _sentence_transformers
    if _sentence_transformers is None:
        from sentence_transformers import SentenceTransformer
        _sentence_transformers = SentenceTransformer
    return _sentence_transformers


def _load_faiss():
    global _faiss
    if _faiss is None:
        import faiss
        _faiss = faiss
    return _faiss


@dataclass
class VectorSearchResult:
    """Vector search result"""
    doc_id: str
    score: float
    title: str
    url: str
    content_preview: str


class VectorIndex:
    """FAISS-based vector index for semantic search"""
    
    def __init__(self, dimension: int = 768):
        """
        Initialize vector index

        Args:
            dimension: Embedding dimension (768 for PhoBERT, 384 for MiniLM)
        """
        self.dimension = dimension
        self.index = None
        self.doc_ids: List[str] = []
        self.doc_info: Dict[str, Dict] = {}
        
    def build_index(self, embeddings: np.ndarray, doc_ids: List[str], 
                   doc_info: Dict[str, Dict]):
        """
        Build FAISS index from embeddings
        
        Args:
            embeddings: numpy array of shape (n_docs, dimension)
            doc_ids: list of document IDs
            doc_info: dict of doc_id -> {title, url, content}
        """
        faiss = _load_faiss()
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        # Build index (Inner Product = Cosine after normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)
        
        self.doc_ids = doc_ids
        self.doc_info = doc_info
        
        print(f"✅ Vector index built: {len(doc_ids)} documents")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[VectorSearchResult]:
        """
        Search for similar documents
        
        Args:
            query_embedding: query vector
            top_k: number of results
            
        Returns:
            List of VectorSearchResult
        """
        if self.index is None:
            return []
        
        faiss = _load_faiss()
        
        # Normalize query
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            doc_id = self.doc_ids[idx]
            info = self.doc_info.get(doc_id, {})
            results.append(VectorSearchResult(
                doc_id=doc_id,
                score=float(score),
                title=info.get('title', ''),
                url=info.get('url', ''),
                content_preview=info.get('content', '')[:200]
            ))
        
        return results
    
    def save(self, path: str):
        """Save index to disk"""
        faiss = _load_faiss()
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        data = {
            'dimension': self.dimension,
            'doc_ids': self.doc_ids,
            'doc_info': self.doc_info
        }
        
        # Save FAISS index
        faiss.write_index(self.index, path + '.faiss')
        
        # Save metadata
        with open(path + '.meta', 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Vector index saved to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'VectorIndex':
        """Load index from disk"""
        faiss = _load_faiss()
        
        # Load metadata
        with open(path + '.meta', 'rb') as f:
            data = pickle.load(f)
        
        index = cls(dimension=data['dimension'])
        index.index = faiss.read_index(path + '.faiss')
        index.doc_ids = data['doc_ids']
        index.doc_info = data['doc_info']
        
        print(f"📂 Vector index loaded: {len(index.doc_ids)} documents")
        return index


class VectorSearchEngine:
    """
    Vector Search Engine using Sentence Transformers
    """
    
    # Vietnamese-compatible models
    MODELS = {
        'phobert': 'bkai-foundation-models/vietnamese-bi-encoder',  # PhoBERT-based, 768-dim
        # 'multilingual': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # 384-dim
        # 'labse': 'sentence-transformers/LaBSE',
        # 'minilm': 'sentence-transformers/all-MiniLM-L6-v2'  # Fallback
    }
    
    def __init__(self, model_name: str = 'phobert'):
        """
        Initialize vector search engine
        
        Args:
            model_name: Model key from MODELS dict
        """
        SentenceTransformer = _load_sentence_transformers()
        
        self.model_key = model_name
        model_path = self.MODELS.get(model_name, model_name)
        
        print(f"🔄 Loading model: {model_path}")
        self.model = SentenceTransformer(model_path)
        self.dimension = self.model.get_sentence_embedding_dimension()

        # Move model to GPU if available for faster query encoding
        self._device = self._detect_device()
        if self._device == 'cuda':
            self.model = self.model.to('cuda')
        print(f"✅ Model loaded on {self._device.upper()}. Dimension: {self.dimension}")

        self.vector_index = VectorIndex(self.dimension)
        self._last_query = None        # Cache last query text
        self._last_embedding = None    # Cache last query embedding

        # Warmup: first encode is slow due to JIT compilation
        print("🔥 Warming up model...")
        self.model.encode("warmup", convert_to_numpy=True, device=self._device)
        print("✅ Model ready")
    
    @staticmethod
    def _detect_device():
        """Auto-detect GPU availability"""
        try:
            import torch
            if torch.cuda.is_available():
                name = torch.cuda.get_device_name(0)
                vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f"GPU detected: {name} ({vram:.1f} GB VRAM)")
                return 'cuda'
        except ImportError:
            pass
        print("No GPU detected, using CPU")
        return 'cpu'

    def build_index_from_jsonl(self, jsonl_path: str,
                               content_field: str = 'content',
                               batch_size: int = 0,
                               max_docs: int = 0,
                               chunk_size: int = 50000) -> VectorIndex:
        """
        Build vector index from JSONL file using chunked processing.
        Encodes chunk_size docs at a time and adds to FAISS incrementally
        to avoid OOM on large datasets.

        Args:
            jsonl_path: Path to JSONL file
            content_field: Field to encode
            batch_size: Encoding batch size (0 = auto)
            max_docs: Limit number of docs (0 = all)
            chunk_size: Number of docs per chunk for encoding (default 50K)

        Returns:
            Built VectorIndex
        """
        import gc
        faiss = _load_faiss()

        print(f"Building vector index from {jsonl_path}")
        start_time = datetime.now()

        device = self._device  # Use device detected at init
        if batch_size <= 0:
            batch_size = 256 if device == 'cuda' else 64

        # Count lines
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            total = sum(1 for _ in f)
        if max_docs > 0:
            total = min(total, max_docs)
        print(f"Documents to process: {total:,} (chunks of {chunk_size:,})")

        # Initialize FAISS index
        self.vector_index.index = faiss.IndexFlatIP(self.dimension)
        all_doc_ids = []
        all_doc_info = {}

        # Process in chunks
        chunk_texts = []
        chunk_ids = []
        chunk_info = {}
        doc_count = 0
        chunk_num = 0

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(tqdm(f, total=total, desc="Reading")):
                if max_docs > 0 and i >= max_docs:
                    break

                doc = json.loads(line)
                doc_id = doc.get('doc_id', '')
                content = doc.get(content_field) or doc.get('content', '')
                if not doc_id or not content:
                    continue

                chunk_texts.append(content[:512])
                chunk_ids.append(doc_id)
                chunk_info[doc_id] = {
                    'title': doc.get('thread_title', ''),
                    'url': doc.get('url', ''),
                    'content': content[:200]  # Reduced from 500 to save RAM
                }
                doc_count += 1

                # Flush chunk when full
                if len(chunk_texts) >= chunk_size:
                    chunk_num += 1
                    print(f"\nEncoding chunk {chunk_num} ({len(chunk_texts):,} docs, device={device})...")

                    embeddings = self.model.encode(
                        chunk_texts, batch_size=batch_size,
                        show_progress_bar=True, convert_to_numpy=True,
                        device=device
                    )
                    embeddings = embeddings.astype('float32')
                    faiss.normalize_L2(embeddings)
                    self.vector_index.index.add(embeddings)

                    all_doc_ids.extend(chunk_ids)
                    all_doc_info.update(chunk_info)

                    # Free memory
                    del embeddings, chunk_texts, chunk_ids, chunk_info
                    gc.collect()
                    chunk_texts, chunk_ids, chunk_info = [], [], {}

        # Flush remaining docs
        if chunk_texts:
            chunk_num += 1
            print(f"\nEncoding chunk {chunk_num} ({len(chunk_texts):,} docs, device={device})...")

            embeddings = self.model.encode(
                chunk_texts, batch_size=batch_size,
                show_progress_bar=True, convert_to_numpy=True,
                device=device
            )
            embeddings = embeddings.astype('float32')
            faiss.normalize_L2(embeddings)
            self.vector_index.index.add(embeddings)

            all_doc_ids.extend(chunk_ids)
            all_doc_info.update(chunk_info)

            del embeddings, chunk_texts, chunk_ids, chunk_info
            gc.collect()

        self.vector_index.doc_ids = all_doc_ids
        self.vector_index.doc_info = all_doc_info

        duration = (datetime.now() - start_time).total_seconds()
        print(f"\nIndex built: {doc_count:,} documents in {duration:.1f}s ({duration/60:.1f} min)")

        return self.vector_index
    
    def search(self, query: str, top_k: int = 10) -> List[VectorSearchResult]:
        """
        Search for documents matching the query

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of VectorSearchResult
        """
        # Cache last query embedding — reuse when switching modes (BM25→Vector→Hybrid)
        if query == self._last_query and self._last_embedding is not None:
            query_embedding = self._last_embedding
        else:
            query_embedding = self.model.encode(query, convert_to_numpy=True,
                                                device=self._device)
            self._last_query = query
            self._last_embedding = query_embedding

        return self.vector_index.search(query_embedding, top_k)
    
    def save_index(self, path: str = 'data/index/vector_index'):
        """Save vector index"""
        self.vector_index.save(path)
    
    def load_index(self, path: str = 'data/index/vector_index'):
        """Load vector index"""
        self.vector_index = VectorIndex.load(path)


def build_vector_index(jsonl_path: str = 'data/voz_data.jsonl',
                       index_path: str = 'data/index/vector_index',
                       model: str = 'phobert',
                       batch_size: int = 0,
                       max_docs: int = 0) -> VectorIndex:
    """
    Convenience function to build and save vector index.
    Frees GPU VRAM and model RAM after saving.
    """
    import gc
    engine = VectorSearchEngine(model)
    engine.build_index_from_jsonl(jsonl_path, batch_size=batch_size, max_docs=max_docs)
    engine.save_index(index_path)
    vi = engine.vector_index
    # Free model from VRAM
    del engine
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass
    return vi


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Vector Search - Build index & test')
    parser.add_argument('jsonl_path', nargs='?', default='data/voz_data.jsonl',
                        help='Path to JSONL data file')
    parser.add_argument('--model', default='phobert',
                        choices=['phobert', 'multilingual', 'labse', 'minilm'],
                        help='Embedding model (default: phobert)')
    parser.add_argument('--batch-size', type=int, default=0,
                        help='Encoding batch size (0=auto: 256 GPU, 64 CPU)')
    parser.add_argument('--max-docs', type=int, default=0,
                        help='Limit number of documents (0=all)')
    parser.add_argument('--index-path', default='data/index/vector_index',
                        help='Output index path')
    parser.add_argument('--search-only', action='store_true',
                        help='Skip building, only test search on existing index')
    args = parser.parse_args()

    if not args.search_only:
        import gc

        # Build index
        print(f"Building Vector Index (model={args.model})")
        engine = VectorSearchEngine(args.model)
        engine.build_index_from_jsonl(
            args.jsonl_path,
            batch_size=args.batch_size,
            max_docs=args.max_docs
        )
        engine.save_index(args.index_path)

        # Free VRAM and RAM after build
        del engine
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("GPU VRAM freed")
        except ImportError:
            pass

        # Reload lightweight for search test
        print("\nReloading model for search test...")
        engine = VectorSearchEngine(args.model)
        engine.load_index(args.index_path)
    else:
        # Load existing index
        print(f"Loading existing index from {args.index_path}")
        engine = VectorSearchEngine(args.model)
        engine.load_index(args.index_path)

    # Test search
    print("\nTesting Vector Search")
    test_queries = ["mua laptop gaming", "kinh nghiem mua nha", "dien thoai tot nhat"]

    for query in test_queries:
        print(f"\nQuery: {query}")
        results = engine.search(query, top_k=3)
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r.score:.4f}] {r.title[:60]}")
            print(f"     URL: {r.url}")

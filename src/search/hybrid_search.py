"""
Hybrid Search: Combining BM25 and Vector Search
Score fusion for better retrieval
"""

import sys
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ranking.bm25 import BM25
from indexer.spimi import InvertedIndex


@dataclass
class HybridSearchResult:
    """Hybrid search result with combined scores"""
    doc_id: str
    bm25_score: float
    vector_score: float
    hybrid_score: float
    title: str
    url: str


class HybridSearch:
    """
    Hybrid Search combining BM25 (lexical) and Vector (semantic) search

    Score fusion: hybrid = alpha * bm25_norm + (1-alpha) * vector_norm
    """

    def __init__(self,
                 bm25_index_path: str = 'data/index/inverted_index.pkl',
                 vector_index_path: str = 'data/index/vector_index',
                 alpha: float = 0.5,
                 existing_index: 'InvertedIndex | None' = None,
                 existing_bm25: 'BM25 | None' = None):
        self.alpha = alpha
        self.bm25 = None
        self.index = None
        self.vector_engine = None

        # Reuse existing BM25/index if provided, otherwise load from disk
        if existing_index and existing_bm25:
            self.index = existing_index
            self.bm25 = existing_bm25
            print("BM25 reused from existing instance")
        else:
            print("Loading BM25 index...")
            self.index = InvertedIndex.load(bm25_index_path)
            self.bm25 = BM25(self.index)

        # Try to load vector index
        try:
            from .vector_search import VectorSearchEngine
            print("Loading Vector index...")
            self.vector_engine = VectorSearchEngine('phobert')
            self.vector_engine.load_index(vector_index_path)
            self.has_vector = True
        except Exception as e:
            print(f"Vector search not available: {e}")
            self.has_vector = False

    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Min-max normalize scores to [0, 1]"""
        if not scores:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if max_s == min_s:
            return [1.0] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]

    def _bm25_to_hybrid(self, bm25_results) -> List[HybridSearchResult]:
        """Convert BM25 raw results [(doc_id, score, info), ...] to HybridSearchResult"""
        return [
            HybridSearchResult(
                doc_id=doc_id,
                bm25_score=score,
                vector_score=0.0,
                hybrid_score=score,
                title=info.get('title', ''),
                url=info.get('url', '')
            ) for doc_id, score, info in bm25_results
        ]

    def search_bm25_only(self, query: str, top_k: int = 10) -> List[HybridSearchResult]:
        """BM25 search only"""
        return self._bm25_to_hybrid(self.bm25.search(query, top_k))

    def search_vector_only(self, query: str, top_k: int = 10) -> List[HybridSearchResult]:
        """Vector search only"""
        if not self.has_vector:
            return []

        results = self.vector_engine.search(query, top_k)
        return [
            HybridSearchResult(
                doc_id=r.doc_id,
                bm25_score=0.0,
                vector_score=r.score,
                hybrid_score=r.score,
                title=r.title,
                url=r.url
            ) for r in results
        ]

    def search_hybrid(self, query: str, top_k: int = 10,
                     alpha: Optional[float] = None) -> List[HybridSearchResult]:
        """
        Hybrid search with weighted score fusion
        hybrid = alpha * bm25_norm + (1-alpha) * vector_norm
        """
        alpha = alpha if alpha is not None else self.alpha

        # Get more candidates from each method
        k = top_k * 3

        # BM25 search — raw: [(doc_id, score, info), ...]
        bm25_raw = self.bm25.search(query, k)
        bm25_scores = {d: s for d, s, _ in bm25_raw}
        bm25_info = {d: info for d, _, info in bm25_raw}

        # Vector search
        vector_scores = {}
        if self.has_vector:
            vector_results = self.vector_engine.search(query, k)
            vector_scores = {r.doc_id: r.score for r in vector_results}
            for r in vector_results:
                if r.doc_id not in bm25_info:
                    bm25_info[r.doc_id] = {'title': r.title, 'url': r.url}

        # Get all candidate documents
        all_docs = set(bm25_scores.keys()) | set(vector_scores.keys())

        if not all_docs:
            return []

        # Normalize scores
        bm25_list = [bm25_scores.get(d, 0) for d in all_docs]
        vector_list = [vector_scores.get(d, 0) for d in all_docs]

        bm25_norm = self._normalize_scores(bm25_list)
        vector_norm = self._normalize_scores(vector_list) if vector_scores else [0] * len(all_docs)

        # Compute hybrid scores
        results = []
        for i, doc_id in enumerate(all_docs):
            hybrid = alpha * bm25_norm[i] + (1 - alpha) * vector_norm[i]

            info = bm25_info.get(doc_id, {})
            results.append(HybridSearchResult(
                doc_id=doc_id,
                bm25_score=bm25_scores.get(doc_id, 0),
                vector_score=vector_scores.get(doc_id, 0),
                hybrid_score=hybrid,
                title=info.get('title', ''),
                url=info.get('url', '')
            ))

        results.sort(key=lambda x: x.hybrid_score, reverse=True)
        return results[:top_k]

    def search(self, query: str, mode: str = 'hybrid',
               top_k: int = 10, alpha: float = None) -> List[HybridSearchResult]:
        """Search with specified mode: 'bm25', 'vector', or 'hybrid'"""
        if mode == 'bm25':
            return self.search_bm25_only(query, top_k)
        elif mode == 'vector':
            return self.search_vector_only(query, top_k)
        else:
            return self.search_hybrid(query, top_k, alpha)

    def get_stats(self) -> Dict:
        """Get search engine stats"""
        return {
            'bm25_available': self.bm25 is not None,
            'vector_available': self.has_vector,
            'alpha': self.alpha,
            'total_docs': self.index.total_docs if self.index else 0,
            'vocabulary_size': self.index.total_terms if self.index else 0,
        }


if __name__ == "__main__":
    print("Testing Hybrid Search")

    search = HybridSearch(alpha=0.5)
    print(f"\nStats: {search.get_stats()}")

    query = "mua laptop gaming"

    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")

    for mode in ['bm25', 'vector', 'hybrid']:
        print(f"\nMode: {mode.upper()}")
        results = search.search(query, mode=mode, top_k=3)

        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r.hybrid_score:.4f}] {r.title[:50]}...")
            print(f"     BM25: {r.bm25_score:.4f}, Vector: {r.vector_score:.4f}")

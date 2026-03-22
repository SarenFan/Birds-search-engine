"""
BM25 (Okapi BM25) Ranking
  Score(D,Q) = Σ IDF(qi) * tf*(k1+1) / (tf + k1*(1 - b + b*|D|/avgdl))
  IDF(qi) = log((N - df + 0.5) / (df + 0.5) + 1)
"""
import math, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from indexer.spimi import InvertedIndex

# === Stopwords: stopwordsiso (265 từ) + bỏ từ có nghĩa trong search ===
from stopwordsiso import stopwords as _sw
_KEEP = {'nhà', 'cao', 'người', 'lớn', 'số', 'anh', 'em', 'con', 'năm', 'nơi', 'việc'}
STOPWORDS = {w for w in _sw('vi') if ' ' not in w} - _KEEP

def tokenize_query(query):
    """Normalize + split query → list of terms."""
    text = query.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # bỏ ký tự đặc biệt
    return [w for w in text.split() if len(w) >= 2 and w not in STOPWORDS and not w.isdigit()]


class BM25:
    def __init__(self, index, k1=1.5, b=0.75):
        self.index = index
        self.N = index.total_docs
        # Pre-compute: flat dict doc_id→length (1 lookup thay vì 2)
        self._dl = {did: info['length'] for did, info in index.doc_info.items()}
        # Pre-compute hằng số BM25
        self._k1_plus1 = k1 + 1
        self._k1_times_1mb = k1 * (1 - b)           # k1*(1-b)
        self._k1_b_over_avgdl = k1 * b / index.avg_doc_length  # k1*b/avgdl

    def _idf(self, df):
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def search(self, query, top_k=10):
        terms = tokenize_query(query)
        if not terms:
            return [], 0

        scores = {}
        dl = self._dl  # local ref (nhanh hơn self.xxx trong loop)
        k1p1, k1_1mb, k1ba = self._k1_plus1, self._k1_times_1mb, self._k1_b_over_avgdl

        for term in terms:
            entry = self.index.index.get(term)
            if not entry:
                continue
            idf = self._idf(entry['df'])
            for doc_id, tf in entry['postings']:
                # tf*(k1+1) / (tf + k1*(1-b) + k1*b*dl/avgdl)
                tf_norm = (tf * k1p1) / (tf + k1_1mb + k1ba * dl[doc_id])
                scores[doc_id] = scores.get(doc_id, 0) + idf * tf_norm

        # heapq top-k: O(n log k) thay vì O(n log n)
        import heapq
        total_matching = len(scores)
        top = heapq.nlargest(top_k, scores.items(), key=lambda x: x[1])
        results = [(doc_id, score, self.index.doc_info[doc_id]) for doc_id, score in top]
        return results, total_matching


if __name__ == "__main__":
    idx = InvertedIndex.load('data/index/inverted_index.pkl')
    print(f"Loaded: {idx.total_docs:,} docs, {idx.total_terms:,} terms")
    bm25 = BM25(idx)
    for q in ['mua laptop', 'kinh nghiệm mua nhà', 'game online']:
        print(f"\nQuery: '{q}'")
        results, total = bm25.search(q, top_k=3)
        print(f"  Total matching: {total:,}")
        for doc_id, score, info in results:
            print(f"  [{score:.3f}] {info['title'][:60]}")

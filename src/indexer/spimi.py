"""
SPIMI (Single-Pass In-Memory Indexing)
  P1: docs → blocks (index trên RAM → sort by term → flush đĩa)
  P2: n-way merge blocks (heap) → inverted index
  P3: đọc lại JSONL lấy doc metadata (tách riêng để giảm RAM)
"""
import json, os, pickle, heapq, shutil
from collections import defaultdict, Counter
from tqdm import tqdm


class InvertedIndex:
    # index: term -> {'df': int, 'postings': [(doc_id, tf), ...]}
    # doc_info: doc_id -> {'length': int, 'title': str, 'url': str}
    def __init__(self):
        self.index = {}
        self.doc_info = {}
        self.total_docs = 0
        self.total_terms = 0
        self.avg_doc_length = 0.0

    def save(self, path):
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(vars(self), f)

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        idx = cls()
        idx.__dict__.update(data)
        return idx


class SPIMIIndexer:
    def __init__(self, block_size=10000, block_dir='data/index/blocks'):
        self.block_size = block_size
        self.block_dir = block_dir

    def build(self, jsonl_path, index_path='data/index/inverted_index.pkl'):
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            total = sum(1 for _ in f)
        print(f"SPIMI: {total:,} docs, block={self.block_size:,}")

        if os.path.exists(self.block_dir):
            shutil.rmtree(self.block_dir)
        os.makedirs(self.block_dir)

        # === P1: INVERT ===
        block_files, block, n = [], defaultdict(list), 0
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f, total=total, desc="P1:Index"):
                doc = json.loads(line)
                doc_id, text = doc.get('doc_id', ''), doc.get('text_segmented', '')
                if not text or not doc_id:
                    continue
                for term, tf in Counter(text.split()).items():
                    block[term].append((doc_id, tf))
                n += 1
                if n >= self.block_size:
                    block_files.append(self._flush(block, len(block_files)))
                    block, n = defaultdict(list), 0
        if block:
            block_files.append(self._flush(block, len(block_files)))

        # === P2: MERGE ===
        final = self._merge(block_files)
        shutil.rmtree(self.block_dir)

        # === P3: METADATA ===
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f, total=total, desc="P3:Meta"):
                doc = json.loads(line)
                doc_id, text = doc.get('doc_id', ''), doc.get('text_segmented', '')
                if not text or not doc_id:
                    continue
                final.doc_info[doc_id] = {
                    'length': len(text.split()),
                    'title': doc.get('thread_title', ''),
                    'url': doc.get('url', ''),
                }

        # Compute stats & save
        final.total_docs = len(final.doc_info)
        final.total_terms = len(final.index)
        if final.total_docs > 0:
            final.avg_doc_length = sum(d['length'] for d in final.doc_info.values()) / final.total_docs
        final.save(index_path)
        print(f"Done: {final.total_docs:,} docs, {final.total_terms:,} terms, "
              f"avgdl={final.avg_doc_length:.1f}")
        return final

    def _flush(self, block, num):
        path = os.path.join(self.block_dir, f'block_{num:04d}.pkl')
        with open(path, 'wb') as f:
            pickle.dump(sorted(block.items()), f)
        return path

    def _merge(self, block_files):
        iters = []
        for path in block_files:
            with open(path, 'rb') as f:
                iters.append(iter(pickle.load(f)))

        heap = []
        for i, it in enumerate(iters):
            item = next(it, None)
            if item:
                heapq.heappush(heap, (item[0], i, item[1]))

        final = InvertedIndex()
        while heap:
            term, bi, postings = heapq.heappop(heap)
            all_p = list(postings)
            while heap and heap[0][0] == term:
                _, oi, op = heapq.heappop(heap)
                all_p.extend(op)
                item = next(iters[oi], None)
                if item:
                    heapq.heappush(heap, (item[0], oi, item[1]))
            item = next(iters[bi], None)
            if item:
                heapq.heappush(heap, (item[0], bi, item[1]))
            final.index[term] = {'df': len(all_p), 'postings': all_p}
        return final


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/voz_data.jsonl'
    bs = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    idx = SPIMIIndexer(block_size=bs).build(path)
    for t in ['laptop', 'mua', 'game']:
        p = idx.index.get(t, {})
        print(f"  '{t}': df={p.get('df',0)}, sample={p.get('postings',[])[:2]}")

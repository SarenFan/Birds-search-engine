"""SEG301 Console Search — BM25 trên SPIMI Index"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indexer.spimi import InvertedIndex, SPIMIIndexer
from ranking.bm25 import BM25

INDEX = 'data/index/inverted_index.pkl'
DATA = 'data/voz_data.jsonl'

def main():
    # Load hoặc build index
    if os.path.exists(INDEX):
        print(f"Loading index...")
        idx = InvertedIndex.load(INDEX)
    else:
        print(f"Building index from {DATA}...")
        idx = SPIMIIndexer().build(DATA, INDEX)
    print(f"Ready: {idx.total_docs:,} docs, {idx.total_terms:,} terms, avgdl={idx.avg_doc_length:.1f}")

    bm25 = BM25(idx)
    top_k = 10

    print("\nCommands: :top N | :stats | :quit")
    while True:
        try:
            query = input("\nQuery> ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not query:
            continue
        if query == ':quit' or query == ':q':
            break
        if query == ':stats':
            print(f"  docs={idx.total_docs:,}  terms={idx.total_terms:,}  avgdl={idx.avg_doc_length:.1f}")
            continue
        if query.startswith(':top '):
            top_k = int(query.split()[1])
            print(f"  top_k={top_k}")
            continue

        # Search
        t0 = time.time()
        results = bm25.search(query, top_k)
        ms = (time.time() - t0) * 1000

        print(f"  {len(results)} results in {ms:.1f}ms")
        for i, (doc_id, score, info) in enumerate(results, 1):
            print(f"  {i}. [{score:.3f}] {info['title'][:70]}")
            print(f"     {info.get('url', '')}")

if __name__ == "__main__":
    main()

"""
Evaluation Script for Search Engine
Calculates Precision@10, Recall, and compares BM25 vs Vector vs Hybrid
"""

import json
import os
import sys
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ranking.bm25 import BM25
from indexer.spimi import InvertedIndex


@dataclass
class EvalQuery:
    """Evaluation query with relevant documents"""
    query: str
    relevant_keywords: List[str]  # Keywords that should appear in relevant docs
    semantic_variants: List[str]  # Semantic variations (for testing AI search)


# 20 Test Queries with expected relevance criteria
TEST_QUERIES = [
    EvalQuery(
        query="mua laptop gaming",
        relevant_keywords=["laptop", "gaming", "máy tính", "chơi game", "pc"],
        semantic_variants=["máy tính chơi game", "pc chơi game"]
    ),
    EvalQuery(
        query="kinh nghiệm mua nhà",
        relevant_keywords=["nhà", "mua", "bất động sản", "căn hộ", "chung cư"],
        semantic_variants=["tư vấn mua nhà", "kinh nghiệm bất động sản"]
    ),
    EvalQuery(
        query="xin visa nhật bản",
        relevant_keywords=["visa", "nhật", "du lịch", "japan", "xin"],
        semantic_variants=["đi nhật", "thủ tục nhập cảnh nhật"]
    ),
    EvalQuery(
        query="công việc lương cao",
        relevant_keywords=["lương", "việc làm", "thu nhập", "career", "nghề"],
        semantic_variants=["việc tốt", "thu nhập tốt", "kiếm tiền"]
    ),
    EvalQuery(
        query="điện thoại giá rẻ",
        relevant_keywords=["điện thoại", "phone", "smartphone", "giá", "rẻ"],
        semantic_variants=["smartphone tầm trung", "mua điện thoại"]
    ),
    EvalQuery(
        query="học lập trình python",
        relevant_keywords=["python", "lập trình", "code", "học", "programming"],
        semantic_variants=["học code", "tự học công nghệ"]
    ),
    EvalQuery(
        query="du lịch đà nẵng",
        relevant_keywords=["đà nẵng", "du lịch", "travel", "biển", "hội an"],
        semantic_variants=["đi chơi miền trung", "nghỉ dưỡng biển"]
    ),
    EvalQuery(
        query="thưởng tết công ty",
        relevant_keywords=["thưởng", "tết", "công ty", "lương", "bonus"],
        semantic_variants=["tiền thưởng cuối năm", "lương tháng 13"]
    ),
    EvalQuery(
        query="mua xe máy honda",
        relevant_keywords=["xe máy", "honda", "motor", "xe", "mua"],
        semantic_variants=["mua xe gắn máy", "xe tay ga"]
    ),
    EvalQuery(
        query="bệnh tiểu đường",
        relevant_keywords=["tiểu đường", "đường huyết", "bệnh", "sức khỏe", "y tế"],
        semantic_variants=["bệnh đường", "sức khỏe tim mạch"]
    ),
    EvalQuery(
        query="game mobile hay",
        relevant_keywords=["game", "mobile", "chơi", "hay", "giải trí"],
        semantic_variants=["trò chơi điện thoại", "game trên điện thoại"]
    ),
    EvalQuery(
        query="nuôi con nhỏ",
        relevant_keywords=["con", "trẻ em", "bé", "nuôi", "cha mẹ"],
        semantic_variants=["làm cha mẹ", "chăm sóc trẻ"]
    ),
    EvalQuery(
        query="đầu tư chứng khoán",
        relevant_keywords=["chứng khoán", "đầu tư", "cổ phiếu", "tài chính", "tiền"],
        semantic_variants=["kiếm tiền từ đầu tư", "tài chính cá nhân"]
    ),
    EvalQuery(
        query="cafe sài gòn",
        relevant_keywords=["cafe", "sài gòn", "quán", "coffee", "hcm"],
        semantic_variants=["quán cà phê đẹp", "địa điểm uống nước"]
    ),
    EvalQuery(
        query="mua nhà hà nội",
        relevant_keywords=["nhà", "hà nội", "bất động sản", "căn hộ", "mua"],
        semantic_variants=["mua căn hộ thủ đô", "bđs miền bắc"]
    ),
    EvalQuery(
        query="làm thêm sinh viên",
        relevant_keywords=["làm thêm", "sinh viên", "part time", "việc", "học sinh"],
        semantic_variants=["kiếm tiền khi còn đi học", "công việc bán thời gian"]
    ),
    EvalQuery(
        query="review sách hay",
        relevant_keywords=["sách", "đọc", "review", "hay", "văn học"],
        semantic_variants=["gợi ý sách đọc", "sách nên đọc"]
    ),
    EvalQuery(
        query="giảm cân hiệu quả",
        relevant_keywords=["giảm cân", "béo", "diet", "ăn kiêng", "tập gym"],
        semantic_variants=["giảm mỡ", "tập luyện để gầy"]
    ),
    EvalQuery(
        query="mua đồ công nghệ",
        relevant_keywords=["công nghệ", "mua", "đồ", "thiết bị", "tech"],
        semantic_variants=["sắm đồ điện tử", "mua gadget"]
    ),
    EvalQuery(
        query="lập gia đình trẻ",
        relevant_keywords=["gia đình", "cưới", "kết hôn", "vợ chồng", "trẻ"],
        semantic_variants=["lấy vợ sớm", "cuộc sống hôn nhân"]
    ),
]


def is_relevant(doc_content: str, keywords: List[str]) -> bool:
    """Check if document is relevant based on keywords"""
    content_lower = doc_content.lower()
    # Document is relevant if it contains at least 1 keyword
    for keyword in keywords:
        if keyword.lower() in content_lower:
            return True
    return False


def calculate_precision_at_k(relevant_count: int, k: int) -> float:
    """Calculate Precision@k"""
    return relevant_count / k if k > 0 else 0.0


def calculate_recall(retrieved_relevant: int, total_relevant: int) -> float:
    """Calculate Recall"""
    return retrieved_relevant / total_relevant if total_relevant > 0 else 0.0


class SearchEvaluator:
    """Evaluator for search engines"""
    
    def __init__(self, data_path: str = ''):
        """Load documents for relevance checking"""
        # Auto-detect data path
        if not data_path:
            for p in ['data/data_clean/voz_cleaned.jsonl', 'data/voz_data.jsonl']:
                if os.path.exists(p):
                    data_path = p
                    break
        if not data_path or not os.path.exists(data_path):
            raise FileNotFoundError("No JSONL data file found")

        self.documents = {}
        print(f"Loading documents from {data_path}...")

        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                doc = json.loads(line)
                doc_id = doc.get('doc_id', '')
                content = doc.get('content', '') + ' ' + doc.get('thread_title', '')
                self.documents[doc_id] = content

        print(f"Loaded {len(self.documents):,} documents")

        # Initialize search engines
        print("Initializing search engines...")
        index = InvertedIndex.load('data/index/inverted_index.pkl')
        self.bm25 = BM25(index)

        # Try to load hybrid search (reuse index to save RAM)
        self.hybrid_search = None
        try:
            from search.hybrid_search import HybridSearch
            self.hybrid_search = HybridSearch(existing_index=index, existing_bm25=self.bm25)
            print("Hybrid search available")
        except Exception as e:
            print(f"Hybrid search not available: {e}")
    
    def evaluate_query(self, eval_query: EvalQuery, k: int = 10) -> Dict:
        """Evaluate a single query with Precision@k and Recall (pooling-based)"""
        results = {
            'query': eval_query.query,
            'keywords': eval_query.relevant_keywords,
            'semantic_variants': eval_query.semantic_variants,
            'bm25': {'precision': 0, 'recall': 0, 'relevant_docs': []},
        }

        # --- Collect results from all methods ---

        # BM25 Search — raw: [(doc_id, score, info), ...]
        bm25_results = self.bm25.search(eval_query.query, k)
        bm25_doc_ids = [doc_id for doc_id, _, _ in bm25_results]

        vector_doc_ids = []
        hybrid_doc_ids = []

        if self.hybrid_search and self.hybrid_search.has_vector:
            vector_results = self.hybrid_search.search_vector_only(eval_query.query, k)
            vector_doc_ids = [r.doc_id for r in vector_results]
            results['vector'] = {'precision': 0, 'recall': 0, 'relevant_docs': []}

        if self.hybrid_search:
            hybrid_results = self.hybrid_search.search_hybrid(eval_query.query, k)
            hybrid_doc_ids = [r.doc_id for r in hybrid_results]
            results['hybrid'] = {'precision': 0, 'recall': 0, 'relevant_docs': []}

        # --- Pooling: total relevant = union of all relevant docs across methods ---
        all_pool = set(bm25_doc_ids) | set(vector_doc_ids) | set(hybrid_doc_ids)
        pool_relevant = set()
        for doc_id in all_pool:
            content = self.documents.get(doc_id, '')
            if is_relevant(content, eval_query.relevant_keywords):
                pool_relevant.add(doc_id)
        total_relevant = len(pool_relevant) if pool_relevant else 1  # avoid div by 0

        # --- BM25 metrics ---
        bm25_rel = [d for d in bm25_doc_ids if d in pool_relevant]
        results['bm25']['relevant_docs'] = bm25_rel
        results['bm25']['precision'] = calculate_precision_at_k(len(bm25_rel), k)
        results['bm25']['recall'] = calculate_recall(len(bm25_rel), total_relevant)

        # --- Vector metrics ---
        if 'vector' in results:
            vec_rel = [d for d in vector_doc_ids if d in pool_relevant]
            results['vector']['relevant_docs'] = vec_rel
            results['vector']['precision'] = calculate_precision_at_k(len(vec_rel), k)
            results['vector']['recall'] = calculate_recall(len(vec_rel), total_relevant)

        # --- Hybrid metrics ---
        if 'hybrid' in results:
            hyb_rel = [d for d in hybrid_doc_ids if d in pool_relevant]
            results['hybrid']['relevant_docs'] = hyb_rel
            results['hybrid']['precision'] = calculate_precision_at_k(len(hyb_rel), k)
            results['hybrid']['recall'] = calculate_recall(len(hyb_rel), total_relevant)

        # --- Per-query analysis: why is one method better? ---
        results['analysis'] = self._analyze_query(eval_query, results)

        return results

    def _analyze_query(self, eval_query: EvalQuery, results: Dict) -> str:
        """Generate per-query analysis explaining why each method performs differently"""
        bm25_p = results['bm25']['precision']
        query = eval_query.query

        # BM25-only case
        if 'vector' not in results:
            if bm25_p >= 0.7:
                return f"BM25 hieu qua cao ({bm25_p:.0%}) vi query '{query}' chua keyword truc tiep co trong corpus."
            else:
                return f"BM25 hieu qua thap ({bm25_p:.0%}) vi query '{query}' co the can hieu ngu nghia (semantic)."

        vec_p = results['vector']['precision']
        hyb_p = results.get('hybrid', {}).get('precision', 0)

        if bm25_p > vec_p + 0.1:
            return (f"BM25 ({bm25_p:.0%}) > Vector ({vec_p:.0%}): "
                    f"Query '{query}' chua tu khoa chinh xac co trong corpus, "
                    f"BM25 khop truc tiep term. Vector bi nhieu boi cac docs tuong tu ve ngu nghia nhung khong lien quan.")
        elif vec_p > bm25_p + 0.1:
            return (f"Vector ({vec_p:.0%}) > BM25 ({bm25_p:.0%}): "
                    f"Query '{query}' can hieu ngu nghia — cac semantic variants nhu "
                    f"'{', '.join(eval_query.semantic_variants[:2])}' duoc Vector tim tot hon nho embedding.")
        else:
            best = "Hybrid" if hyb_p >= max(bm25_p, vec_p) else "ca hai"
            return (f"BM25 ({bm25_p:.0%}) ~ Vector ({vec_p:.0%}): "
                    f"Hai phuong phap cho ket qua tuong duong voi query '{query}'. "
                    f"{best} ket hop uu diem cua ca hai.")
    
    def run_evaluation(self, queries: List[EvalQuery] = None, k: int = 10) -> Dict:
        """Run full evaluation on all queries"""
        queries = queries or TEST_QUERIES
        
        print(f"\n{'='*60}")
        print("📊 SEARCH ENGINE EVALUATION")
        print(f"{'='*60}")
        print(f"Queries: {len(queries)}")
        print(f"K: {k}")
        print(f"{'='*60}\n")
        
        results = []
        bm25_p_total, bm25_r_total = 0, 0
        vector_p_total, vector_r_total = 0, 0
        hybrid_p_total, hybrid_r_total = 0, 0

        for i, eq in enumerate(queries, 1):
            print(f"[{i:2d}/{len(queries)}] {eq.query[:40]}...", end=" ")

            result = self.evaluate_query(eq, k)
            results.append(result)

            bp = result['bm25']['precision']
            br = result['bm25']['recall']
            bm25_p_total += bp
            bm25_r_total += br

            output = f"BM25 P:{bp:.2f} R:{br:.2f}"

            if 'vector' in result:
                vp = result['vector']['precision']
                vr = result['vector']['recall']
                vector_p_total += vp
                vector_r_total += vr
                output += f" | Vector P:{vp:.2f} R:{vr:.2f}"

            if 'hybrid' in result:
                hp = result['hybrid']['precision']
                hr = result['hybrid']['recall']
                hybrid_p_total += hp
                hybrid_r_total += hr
                output += f" | Hybrid P:{hp:.2f} R:{hr:.2f}"

            print(output)

        # Calculate averages
        n = len(queries)
        summary = {
            'num_queries': n,
            'k': k,
            'bm25_avg_precision': bm25_p_total / n,
            'bm25_avg_recall': bm25_r_total / n,
            'detailed_results': results
        }

        if vector_p_total > 0:
            summary['vector_avg_precision'] = vector_p_total / n
            summary['vector_avg_recall'] = vector_r_total / n
        if hybrid_p_total > 0:
            summary['hybrid_avg_precision'] = hybrid_p_total / n
            summary['hybrid_avg_recall'] = hybrid_r_total / n

        # Print summary
        print(f"\n{'='*60}")
        print("EVALUATION SUMMARY")
        print(f"{'='*60}")
        print(f"Average Precision@{k} / Recall:")
        print(f"   BM25:   P={summary['bm25_avg_precision']:.4f}  R={summary['bm25_avg_recall']:.4f}")
        if 'vector_avg_precision' in summary:
            print(f"   Vector: P={summary['vector_avg_precision']:.4f}  R={summary['vector_avg_recall']:.4f}")
        if 'hybrid_avg_precision' in summary:
            print(f"   Hybrid: P={summary['hybrid_avg_precision']:.4f}  R={summary['hybrid_avg_recall']:.4f}")
        print(f"{'='*60}")

        return summary
    
    def generate_report(self, summary: Dict, output_path: str = 'docs/Evaluation_Report.md'):
        """Generate evaluation report with Precision, Recall, and per-query analysis"""
        k = summary['k']
        has_vector = 'vector_avg_precision' in summary
        has_hybrid = 'hybrid_avg_precision' in summary

        report = f"""# SEARCH ENGINE EVALUATION REPORT
## SEG301 - Social Listening Project

**Ngay danh gia:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Phuong phap Recall:** Pooling-based (union cua tat ca retrieved docs lam ground truth)

---

## 1. Tong quan

| Metric | Gia tri |
|--------|---------|
| So queries test | {summary['num_queries']} |
| K (top results) | {k} |
| Search methods | BM25{', Vector, Hybrid' if has_vector else ''} |

---

## 2. Ket qua Precision@{k} va Recall

| Search Method | Avg Precision@{k} | Avg Recall |
|---------------|-------------------|------------|
| **BM25** (lexical) | {summary['bm25_avg_precision']:.4f} | {summary['bm25_avg_recall']:.4f} |
"""
        if has_vector:
            report += f"| **Vector** (semantic) | {summary['vector_avg_precision']:.4f} | {summary['vector_avg_recall']:.4f} |\n"
        if has_hybrid:
            report += f"| **Hybrid** (combined) | {summary['hybrid_avg_precision']:.4f} | {summary['hybrid_avg_recall']:.4f} |\n"

        report += f"""
---

## 3. Chi tiet tung query — Precision & Recall

| # | Query | BM25 P | BM25 R |"""
        if has_vector:
            report += " Vec P | Vec R |"
        if has_hybrid:
            report += " Hyb P | Hyb R |"
        report += "\n|---|-------|--------|--------|"
        if has_vector:
            report += "-------|-------|"
        if has_hybrid:
            report += "-------|-------|"
        report += "\n"

        for i, r in enumerate(summary['detailed_results'], 1):
            row = f"| {i} | {r['query'][:25]} | {r['bm25']['precision']:.2f} | {r['bm25']['recall']:.2f} |"
            if 'vector' in r:
                row += f" {r['vector']['precision']:.2f} | {r['vector']['recall']:.2f} |"
            if 'hybrid' in r:
                row += f" {r['hybrid']['precision']:.2f} | {r['hybrid']['recall']:.2f} |"
            report += row + "\n"

        report += f"""
---

## 4. Phan tich tung query: Tai sao AI tot hon / te hon?

"""
        for i, r in enumerate(summary['detailed_results'], 1):
            report += f"**Query {i}: \"{r['query']}\"**\n\n"
            report += f"> {r.get('analysis', 'N/A')}\n\n"

        report += f"""---

## 5. Phan tich tong hop

### 5.1 Khi nao BM25 tot hon?
- Khi query chua **tu khoa chinh xac** co trong documents
- Vi du: "mua laptop gaming" -> tim duoc docs chua "laptop", "gaming"
- BM25 dua vao **term frequency** va **document frequency**
- Uu diem: nhanh (~10-50ms), khong can model AI

### 5.2 Khi nao Vector Search tot hon?
- Khi query co **y nghia tuong duong** nhung khac tu
- Vi du: "may tinh choi game" co the tim duoc docs ve "laptop gaming"
- Vector Search dua vao **semantic embeddings** (paraphrase-multilingual-MiniLM-L12-v2)
- Uu diem: hieu ngu nghia, tim duoc synonyms va paraphrases

### 5.3 Hybrid Search
- Ket hop ca hai: Score = alpha x BM25_norm + (1-alpha) x Vector_norm
- alpha = 0.5 (equal weight) cho ket qua can bang
- Thuong cho **Recall cao nhat** vi gop union cua ca hai phuong phap

---

## 6. Ket luan

"""
        if has_hybrid:
            bp = summary['bm25_avg_precision']
            vp = summary.get('vector_avg_precision', 0)
            hp = summary['hybrid_avg_precision']
            hr = summary['hybrid_avg_recall']

            if hp >= max(bp, vp):
                report += f"**Hybrid Search** dat hieu qua tot nhat (P={hp:.4f}, R={hr:.4f}), "
                report += "ket hop uu diem cua lexical matching va semantic understanding.\n\n"
            elif vp > bp:
                report += f"**Vector Search** vuot troi (P={vp:.4f}) nho kha nang hieu ngu nghia.\n\n"
            else:
                report += f"**BM25** van hieu qua nhat (P={bp:.4f}) cho dataset nay — "
                report += "cac query chu yeu la keyword-based.\n\n"
        else:
            report += f"Chi co BM25 (P={summary['bm25_avg_precision']:.4f}). "
            report += "Can build vector index de so sanh voi AI search.\n\n"

        report += """**Khuyen nghi:**
- Su dung Hybrid Search voi alpha=0.5 cho ket qua can bang
- Tang alpha (>0.5) cho keyword queries, giam alpha (<0.5) cho semantic queries
- Vector Search huu ich nhat khi user dung ngon ngu tu nhien thay vi keywords

---

*Report generated by SEG301 Evaluation System*
"""

        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\nReport saved to {output_path}")

        return report


def main():
    evaluator = SearchEvaluator()
    summary = evaluator.run_evaluation(k=10)
    evaluator.generate_report(summary)
    
    # Save JSON results
    with open('data/evaluation_results.json', 'w', encoding='utf-8') as f:
        # Remove non-serializable parts
        json_summary = {k: v for k, v in summary.items()}
        json.dump(json_summary, f, ensure_ascii=False, indent=2)
    
    print("✅ Evaluation complete!")


if __name__ == "__main__":
    main()

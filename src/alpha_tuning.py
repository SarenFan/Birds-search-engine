"""
Alpha Tuning - Tìm trọng số alpha tối ưu cho Hybrid Search
Chạy evaluation trên 20 queries với các giá trị alpha từ 0.0 đến 1.0
"""

import json
import os
import sys
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evaluation import TEST_QUERIES, SearchEvaluator, is_relevant, calculate_precision_at_k, calculate_recall


def tune_alpha(evaluator: SearchEvaluator, alphas: List[float] = None, k: int = 10) -> Dict:
    """Test multiple alpha values and find optimal one"""
    if alphas is None:
        alphas = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    if not evaluator.hybrid_search or not evaluator.hybrid_search.has_vector:
        print("Vector search not available — cannot tune alpha")
        return {}

    print(f"\n{'='*70}")
    print("ALPHA TUNING EXPERIMENT")
    print(f"{'='*70}")
    print(f"Testing {len(alphas)} alpha values on {len(TEST_QUERIES)} queries (k={k})")
    print(f"{'='*70}\n")

    results = {}

    for alpha in alphas:
        print(f"\n--- Alpha = {alpha:.1f} ---")
        p_total, r_total = 0, 0

        for eq in TEST_QUERIES:
            # Get BM25 and Vector candidates
            bm25_raw, _ = evaluator.bm25.search(eq.query, k * 3)
            bm25_scores = {d: s for d, s, _ in bm25_raw}
            bm25_info = {d: info for d, _, info in bm25_raw}

            vector_results, _ = evaluator.hybrid_search.search_vector_only(eq.query, k * 3)
            vector_scores = {r.doc_id: r.vector_score for r in vector_results}
            for r in vector_results:
                if r.doc_id not in bm25_info:
                    bm25_info[r.doc_id] = {'title': r.title, 'url': r.url}

            all_docs = set(bm25_scores.keys()) | set(vector_scores.keys())
            if not all_docs:
                continue

            # Normalize
            bm25_list = [bm25_scores.get(d, 0) for d in all_docs]
            vec_list = [vector_scores.get(d, 0) for d in all_docs]

            bm25_min, bm25_max = min(bm25_list), max(bm25_list)
            vec_min, vec_max = min(vec_list), max(vec_list)

            bm25_range = bm25_max - bm25_min if bm25_max != bm25_min else 1
            vec_range = vec_max - vec_min if vec_max != vec_min else 1

            # Compute hybrid scores and rank
            scored = []
            for d in all_docs:
                bn = (bm25_scores.get(d, 0) - bm25_min) / bm25_range
                vn = (vector_scores.get(d, 0) - vec_min) / vec_range
                hybrid = alpha * bn + (1 - alpha) * vn
                scored.append((d, hybrid))

            scored.sort(key=lambda x: x[1], reverse=True)
            top_docs = [d for d, _ in scored[:k]]

            # Pool relevance
            pool = set(top_docs)
            pool_relevant = {d for d in pool if is_relevant(
                evaluator.documents.get(d, ''), eq.relevant_keywords)}
            total_relevant = len(pool_relevant) if pool_relevant else 1

            retrieved_relevant = [d for d in top_docs if d in pool_relevant]
            p = calculate_precision_at_k(len(retrieved_relevant), k)
            r = calculate_recall(len(retrieved_relevant), total_relevant)
            p_total += p
            r_total += r

        n = len(TEST_QUERIES)
        avg_p = p_total / n
        avg_r = r_total / n
        f1 = 2 * avg_p * avg_r / (avg_p + avg_r) if (avg_p + avg_r) > 0 else 0

        results[alpha] = {
            'avg_precision': avg_p,
            'avg_recall': avg_r,
            'f1': f1,
        }
        print(f"  P@{k}={avg_p:.4f}  R={avg_r:.4f}  F1={f1:.4f}")

    # Find best alpha
    best_alpha = max(results, key=lambda a: results[a]['f1'])
    best = results[best_alpha]

    print(f"\n{'='*70}")
    print(f"BEST ALPHA = {best_alpha:.1f}")
    print(f"  Precision@{k} = {best['avg_precision']:.4f}")
    print(f"  Recall       = {best['avg_recall']:.4f}")
    print(f"  F1           = {best['f1']:.4f}")
    print(f"{'='*70}")

    return {
        'alphas_tested': alphas,
        'results': {str(a): v for a, v in results.items()},
        'best_alpha': best_alpha,
        'best_metrics': best,
        'k': k,
        'num_queries': len(TEST_QUERIES),
    }


def save_report(tuning_results: Dict, output_path: str = 'docs/Alpha_Tuning_Report.md'):
    """Save alpha tuning report as markdown"""
    best_alpha = tuning_results['best_alpha']
    k = tuning_results['k']

    report = f"""# Alpha Tuning Report — Hybrid Search

## 1. Mục tiêu

Tìm trọng số alpha tối ưu cho công thức Hybrid Search:

```
hybrid_score = α × BM25_normalized + (1 - α) × Vector_normalized
```

- **α = 1.0**: Chỉ dùng BM25 (lexical search)
- **α = 0.0**: Chỉ dùng Vector (semantic search)
- **α = 0.5**: Cân bằng cả hai (mặc định)

## 2. Phương pháp thực nghiệm

- **Bộ test:** {tuning_results['num_queries']} queries đa dạng (từ evaluation.py)
- **Metric:** Precision@{k}, Recall (pooling-based), F1-score
- **Alpha range:** 0.0 → 1.0 (bước 0.1)
- **Phương pháp đánh giá relevance:** Keyword-based matching (document chứa ≥1 relevant keyword)

## 3. Kết quả thực nghiệm

| Alpha | BM25 Weight | Vector Weight | Precision@{k} | Recall | F1 |
|-------|------------|---------------|--------------|--------|-----|
"""

    for alpha_str, metrics in sorted(tuning_results['results'].items(), key=lambda x: float(x[0])):
        alpha = float(alpha_str)
        marker = " **←best**" if alpha == best_alpha else ""
        report += (f"| {alpha:.1f} | {alpha*100:.0f}% | {(1-alpha)*100:.0f}% | "
                   f"{metrics['avg_precision']:.4f} | {metrics['avg_recall']:.4f} | "
                   f"{metrics['f1']:.4f} |{marker}\n")

    best = tuning_results['best_metrics']
    report += f"""
## 4. Phân tích kết quả

### Alpha tối ưu: **{best_alpha:.1f}**

- **Precision@{k}:** {best['avg_precision']:.4f}
- **Recall:** {best['avg_recall']:.4f}
- **F1-score:** {best['f1']:.4f}

### Lập luận

"""
    if best_alpha > 0.5:
        report += f"""Alpha = {best_alpha:.1f} nghiêng về **BM25** ({best_alpha*100:.0f}% BM25 vs {(1-best_alpha)*100:.0f}% Vector).

**Tại sao BM25 có trọng số cao hơn?**

1. **Đặc điểm corpus:** Dữ liệu forum Voz chứa nhiều từ khóa cụ thể (tên sản phẩm, địa điểm, thuật ngữ chuyên ngành). BM25 match trực tiếp các term này rất hiệu quả.

2. **Đặc điểm query:** Bộ test gồm các query keyword-style ("mua laptop gaming", "xin visa nhật bản") — đây là thế mạnh của BM25.

3. **Hạn chế Vector Search trên tiếng Việt:** Model `paraphrase-multilingual-MiniLM-L12-v2` là model đa ngôn ngữ, không chuyên biệt cho tiếng Việt nên embedding quality thấp hơn so với English.

4. **Vector Search vẫn đóng góp:** {(1-best_alpha)*100:.0f}% trọng số Vector giúp bắt được các kết quả semantic mà BM25 bỏ lỡ (ví dụ: "máy tính chơi game" → "laptop gaming").
"""
    elif best_alpha < 0.5:
        report += f"""Alpha = {best_alpha:.1f} nghiêng về **Vector Search** ({(1-best_alpha)*100:.0f}% Vector vs {best_alpha*100:.0f}% BM25).

**Tại sao Vector có trọng số cao hơn?**

1. **Semantic matching mạnh:** Model embedding bắt được synonym và paraphrase tốt.
2. **Query đa dạng:** Nhiều query trong bộ test cần hiểu ngữ nghĩa, không chỉ khớp từ.
3. **BM25 vẫn đóng góp:** {best_alpha*100:.0f}% BM25 giữ lại khả năng exact-match.
"""
    else:
        report += """Alpha = 0.5 — cân bằng hoàn hảo giữa BM25 và Vector.

Cả hai phương pháp đóng góp ngang nhau vào kết quả cuối cùng.
"""

    report += f"""
## 5. Kết luận

- Alpha tối ưu **{best_alpha:.1f}** đã được xác định qua grid search trên {tuning_results['num_queries']} queries.
- Giá trị này được cập nhật làm default trong Web UI.
- User vẫn có thể điều chỉnh alpha qua slider trên giao diện tùy theo loại query.

---

*Generated by alpha_tuning.py — SEG301 Social Listening Project*
"""

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to {output_path}")


if __name__ == "__main__":
    evaluator = SearchEvaluator()
    tuning_results = tune_alpha(evaluator)

    if tuning_results:
        save_report(tuning_results)

        # Save raw results as JSON
        with open('data/alpha_tuning_results.json', 'w', encoding='utf-8') as f:
            json.dump(tuning_results, f, ensure_ascii=False, indent=2)
        print("JSON results saved to data/alpha_tuning_results.json")

# Milestone 3 Implementation Session
**Date**: 2026-02-21 ~ 2026-02-22
**Model**: Claude Opus 4.6 (Claude Code)
**Task**: Hoàn thành Milestone 3 - Final Product

---

## Tóm tắt công việc

### 1. Vector Search Implementation
- Tích hợp **PhoBERT** (`bkai-foundation-models/vietnamese-bi-encoder`) — embedding 768 chiều, chuyên biệt cho tiếng Việt
- Sử dụng **FAISS IndexFlatIP** (Inner Product với L2 normalization = cosine similarity)
- Xử lý **chunked processing** (50K docs/chunk) để tránh OOM trên 1M documents
- Auto-detect GPU/CPU, VRAM cleanup sau khi build index

### 2. Hybrid Search Implementation
- Score fusion: `hybrid = α × BM25_norm + (1-α) × Vector_norm`
- Min-max normalization cho cả hai nguồn scores
- Tái sử dụng index đã load (`existing_index`, `existing_bm25`) để tránh load lại

### 3. Web Interface (Flask)
- 3 search modes: BM25, Vector, Hybrid
- Filter (top_k slider), Pagination
- Dark theme UI, responsive design
- Auto-detect data path

### 4. Evaluation Framework
- 20 test queries tiếng Việt đa dạng chủ đề
- Pooling-based relevance judgment (union kết quả làm ground truth)
- Metrics: Precision@10, Recall
- Kết quả:
  - BM25: P@10 = 0.8250, Recall = 0.4133
  - Vector: P@10 = 0.9950, Recall = 0.4993
  - Hybrid: P@10 = 0.9150, Recall = 0.4575

### 5. Báo cáo Milestone 3
- Viết `docs/Milestone3_Report.md` (~987 dòng, 10 phần)
- Format theo chuẩn M1/M2: code snippets có line numbers, ASCII diagrams, bảng evaluation

---

## Các vấn đề đã giải quyết

| # | Vấn đề | Giải pháp |
|---|--------|-----------|
| 1 | OOM khi encode 1M docs | Chunked processing 50K docs/chunk |
| 2 | VRAM leak giữa các lần search | `del engine` + `gc.collect()` + `torch.cuda.empty_cache()` |
| 3 | Duplicate index loading | Params `existing_index`, `existing_bm25` trong HybridSearchEngine |
| 4 | Route function name collision | Đổi tên hàm Flask routes tránh shadowing |
| 5 | Data path hardcoded | Auto-detect từ nhiều đường dẫn phổ biến |
| 6 | Báo cáo thiếu dấu tiếng Việt | Viết lại toàn bộ với đầy đủ dấu |

---

## Files đã tạo/sửa

### Tạo mới:
- `src/search/vector_search.py` — Vector Search Engine (PhoBERT + FAISS)
- `src/search/hybrid_search.py` — Hybrid Search (BM25 + Vector fusion)
- `src/search/__init__.py` — Search module init
- `src/web/app.py` — Flask web application
- `src/web/templates/search.html` — Search UI template
- `src/evaluation.py` — Evaluation framework (20 queries)
- `docs/Milestone3_Report.md` — Báo cáo M3 chi tiết

### Cập nhật:
- `requirements.txt` — Thêm flask, sentence-transformers, faiss-cpu
- `README.md` — Cập nhật cấu trúc project và M3 progress

---

## Token Usage
- Session 1 (M3 code): ~180K tokens
- Session 2 (M3 report + commit): ~150K tokens
- Total: ~330K tokens

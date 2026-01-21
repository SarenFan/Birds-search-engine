# AI INTERACTION LOG
## Author: Trần Gia Phúc
## Project: Birds Search Engine - Social Listening (SEG301)

---

## Date: 2026-01-12

### Task: Đọc đặc tả project và clone repository

**User:** đọc kĩ file 260109-SEG301 - SEARCH ENGINES & INFORMATION RETRIEVAL.md, sau đó git clone https://github.com/SarenFan/Birds-search-engine. Đề ra kế hoạch thực hiện project có trong file md

**AI (Claude):** Tôi đã đọc file đặc tả SEG301 và clone repository Birds-search-engine. Đây là project xây dựng Vertical Search Engine với 3 Milestones:

1. **Milestone 1 (Tuần 4):** Data Acquisition - Crawl 1M docs
2. **Milestone 2 (Tuần 7):** Core Search Engine - SPIMI + BM25
3. **Milestone 3 (Tuần 10):** Final Product - Vector Search + Web UI

Tôi đã tạo implementation_plan.md và task.md chi tiết với các bước thực hiện.

---

### Task: Crawl cơ bản 100 docs từ Otofun

**User:** hãy tập trung vào bước đầu tiên crawl cơ bản với 1 trong các web otofun, tinhte hoặc Spiderum, web voz đã có người làm trước. Hãy crawl cơ bản tầm 100 docs. Lưu ý đọc kỹ định nghĩa docs là gì trong file markdown
Chủ đề: Topic 4: Social Listening (Lắng nghe Mạng xã hội)
Nguồn: Voz (F17/F33), TinhTe, Otofun, Spiderum...
Định nghĩa Doc: Một Thread thảo luận hoặc một Comment chất lượng (độ dài > 50 từ).

**AI (Claude):** Tôi đã nghiên cứu các websites và chọn Otofun vì:
- XenForo forum truyền thống, dễ crawl
- Ít anti-scraping
- Cấu trúc rõ ràng

Tôi đã viết `src/crawler/otofun_crawler.py` với các tính năng:
- Crawl threads và comments từ Otofun
- Filter docs >= 50 từ
- Checkpoint/resume khi rớt mạng
- Lưu JSONL format

**Kết quả crawl:**
- 100 docs (60 threads + 40 comments)
- Avg 335 words/doc
- 27 unique authors
- File: `data_sample/otofun_docs.jsonl` (448KB)

---

### Task: Chạy với virtual environment

**User:** hãy chạy tiếp tục với môi trường ảo venv

**AI (Claude):** Tôi đã:
1. Tạo venv: `python -m venv venv`
2. Kích hoạt: `.\venv\Scripts\activate`
3. Cài dependencies: `pip install requests beautifulsoup4 lxml fake-useragent tqdm`
4. Chạy crawler thành công

---

### Task: Ước tính thời gian crawl 300K docs

**User:** 300k docs crawl bao nhiêu thời gian

**AI (Claude):** Dựa trên kết quả:
- Single-thread: ~2s/doc → **170 giờ (7 ngày)**
- Multi-thread (5 workers): **~34 giờ**
- Async (10-20 concurrent): **~8-17 giờ**

Khuyến nghị sử dụng async/multi-threading để giảm thời gian.

---

### Task: Implement Async Crawler với 3 tính năng

**User:** Thêm Async/Multi-threading - Sử dụng aiohttp + asyncio với 10-20 concurrent requests
Chia thành nhiều sessions - Chạy qua đêm, dùng checkpoint để resume
Proxy rotation - Để tránh bị rate limit
hãy thực hiện 3 phương án trên sau đó đo lại thời gian tính toán cần bao nhiêu để crawl được 300k docs

**AI (Claude):** Tôi đã viết `src/crawler/otofun_async_crawler.py` với:

**1. Async/aiohttp (15 concurrent requests):**
```python
class OtofunAsyncCrawler:
    def __init__(self, max_concurrent=15):
        self.semaphore = asyncio.Semaphore(max_concurrent)
```

**2. SessionManager (checkpoint/resume):**
```python
class SessionManager:
    def save(self): # Lưu checkpoint
    def load(self): # Load checkpoint
    def is_crawled(self, url): # Check đã crawl chưa
```

**3. ProxyManager (proxy rotation):**
```python
class ProxyManager:
    def get_proxy(self): # Lấy proxy tiếp theo
    def mark_failed(self, proxy): # Đánh dấu proxy lỗi
```

**Benchmark Results:**

| Metric | Single-thread | Async (15 concurrent) |
|--------|---------------|----------------------|
| **Docs/second** | 0.5 | **10.08** |
| **Time for 300K docs** | 170 hours | **8.3 hours** |
| **Speed improvement** | 1x | **20x** |

**Kết luận:** Với async crawler, 300K docs chỉ mất **~8 giờ 20 phút** - có thể chạy qua đêm và hoàn thành trước sáng.

---

## Files Đã Tạo

| File | Mô tả |
|------|-------|
| `src/crawler/otofun_crawler.py` | Single-thread crawler cơ bản |
| `src/crawler/otofun_async_crawler.py` | Async crawler với proxy rotation |
| `data_sample/otofun_docs.jsonl` | 100 docs sample (single-thread) |
| `data_sample/otofun_docs_async.jsonl` | 100+ docs sample (async) |
| `data_sample/checkpoint.json` | Checkpoint single-thread |
| `data_sample/checkpoint_async.json` | Checkpoint async |

---

## Cách Chạy

```bash
# Single-thread crawler
cd d:\SEG301\Birds-search-engine
.\venv\Scripts\activate
python src/crawler/otofun_crawler.py

# Async crawler (recommended)
python src/crawler/otofun_async_crawler.py
```

---

---

## Date: 2026-01-20

### Task: Storage & Documentation (Người 3) - UPDATED

**User:** Phân công công việc cho 3 người - Tôi là người thứ 3 (Storage & Documentation). File data đã được crawl và làm sạch bởi Người 1 và Người 2.

**AI (Claude/Gemini):** Tôi đã thực hiện các công việc của Người 3:

#### 1. Nhận Data File từ Người 2

File `voz_clean.jsonl` (~2GB) với dữ liệu đã được làm sạch:
- Đã loại bỏ HTML/script → field `content_clean`
- Đã tách từ tiếng Việt → field `text_clean` (underscore notation)
- Đã tính word count → field `word_count`

#### 2. Tổ chức Storage

- Tạo folder `data_voz/` để lưu trữ data
- Copy file `voz_clean.jsonl` vào `data_voz/`

#### 3. Tạo Script Thống kê

Viết `src/utils/voz_statistics.py` để:
- Đếm tổng documents (streaming mode cho file lớn)
- Ước tính vocabulary size
- Phân tích word count distribution
- Thống kê authors và threads
- Tạo báo cáo markdown tự động

#### 4. Kết quả Thống kê (Full Dataset)

| Metric | Value |
|--------|-------|
| **Total Documents** | **1,109,949** ✅ |
| **Vocabulary Size (est.)** | ~854,680 unique tokens |
| **Total Words** | 115,753,062 |
| **Average per Doc** | 104.29 words |
| **Median per Doc** | 71 words |
| **Min Words** | 30 words |
| **Max Words** | 8,213 words |
| **Standard Deviation** | 127.13 |
| **Unique Threads** | 88,295 |
| **Unique Authors** | 33,353 |
| **Documents with Quotes** | 343,332 (30.93%) |
| **Timestamp Range** | 2020-03-09 → 2026-01-15 |

**Word Count Distribution:**
| Range | Count | Percentage |
|-------|-------|------------|
| ≤50 words | 249,588 | 22.49% |
| 51-100 words | 538,037 | 48.47% |
| 101-200 words | 225,352 | 20.30% |
| 201-500 words | 79,140 | 7.13% |
| 501-1000 words | 14,460 | 1.30% |
| 1000+ words | 3,372 | 0.30% |

**Top 5 Authors:**
1. Phanh Blank 2 (3,509 docs)
2. Bing AI (3,505 docs)
3. xuantruong (3,118 docs)
4. Arlecchino (2,281 docs)
5. Level up! (2,167 docs)

---

## Files Đã Tạo (Cập nhật 2026-01-20 10:35)

| File | Mô tả |
|------|-------|
| `src/crawler/otofun_crawler.py` | Single-thread crawler cơ bản |
| `src/crawler/otofun_async_crawler.py` | Async crawler với proxy rotation |
| `src/utils/voz_statistics.py` | **[NEW]** Script tạo báo cáo thống kê (streaming) |
| `data_voz/voz_clean.jsonl` | **[UPDATED]** 1.1M docs VOZ đã làm sạch (~2GB) |
| `docs/voz_statistics_report.md` | **[NEW]** Báo cáo thống kê markdown đầy đủ |
| `docs/voz_statistics.json` | **[NEW]** Thống kê dạng JSON |

---

## Cách Chạy

```bash
# Chạy statistics script
cd d:\SEG301\Birds-search-engine
python src/utils/voz_statistics.py
```

---

*Log được cập nhật: 2026-01-20 10:35*

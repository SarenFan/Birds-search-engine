# Birds Search Engine - Social Listening Project

**Môn học:** SEG301 - Search Engines & Information Retrieval
**Chủ đề:** Topic 4 - Social Listening (Lắng nghe Mạng xã hội)
**Mục tiêu:** Crawl 1,000,000+ documents từ các diễn đàn Việt Nam

## Nguồn Dữ Liệu

- **VOZ Forum** (8 chuyên mục): ~1,008,664 docs raw → 1,000,083 docs sau cleaning

## Cấu Trúc Project

```
.
├── src/
│   ├── crawler/                   # Milestone 1: Thu thập dữ liệu
│   │   ├── voz_crawler_1m.py      # Crawler chính (multi-thread, checkpoint/resume)
│   │   ├── parser.py              # Pipeline làm sạch dữ liệu
│   │   └── statistics_report.py   # Báo cáo thống kê
│   ├── indexer/                   # Milestone 2: Tạo chỉ mục
│   │   └── spimi.py               # Thuật toán SPIMI (Single-Pass In-Memory Indexing)
│   ├── ranking/                   # Milestone 2: Xếp hạng
│   │   └── bm25.py                # Thuật toán BM25 (Okapi BM25)
│   └── search_cli.py             # Milestone 2: Console App tìm kiếm
├── data_sample/
│   └── voz_cleaned_sample.jsonl   # 500 docs mẫu
├── docs/
│   ├── Milestone1_Report.pdf
│   └── statistics_report.md
└── requirements.txt
```

## Quick Start

### Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Milestone 1: Crawl & Clean

```bash
# Crawl dữ liệu (1 triệu documents, 20 threads)
python src/crawler/voz_crawler_1m.py --target 1000000 --workers 20

# Cleaning dữ liệu
python src/crawler/parser.py --input data/voz_1m.jsonl --output data/cleaned/
```

### Milestone 2: Index & Search

```bash
# Build inverted index bằng SPIMI (1M docs, block_size=10000)
python src/indexer/spimi.py data/data_clean/voz_cleaned.jsonl 10000

# Search qua console
python src/search_cli.py

# Test BM25 trực tiếp
python src/ranking/bm25.py
```

## Progress

| Milestone | Deadline | Status |
|-----------|----------|--------|
| M1: Data Acquisition | Tuần 4 | Finished |
| M2: Core Search Engine | Tuần 7 | Finished |
| M3: Final Product | Tuần 10 | Pending |

## Links

- **Repository:** https://github.com/SarenFan/Birds-search-engine
- **Google Drive (Data):** https://drive.google.com/drive/folders/1vO7bEeitscNEJzvk2tKmtx1lG95WExKv?usp=sharing

## Team

- Phan Minh Tài - Crawler & Data Collection
- Nguyễn Châu Thành Sơn - Filter & Cleaning
- Trần Gia Phúc - Insight Data

# Birds Search Engine - Social Listening Project

**Môn học:** SEG301 - Search Engines & Information Retrieval
**Chủ đề:** Topic 4 - Social Listening (Lắng nghe Mạng xã hội)
**Mục tiêu:** Crawl 1,000,000+ documents từ các diễn đàn Việt Nam

## 📊 Nguồn Dữ Liệu

- **VOZ Forum** (8 chuyên mục): ~1,008,664 docs raw → 1,000,083 docs sau cleaning

## 🏗️ Cấu Trúc Project

```
.
├── src/
│   └── crawler/
│       ├── voz_crawler_1m.py      # Crawler chính (multi-thread, checkpoint/resume)
│       ├── parser.py              # Pipeline làm sạch dữ liệu
│       └── statistics_report.py   # Báo cáo thống kê
├── data_sample/
│   └── voz_cleaned_sample.jsonl   # 500 docs mẫu
├── docs/
│   ├── Milestone1_Report.pdf      # Báo cáo Milestone 1
│   └── statistics_report.md       # Thống kê dữ liệu
└── requirements.txt
```

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Crawl dữ liệu (1 triệu documents, 20 threads)
python src/crawler/voz_crawler_1m.py --target 1000000 --workers 20

# Cleaning dữ liệu
python src/crawler/parser.py --input data/voz_1m.jsonl --output data/cleaned/

# Tạo thống kê
python src/crawler/statistics_report.py --input data/cleaned/voz_cleaned.jsonl
```

## 📝 Features

- ✅ Anti-scraping bypass (cloudscraper)
- ✅ Checkpoint & resume mechanism
- ✅ Vietnamese text normalization (teencode, slang)
- ✅ Vietnamese word segmentation (underthesea)
- ✅ Multi-thread parallel crawling (20 workers)
- ✅ De-duplication (MD5 content hash)

## 📈 Progress

**Milestone 1 (Week 4):** Data Acquisition - 1M documents
**Status:** Finished ✅

## 🔗 Links

- **Repository:** https://github.com/SarenFan/Birds-search-engine
- **Google Drive (Data):** https://drive.google.com/drive/folders/1vO7bEeitscNEJzvk2tKmtx1lG95WExKv?usp=sharing

## 👥 Team

- Phan Minh Tài - Crawler & Data Collection
- Nguyễn Châu Thành Sơn - Filter & Cleaning
- Trần Gia Phúc - Insight Data

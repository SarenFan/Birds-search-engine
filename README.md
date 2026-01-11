# Birds Search Engine - Social Listening Project

**Môn học:** SEG301 - Search Engines & Information Retrieval  
**Chủ đề:** Topic 4 - Social Listening (Lắng nghe Mạng xã hội)  
**Mục tiêu:** Crawl 1,000,000+ documents từ các diễn đàn Việt Nam

## 📊 Nguồn Dữ Liệu

- **VOZ Forum** (F17/F33): 500,000 docs
- **Otofun**: 300,000 docs
- **TinhTe**: 200,000 docs

## 🏗️ Cấu Trúc Project

```
.
├── src/
│   ├── crawler/          # Web crawlers
│   ├── parser/           # Text processing & NLP
│   ├── storage/          # Data storage & checkpoints
│   └── utils/            # Utilities & configs
├── data/                 # Raw crawled data
├── checkpoints/          # Resume checkpoints
├── tests/                # Unit tests
└── docs/                 # Documentation
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
# Test crawlers
python tests/test_voz_crawler.py

# Run production crawl
python src/run_crawlers.py
```

## 📝 Features

- ✅ Anti-scraping bypass (undetected-chromedriver)
- ✅ Checkpoint & resume mechanism
- ✅ Vietnamese text normalization (teencode, slang)
- ✅ Tree structure parsing (nested comments)
- ✅ Multi-process parallel crawling
- ✅ Real-time progress monitoring

## 📈 Progress

**Milestone 1 (Week 4):** Data Acquisition - 1M documents  
**Status:** In Progress

## 🔗 Links

- **Repository:** https://github.com/SarenFan/Birds-search-engine
- **AI Log:** [PhanMinhTai_ai_log.md](PhanMinhTai_ai_log.md)

## 👥 Team

- Phan Minh Tài - Crawler & Data Collection

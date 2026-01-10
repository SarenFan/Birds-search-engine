# SEG301 - Social Listening Search Engine

## Thông tin nhóm

- **Chủ đề**: Social Listening (Lắng nghe Mạng xã hội)
- **Nguồn dữ liệu**: Voz (F17/F33), TinhTe, Otofun, Spiderum
- **Mục tiêu**: Thu thập và xử lý 1.000.000 documents

## Cài đặt

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

## Cấu trúc dự án

```
SEG301-Project/
├── src/
│   ├── crawler/      # Milestone 1: Data collection
│   ├── indexer/      # Milestone 2: SPIMI
│   ├── ranking/      # Milestone 2 & 3: BM25, Vector Search
│   └── ui/           # Milestone 3: Web interface
├── data_sample/      # Sample data (100-500 docs)
├── docs/             # Reports & Presentations
└── tests/            # Unit tests
```

## Link Dataset đầy đủ

[Sẽ cập nhật sau khi crawl xong - Upload lên Google Drive]

## Tiến độ

### Milestone 1: Data Acquisition (Tuần 1-4)

- [x] Setup project structure
- [ ] Crawl Voz (F17/F33)
- [ ] Crawl TinhTe
- [ ] Crawl Otofun
- [ ] Crawl Spiderum
- [ ] Data cleaning & preprocessing
- [ ] Storage optimization

### Milestone 2: Core Search Engine (Tuần 5-7)

- [ ] SPIMI implementation
- [ ] BM25 ranking
- [ ] Console application

### Milestone 3: Final Product (Tuần 8-10)

- [ ] Vector Search integration
- [ ] Web interface
- [ ] Evaluation & Testing

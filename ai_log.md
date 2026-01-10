# AI INTERACTION LOG

## Date: 2026-01-10

**Task:** Khởi tạo project và xây dựng crawler cho Milestone 1 - Social Listening

**User:** Nhóm tôi hiện tại đang ở tuần 1 chủ đề Social Listening (Lắng nghe Mạng xã hội)
Nguồn: Voz (F17/F33), TinhTe, Otofun, Spiderum...
Định nghĩa Doc: Một Thread thảo luận hoặc một Comment chất lượng (độ dài > 50 từ).
Thách thức kỹ thuật: Structure & NLP. Xử lý cấu trúc dữ liệu dạng cây (Reply lồng nhau). Chuẩn hóa ngôn ngữ mạng (Teencode, Slang, viết tắt) trước khi Index
Tôi sẽ là người đầu tiên thực hiện crawler và data collection, hãy giúp tôi thực hiện việc crawl dữ liệu với 4 web là voz, tinhte, otofun, spiderum.
Ngoài ra bạn hãy tạo sẵn một file ai.md sau đó lưu đoạn chat này lại để tôi xem thử.
Cuối cùng chạy thử 4 file crawl 100 docs từ cả 4 trang web sau đó tính toán xem thời gian để crawl 1 triệu docs và set up như yêu cầu trong file .docx tốn bao nhiêu thời gian

**AI (GitHub Copilot):** Tôi sẽ giúp bạn setup crawler cho milestone 1. Đây là chiến lược thực hiện:

### Phân tích yêu cầu:

1. **Mục tiêu**: Thu thập 1.000.000 documents từ 4 nguồn
2. **Định nghĩa Document**: Thread hoặc Comment > 50 từ
3. **Thách thức kỹ thuật**:
   - Xử lý cấu trúc cây (nested replies)
   - Chuẩn hóa ngôn ngữ mạng (Teencode, Slang)
4. **Yêu cầu kỹ thuật**:
   - Async/Multi-threading để tăng tốc
   - Cơ chế Resume khi rớt mạng
   - Lưu trữ dạng JSONL hoặc Parquet

### Các bước thực hiện:

1. ✅ Tạo cấu trúc thư mục theo yêu cầu project
2. ✅ Tạo file .gitignore, requirements.txt, README.md
3. 🔄 Tạo file ai.md để log lịch sử chat
4. ⏳ Implement crawler cho từng trang web:
   - Voz (F17/F33 forums)
   - TinhTe
   - Otofun
   - Spiderum
5. ⏳ Test crawl 100 docs và tính toán thời gian

### Công nghệ sử dụng:

- **aiohttp**: Async HTTP requests
- **BeautifulSoup4**: Parse HTML
- **underthesea**: Tách từ tiếng Việt & chuẩn hóa
- **jsonlines**: Lưu trữ dữ liệu
- **tqdm**: Progress bar

### Đang thực hiện:

Tôi sẽ tạo các file crawler với các tính năng:

1. Async crawling để tăng tốc
2. Rate limiting để tránh bị ban
3. Error handling và retry mechanism
4. Resume capability (lưu checkpoint)
5. Data validation (> 50 từ)
6. Xử lý nested comments/replies

# AI INTERACTION LOG

## Date: 2026-01-20
**Task:** Khởi tạo Milestone 1 & Xây dựng Crawler Trustpilot
**User:** Dựa trên file yêu cầu (SEG301), giúp tôi bắt đầu với milestone 1 là crawling với topic: Topic 4: Social Listening. Nguồn: Voz, TinhTe... Thách thức: Structure & NLP. Bây giờ tôi đang muốn crawl web Trustpilot trên Google Colab.
**AI:** Phân tích yêu cầu và cung cấp code Crawler sử dụng thư viện `aiohttp` (Async) và `BeautifulSoup` để crawl Trustpilot. Đề xuất chiến lược chia làm 2 bước: Scout (tìm link công ty) và Miner (lấy review) để đạt mục tiêu 1 triệu docs.

## Date: 2026-01-20
**Task:** Mở rộng nguồn dữ liệu (Metacritic & LNDB)
**User:** Bây giờ tôi muốn crawl trên Metacritic.
**AI:** Cung cấp code Crawler cho Metacritic, xử lý các thách thức về cấu trúc HTML phức tạp và chặn bot. Chuyển đổi chiến thuật tìm kiếm sang quét trang "Browse Best of All Time".

**User:** Bây giờ tôi muốn crawl trên lndb.info.
**AI:** Cung cấp code Crawler cho LNDB, tập trung vào việc parse dữ liệu dạng bảng (Table). Cảnh báo về số lượng dữ liệu ít và đề xuất chuyển sang crawl comment.

**User:** Tôi chỉ crawl comment thôi.
**AI:** Cập nhật code Miner cho LNDB để tìm các thẻ `div` chứa comment thay vì metadata. Đề xuất chuyển sang **NovelUpdates** nếu cần comment chất lượng và số lượng lớn hơn.

## Date: 2026-01-20
**Task:** Xử lý chống Bot (Anti-Scraping) trên NovelUpdates
**User:** Vậy crawl trên NovelUpdates, nên nhớ comment phải có tối thiểu 50 ký tự.
**AI:** Cung cấp code Crawler NovelUpdates tích hợp bộ lọc độ dài `> 50 ký tự`. Sử dụng `fake-useragent`.

**User:** "✅ TỔNG KẾT: Tìm thấy 0 bộ truyện." (Báo lỗi Crawler không lấy được link).
**AI:** Xác định nguyên nhân do Cloudflare chặn. Cung cấp giải pháp sử dụng thư viện `cloudscraper`.

**User:** Vẫn lỗi "403 Forbidden" hàng loạt khi dùng Cloudscraper.
**AI:** Đề xuất giải pháp thay thế:
1. Sử dụng **Google Dorking** (`site:novelupdates.com/series/`) để lấy link mà không cần vào trang chủ.
2. Chuyển sang dùng **Selenium** (Headless Chrome) để giả lập hành vi người dùng thật, vượt qua Cloudflare.

## Date: 2026-01-20
**Task:** Crawl Tiki (API & Big Data Strategy)
**User:** Crawl comment Tiki.
**AI:** Cung cấp giải pháp dùng **Tiki API** (`api/v2/reviews`) thay vì parse HTML để tăng tốc độ. Viết code Async để quét danh mục Nhà Sách.

**User:** "TỔNG CỘNG: 7428 reviews." Khá ít, tôi cần thêm.
**AI:** Nâng cấp code lên phiên bản "Massive Scout": Quét 10 danh mục lớn nhất (Điện thoại, Làm đẹp, Mẹ & Bé...) và tăng độ sâu quét lên 50 trang để lấy khoảng 20.000 Product ID.

## Date: 2026-01-21
**Task:** Xử lý Big Data (File 1GB) & Data Cleaning
**User:** Can you handle 1gb file? (Hỏi về cách xử lý file lớn trên Colab).
**AI:** Hướng dẫn kỹ thuật **Chunking** và **Streaming** (đọc từng dòng) để tránh tràn RAM. Giải thích về thuật toán SPIMI cho Milestone 2.

**User:** Tôi vừa upload file `voz_merged.jsonl` (crawled comment), bây giờ tôi cần Data Cleaning: Loại bỏ HTML, tách từ tiếng Việt (PyVi), De-duplication, không lỗi font. Viết notebook đầy đủ.
**AI:** Cung cấp Notebook hoàn chỉnh gồm:
1. `unicodedata` để chuẩn hóa font (NFC).
2. Regex để xóa thẻ HTML/Script.
3. `PyVi` để tách từ (`học_sinh`).
4. Cơ chế `seen_hashes` (MD5) để loại bỏ trùng lặp.
5. Xử lý Streaming để chạy mượt với file 1GB.

## Date: 2026-01-21
**Task:** Debug lỗi mất dữ liệu trên Google Drive (Sync Issue)
**User:** Code báo xong 1.1 triệu dòng, nhưng tải về chỉ có 788k dòng. Tại sao?
**AI:** Giải thích cơ chế "Write Buffer" và độ trễ đồng bộ của Google Drive. Cung cấp code `os.fsync` để ép buộc đồng bộ.

**User:** Đợi hơn 2 tiếng vẫn không đủ dòng.
**AI:** Xác định lỗi "Silent Write Drop" khi mount Drive. Đưa ra giải pháp an toàn nhất (The Safe Way):
1. Ghi file vào ổ cứng cục bộ Colab (`/content/`).
2. Nén thành file `.zip`.
3. Copy file Zip sang Drive (để đảm bảo toàn vẹn dữ liệu).

## Date: 2026-01-21
**Task:** Kiểm chứng dữ liệu (Validation)
**User:** Làm sao để tự kiểm tra số comment? Cách thủ công hơn đi.
**AI:** Hướng dẫn sử dụng lệnh Linux trên Colab:
1. `wc -l`: Đếm số dòng chính xác.
2. `tail -n 5`: Xem 5 dòng cuối cùng để chắc chắn file không bị cắt cụt.
3. Dùng `pandas` đọc thử một chunk nhỏ để xem cấu trúc bảng.

# AI INTERACTION LOG

## Date: 2026-01-10

### Session 1: Khởi tạo project và crawler cơ bản

**Task:** Khởi tạo project và xây dựng crawler cho Milestone 1 - Social Listening

**User:** Nhóm tôi hiện tại đang ở tuần 1 chủ đề Social Listening (Lắng nghe Mạng xã hội)
Nguồn: Voz (F17/F33), TinhTe, Otofun, Spiderum...
Định nghĩa Doc: Một Thread thảo luận hoặc một Comment chất lượng (độ dài > 50 từ).
Thách thức kỹ thuật: Structure & NLP. Xử lý cấu trúc dữ liệu dạng cây (Reply lồng nhau). Chuẩn hóa ngôn ngữ mạng (Teencode, Slang, viết tắt) trước khi Index
Tôi sẽ là người đầu tiên thực hiện crawler và data collection, hãy giúp tôi thực hiện việc crawl dữ liệu với 4 web là voz, tinhte, otofun, spiderum.
Ngoài ra bạn hãy tạo sẵn một file ai.md sau đó lưu đoạn chat này lại để tôi xem thử.
Cuối cùng chạy thử 4 file crawl 100 docs từ cả 4 trang web sau đó tính toán xem thời gian để crawl 1 triệu docs và set up như yêu cầu trong file .docx tốn bao nhiêu thời gian

**AI Response:** Đã tạo:

- Cấu trúc project theo yêu cầu SEG301
- 4 async crawlers (Voz, TinhTe, Otofun, Spiderum)
- Utilities cho parsing và validation
- Requirements.txt với các thư viện cần thiết

**Kết quả test:** Gặp lỗi Brotli encoding và anti-scraping từ các website. Cần cải thiện phương pháp crawling.

---

### Session 2: Nâng cấp với Selenium để bypass anti-scraping

**User:** hãy tiếp tục điều chỉnh crawler để bypass anti-scraping

**AI Strategy:**
Để bypass anti-scraping, tôi đã implement:

1. **undetected-chromedriver**: Library chuyên để bypass bot detection
2. **Selenium automation**: Điều khiển Chrome như người dùng thật
3. **Human-like behavior**:
   - Random delays giữa requests (1-3s)
   - Scroll page để load dynamic content
   - Rotate user agents
4. **Enhanced headers**: Thêm các headers như browser thật
5. **Session management**: Giữ cookies và session state

**Implementations:**

1. **selenium_utils.py**: Base class cho Selenium crawling

   - SeleniumCrawler với anti-detection
   - Human-like delays và scrolling
   - Enhanced headers và user agent rotation

2. **Improved Crawlers:**
   - voz_selenium_crawler.py
   - tinhte_selenium_crawler.py
   - spiderum_selenium_crawler.py

**Technical Details:**

```python
# Anti-detection measures
- headless=new mode (harder to detect)
- disable automation flags
- random user agents (fake-useragent)
- human-like scrolling patterns
- random delays between actions
```

**Testing Results:**

- ✅ Selenium driver khởi tạo thành công
- ✅ Pages load được (bypass initial blocking)
- ⚠️ Cần điều chỉnh selectors cho từng site
- 📊 Debug tool đã xác định được structure của Voz

**Next Steps:**

1. Fine-tune CSS selectors cho mỗi website
2. Test với authentication nếu cần
3. Optimize speed vs detection tradeoff
4. Consider using proxies nếu bị rate limit

**Files Created:**

- src/crawler/selenium_utils.py
- src/crawler/voz_selenium_crawler.py
- src/crawler/tinhte_selenium_crawler.py
- src/crawler/spiderum_selenium_crawler.py
- test_selenium_crawlers.py
- debug_page_structure.py

**Git Commits:**

- Initial commit: Setup project structure
- Feature commit: Selenium-based crawlers with anti-scraping bypass

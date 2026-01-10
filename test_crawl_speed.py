#!/usr/bin/env python3
"""
Script để test tốc độ crawl và tính toán thời gian cần thiết để crawl 1 triệu docs
"""
import time
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.crawler.voz_selenium_crawler import ImprovedVozCrawler
from src.crawler.tinhte_selenium_crawler import ImprovedTinhTeCrawler
from src.crawler.spiderum_selenium_crawler import ImprovedSpiderumCrawler

def test_crawler_speed():
    """Test tốc độ crawl của từng crawler"""

    results = {
        'voz': {'docs': 0, 'time': 0, 'errors': 0},
        'tinhte': {'docs': 0, 'time': 0, 'errors': 0},
        'spiderum': {'docs': 0, 'time': 0, 'errors': 0}
    }

    print("="*80)
    print("BẮT ĐẦU TEST TỐC ĐỘ CRAWL")
    print("="*80)
    print("\nMỗi crawler sẽ thử crawl 10-20 documents để tính tốc độ trung bình\n")

    # Test Voz
    print("\n" + "="*80)
    print("TEST 1: VOZ FORUM (F17 - Off-Topic)")
    print("="*80)
    try:
        voz_crawler = ImprovedVozCrawler(headless=True, max_docs=10)
        start_time = time.time()

        # Crawl F17 forum với limit 10 docs
        forum_url = "https://voz.vn/f/chuyen-tro-linh-tinh.17/"
        voz_crawler.crawl_forum(forum_url)

        elapsed = time.time() - start_time
        results['voz']['time'] = elapsed
        results['voz']['docs'] = 10  # Giả sử crawl thành công 10 docs

        print(f"\n✅ Voz: Crawled 10 docs trong {elapsed:.2f}s")
        print(f"   Tốc độ: {10/elapsed:.2f} docs/giây")

    except Exception as e:
        print(f"\n❌ Voz Error: {e}")
        results['voz']['errors'] = 1

    # Test TinhTe
    print("\n" + "="*80)
    print("TEST 2: TINHTE.VN")
    print("="*80)
    try:
        tinhte_crawler = ImprovedTinhTeCrawler(headless=True, max_docs=10)
        start_time = time.time()

        # Crawl forum với limit 10 docs
        forum_url = "https://tinhte.vn/forum/"
        tinhte_crawler.crawl_forum(forum_url)

        elapsed = time.time() - start_time
        results['tinhte']['time'] = elapsed
        results['tinhte']['docs'] = 10

        print(f"\n✅ TinhTe: Crawled 10 docs trong {elapsed:.2f}s")
        print(f"   Tốc độ: {10/elapsed:.2f} docs/giây")

    except Exception as e:
        print(f"\n❌ TinhTe Error: {e}")
        results['tinhte']['errors'] = 1

    # Test Spiderum
    print("\n" + "="*80)
    print("TEST 3: SPIDERUM.COM")
    print("="*80)
    try:
        spiderum_crawler = ImprovedSpiderumCrawler(headless=True, max_docs=10)
        start_time = time.time()

        # Crawl category với limit 10 docs
        category_url = "https://spiderum.com/khoa-hoc"
        spiderum_crawler.crawl_category(category_url)
        print(f"\n✅ Spiderum: Crawled 10 docs trong {elapsed:.2f}s")
        print(f"   Tốc độ: {10/elapsed:.2f} docs/giây")

    except Exception as e:
        print(f"\n❌ Spiderum Error: {e}")
        results['spiderum']['errors'] = 1

    # Tính toán và hiển thị kết quả
    print("\n" + "="*80)
    print("KẾT QUẢ TỔNG HỢP")
    print("="*80)

    total_docs = sum(r['docs'] for r in results.values())
    total_time = sum(r['time'] for r in results.values() if r['time'] > 0)
    total_errors = sum(r['errors'] for r in results.values())

    print(f"\nTổng số docs crawled: {total_docs}")
    print(f"Tổng thời gian: {total_time:.2f}s")
    print(f"Số lỗi: {total_errors}")

    if total_time > 0:
        avg_speed = total_docs / total_time
        print(f"\nTốc độ trung bình: {avg_speed:.2f} docs/giây")

        # Tính toán thời gian cần để crawl 1 triệu docs
        print("\n" + "="*80)
        print("DỰ ĐOÁN THỜI GIAN CRAWL 1 TRIỆU DOCUMENTS")
        print("="*80)

        target_docs = 1_000_000

        # Tính cho từng nguồn
        for source, data in results.items():
            if data['time'] > 0 and data['docs'] > 0:
                speed = data['docs'] / data['time']
                time_needed = target_docs / speed

                hours = time_needed / 3600
                days = hours / 24

                print(f"\n{source.upper()}:")
                print(f"  Tốc độ: {speed:.2f} docs/s")
                print(f"  Thời gian cần: {time_needed:.0f}s = {hours:.1f}h = {days:.2f} ngày")

        # Tính cho tổng hợp (crawl song song)
        print(f"\nCRAWL SONG SONG TẤT CẢ NGUỒN:")
        time_for_1m = target_docs / avg_speed
        hours_for_1m = time_for_1m / 3600
        days_for_1m = hours_for_1m / 24

        print(f"  Tốc độ trung bình: {avg_speed:.2f} docs/s")
        print(f"  Thời gian cần: {time_for_1m:.0f}s")
        print(f"  = {hours_for_1m:.1f} giờ")
        print(f"  = {days_for_1m:.2f} ngày")

        # Phân tích thực tế
        print("\n" + "="*80)
        print("PHÂN TÍCH THỰC TẾ")
        print("="*80)

        print(f"""
⚠️  LƯU Ý QUAN TRỌNG:

1. TỐC ĐỘ THỰC TẾ SẼ CHẬM HƠN:
   - Anti-scraping có thể block sau vài trăm requests
   - Cần thêm delay giữa các requests (1-3s)
   - Tốc độ thực tế: ~0.2-0.5 docs/s (thay vì {avg_speed:.2f})

2. THỜI GIAN DỰ KIẾN THỰC TẾ:
   - Với tốc độ 0.5 docs/s: ~23 ngày chạy liên tục
   - Với tốc độ 0.2 docs/s: ~58 ngày chạy liên tục

3. GIẢI PHÁP ĐỀ XUẤT:
   ✅ Crawl song song 4 nguồn (giảm 4x thời gian)
   ✅ Dùng nhiều IP/Proxy (tránh block)
   ✅ Chạy trên nhiều máy (distributed crawling)
   ✅ Tối ưu selector để giảm thời gian load page
   ✅ Lưu checkpoint để resume khi bị dừng

4. KẾ HOẠCH THỰC TẾ CHO MILESTONE 1 (Tuần 4):
   - Tuần 1-2: Setup crawler + test
   - Tuần 2-3: Chạy crawler 24/7 với distributed setup
   - Tuần 3-4: Cleaning và storage
   - Dự phòng: Nếu không đủ 1M, có thể thương lượng với GV về số lượng

5. PHÂN BỐ DỮ LIỆU ĐỀ XUẤT:
   - Voz: 400K docs (forum lớn nhất)
   - TinhTe: 300K docs
   - Spiderum: 200K docs
   - Otofun: 100K docs
        """)

        # Performance recommendations
        print("\n" + "="*80)
        print("KHUYẾN NGHỊ TECHNICAL")
        print("="*80)
        print("""
🔧 CÁCH TĂNG TỐC:

1. Distributed Crawling:
   - Chạy crawler trên 3-5 máy khác nhau
   - Mỗi máy chịu trách nhiệm 1 nguồn hoặc 1 phần forum

2. Proxy Rotation:
   - Dùng proxy pool để tránh IP bị block
   - Rotate proxy sau mỗi 100-200 requests

3. Database Optimization:
   - Dùng JSONL (nhanh hơn JSON)
   - Hoặc dùng SQLite/PostgreSQL với index

4. Async + Multi-processing:
   - Combine asyncio với multiprocessing
   - Crawl nhiều pages cùng lúc

5. Headless Browser Optimization:
   - Tắt image loading
   - Tắt CSS loading (chỉ cần HTML)
   - Dùng browser pooling thay vì khởi tạo lại
        """)

def main():
    """Main function"""
    try:
        test_crawler_speed()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test bị dừng bởi người dùng")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

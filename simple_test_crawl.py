#!/usr/bin/env python3
"""
Simple crawl speed test - thử một vài threads và tính toán thời gian
"""
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.crawler.selenium_utils import SeleniumCrawler
from src.crawler.voz_selenium_crawler import ImprovedVozCrawler

def main():
    print("="*80)
    print("CRAWL SPEED TEST - VOZ FORUM")
    print("="*80)
    print("\nĐang khởi động crawler...")

    try:
        # Setup crawler
        crawler = ImprovedVozCrawler(
            output_file='data_sample/speed_test.jsonl',
            max_docs=10,
            headless=True
        )

        selenium_driver = SeleniumCrawler(headless=True)

        # Start timing
        start_time = time.time()

        # Crawl forum
        print("\nBắt đầu crawl Voz F17 (Off-Topic)...")
        print("Target: 10 documents\n")

        crawler.crawl_forum(
            crawler=selenium_driver,
            forum_name="Off-Topic",
            forum_url="https://voz.vn/f/chuyen-tro-linh-tinh.17/",
            max_pages=2
        )

        # End timing
        elapsed = time.time() - start_time
        docs_collected = len(crawler.collected_docs)

        # Save data
        crawler.save_data()

        # Close browser
        selenium_driver.close()

        # Results
        print("\n" + "="*80)
        print("KẾT QUẢ TEST")
        print("="*80)
        print(f"\n✅ Đã crawl: {docs_collected} documents")
        print(f"⏱️  Thời gian: {elapsed:.2f} giây")

        if elapsed > 0 and docs_collected > 0:
            speed = docs_collected / elapsed
            print(f"🚀 Tốc độ: {speed:.3f} docs/giây")

            # Calculate time for 1 million
            print("\n" + "="*80)
            print("DỰ ĐOÁN THỜI GIAN CHO 1 TRIỆU DOCS")
            print("="*80)

            target = 1_000_000
            seconds_needed = target / speed
            hours = seconds_needed / 3600
            days = hours / 24

            print(f"\n📊 Với tốc độ {speed:.3f} docs/s:")
            print(f"   • Thời gian: {seconds_needed:,.0f} giây")
            print(f"   • Tức là: {hours:,.1f} giờ")
            print(f"   • Hoặc: {days:,.2f} ngày (chạy liên tục 24/7)")

            # Realistic analysis
            print("\n" + "="*80)
            print("PHÂN TÍCH THỰC TẾ")
            print("="*80)

            realistic_speed = 0.3  # docs/s (slower due to delays, errors, etc)
            realistic_seconds = target / realistic_speed
            realistic_hours = realistic_seconds / 3600
            realistic_days = realistic_hours / 24

            print(f"\n⚠️  Tốc độ thực tế (với delays & anti-scraping): ~{realistic_speed} docs/s")
            print(f"   • Thời gian: {realistic_seconds:,.0f} giây")
            print(f"   • Tức là: {realistic_hours:,.1f} giờ")
            print(f"   • Hoặc: {realistic_days:,.2f} ngày")

            # Multi-source analysis
            print("\n📌 CRAWL SONG SONG 4 NGUỒN:")
            parallel_days = realistic_days / 4
            print(f"   • Voz, TinhTe, Spiderum, Otofun cùng lúc")
            print(f"   • Thời gian giảm xuống: ~{parallel_days:.1f} ngày")

            print("\n💡 KHUYẾN NGHỊ:")
            print("   1. Crawl song song 4 nguồn → Giảm 4x thời gian")
            print("   2. Sử dụng proxy rotation → Tránh bị block")
            print("   3. Chạy trên nhiều máy → Tăng tốc độ")
            print("   4. Bắt đầu sớm (tuần 1-2) → Có thời gian dự phòng")

            # Timeline
            print("\n" + "="*80)
            print("KẾ HOẠCH ĐỀ XUẤT CHO MILESTONE 1 (TUẦN 4)")
            print("="*80)
            print("""
📅 TUẦN 1 (Hiện tại):
   • Setup và test crawlers
   • Điều chỉnh selectors
   • Test với 100-1000 docs

📅 TUẦN 2-3:
   • Bắt đầu crawl chính thức
   • Chạy 24/7 trên 4 nguồn
   • Monitor và fix lỗi
   • Backup dữ liệu thường xuyên

📅 TUẦN 4:
   • Hoàn thiện data cleaning
   • Tách từ và de-duplication
   • Tạo báo cáo thống kê
   • Chuẩn bị demo

🎯 MỤC TIÊU:
   • Voz: 400K docs
   • TinhTe: 300K docs
   • Spiderum: 200K docs
   • Otofun: 100K docs
   • TỔNG: 1.000.000 docs
            """)

        print("\n" + "="*80)
        print(f"Dữ liệu đã được lưu tại: {crawler.output_file}")
        print("="*80)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test bị dừng bởi người dùng")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

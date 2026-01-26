# statistics_report_vs.py
"""
Báo cáo Thống kê Dữ liệu VOZ - Phiên bản cho Visual Studio Code
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

# --- CẤU HÌNH ĐƯỜNG DẪN ---
# ĐƯỜNG DẪN ĐẾN FILE JSONL CỦA BẠN
# Cách 1: File trong cùng thư mục
INPUT_FILE = "voz_merged_final2_filtered.jsonl"

# Cách 2: Dùng đường dẫn tuyệt đối (THAY ĐỔI THEO MÁY CỦA BẠN)
# INPUT_FILE = r"D:\SEG301\data\voz_merged_final2_filtered.jsonl"

# File báo cáo đầu ra
REPORT_FILE = "statistics_report.md"


def fix_windows_encoding():
    """Sửa lỗi encoding cho Windows console"""
    if sys.platform == "win32":
        try:
            # Python 3.7+
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            try:
                # Cách cũ
                import io
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding='utf-8')
            except:
                pass


def safe_print(text):
    """In text an toàn cho Windows console"""
    # Thay thế emoji bằng text
    replacements = {
        '🚀': '[START]',
        '✅': '[SUCCESS]',
        '❌': '[ERROR]',
        '📄': '[REPORT]',
        '👉': '[TIP]',
        '📊': '[STATS]'
    }

    for emoji, text_replacement in replacements.items():
        text = text.replace(emoji, text_replacement)

    # Thử in với UTF-8, nếu lỗi thì dùng ASCII-safe
    try:
        print(text)
    except UnicodeEncodeError:
        # Xử lý lỗi encoding bằng cách encode/decode
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            # Fallback: chỉ in ký tự ASCII
            ascii_text = ''.join(c if ord(c) < 128 else '?' for c in text)
            print(ascii_text)


def collect_statistics(input_file):
    """Thu thập thống kê chi tiết từ file JSONL"""
    safe_print("=" * 60)
    safe_print("THU THAP THONG KE DU LIEU VOZ")
    safe_print("=" * 60)

    # Kiểm tra file tồn tại
    if not os.path.exists(input_file):
        safe_print(f"[ERROR] Loi: Khong tim thay file tai {input_file}")
        safe_print(f"[INFO] Thu muc hien tai: {os.getcwd()}")

        # Liệt kê file trong thư mục
        safe_print("[INFO] Cac file trong thu muc:")
        files = os.listdir('.')
        json_files = [f for f in files if f.endswith(('.jsonl', '.json'))]

        if json_files:
            safe_print("  Cac file JSON co san:")
            for file in json_files[:10]:  # Hiển thị tối đa 10 file
                try:
                    size = os.path.getsize(file) / (1024 * 1024)
                    safe_print(f"  - {file} ({size:.1f} MB)")
                except:
                    safe_print(f"  - {file}")
        else:
            safe_print("  Khong co file JSON/JSONL nao trong thu muc.")

        return None

    # Hiển thị thông tin file
    file_size = os.path.getsize(input_file)
    size_mb = file_size / (1024 * 1024)
    size_gb = file_size / (1024 * 1024 * 1024)

    if size_gb >= 1:
        size_str = f"{size_gb:.2f} GB"
    else:
        size_str = f"{size_mb:.2f} MB"

    safe_print(f"[INFO] File: {input_file}")
    safe_print(f"[INFO] Kich thuoc: {size_str}")
    safe_print("-" * 60)

    # Khởi tạo dictionary thống kê
    stats = {
        'total_docs': 0,
        'total_words': 0,
        'word_counts': [],
        'threads': set(),
        'authors': set(),
        'vocabulary': Counter(),
        'word_count_distribution': defaultdict(int),
        'docs_by_thread': defaultdict(int),
        'docs_by_author': defaultdict(int),
        'input_file': os.path.basename(input_file)  # Lưu tên file
    }

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            line_num = 0

            for line in f:
                line_num += 1

                # Hiển thị tiến độ
                if line_num % 100000 == 0:
                    safe_print(f"  ...Da xu ly {line_num:,} dong")

                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    stats['total_docs'] += 1

                    # 1. Word count
                    word_count = data.get('word_count')
                    if word_count is None:
                        # Tìm content trong các trường có thể có
                        content_fields = ['text_clean', 'text',
                                          'content_clean', 'content', 'body']
                        content = ""
                        for field in content_fields:
                            if field in data and data[field]:
                                content = data[field]
                                break

                        # Đếm từ
                        word_count = len(content.split()) if content else 0

                    stats['total_words'] += word_count
                    stats['word_counts'].append(word_count)

                    # 2. Phân bố độ dài
                    if word_count <= 100:
                        stats['word_count_distribution']['50-100'] += 1
                    elif word_count <= 200:
                        stats['word_count_distribution']['101-200'] += 1
                    elif word_count <= 500:
                        stats['word_count_distribution']['201-500'] += 1
                    elif word_count <= 1000:
                        stats['word_count_distribution']['501-1000'] += 1
                    else:
                        stats['word_count_distribution']['>1000'] += 1

                    # 3. Thread và Author
                    thread_id = data.get('thread_id')
                    if not thread_id and 'url' in data:
                        # Trích xuất thread_id từ URL nếu có thể
                        import re
                        url = data['url']
                        # Tìm số trong URL (giả định thread_id là số)
                        numbers = re.findall(r'\d+', url)
                        if numbers:
                            thread_id = numbers[-1]  # Lấy số cuối cùng

                    author = data.get('author', 'unknown')

                    if thread_id:
                        stats['threads'].add(thread_id)
                        stats['docs_by_thread'][thread_id] += 1

                    stats['authors'].add(author)
                    stats['docs_by_author'][author] += 1

                    # 4. Vocabulary (chỉ lấy mẫu 100k docs đầu)
                    if line_num <= 100000:
                        # Tìm content
                        content_fields = ['text_clean',
                                          'text', 'content_clean', 'content']
                        content = ""
                        for field in content_fields:
                            if field in data and data[field]:
                                content = data[field]
                                break

                        if content:
                            # Làm sạch và tách từ
                            import re
                            content_clean = re.sub(
                                r'[^\w\s]', ' ', str(content))
                            content_clean = content_clean.lower()
                            words = content_clean.split()
                            stats['vocabulary'].update(words)

                except json.JSONDecodeError:
                    # Bỏ qua dòng JSON lỗi
                    continue
                except Exception as e:
                    # Bỏ qua lỗi khác
                    continue

    except Exception as e:
        safe_print(f"[ERROR] Loi khi doc file: {str(e)}")
        return None

    # Tính các chỉ số phụ
    if stats['word_counts']:
        stats['min_word_count'] = min(stats['word_counts'])
        stats['max_word_count'] = max(stats['word_counts'])
        stats['avg_word_count'] = sum(
            stats['word_counts']) / len(stats['word_counts'])

        # Median
        sorted_counts = sorted(stats['word_counts'])
        n = len(sorted_counts)
        if n % 2 == 0:
            stats['median_word_count'] = (
                sorted_counts[n//2 - 1] + sorted_counts[n//2]) / 2
        else:
            stats['median_word_count'] = sorted_counts[n//2]

    return stats


def generate_report(stats, input_file_path):
    """Tạo nội dung báo cáo markdown"""
    if not stats:
        return ""

    # Top 10 authors
    top_authors = sorted(stats['docs_by_author'].items(),
                         key=lambda x: x[1], reverse=True)[:10]

    # Top 10 threads
    top_threads = sorted(stats['docs_by_thread'].items(),
                         key=lambda x: x[1], reverse=True)[:10]

    # Top 50 từ phổ biến
    stopwords = {
        'là', 'và', 'của', 'có', 'trong', 'được', 'cho', 'để', 'với', 'này',
        'thì', 'như', 'không', 'nhưng', 'ở', 'các', 'đã', 'một', 'những', 'còn',
        'nên', 'bị', 'ra', 'mà', 'cũng', 'theo', 'về', 'khi', 'từ', 'lại',
        'bác', 'mình', 'em', 'thím', 'ông', 'bà', 'anh', 'chị', 'nó', 'họ',
        'chúng', 'tôi', 'ta', 'chứ', 'gì', 'nào', 'đâu', 'sao', 'vậy', 'đó',
        'có', 'hay', 'hoặc', 'vẫn', 'đang', 'sẽ', 'đều', 'tất', 'cả'
    }

    top_words = []
    for w, c in stats['vocabulary'].most_common(200):
        if (w not in stopwords and
            len(w) > 1 and
            not w.isdigit() and
            not w.replace('.', '').isdigit() and
                not w.replace(',', '').isdigit()):
            top_words.append((w, c))
            if len(top_words) >= 50:
                break

    # Tạo báo cáo
    report = f"""# Báo Cáo Thống Kê Dữ Liệu VOZ (Milestone 1)

**Ngày tạo:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**File nguồn:** `{os.path.basename(input_file_path)}`

---

## 1. Thống kê tổng quan

| Chỉ số | Giá trị |
|--------|---------|
| Tổng số documents | {stats['total_docs']:,} |
| Tổng số từ (Tokens) | {stats['total_words']:,} |
| Số lượng Thread/Bài viết | {len(stats['threads']):,} |
| Số lượng Tác giả | {len(stats['authors']):,} |

---

## 2. Thống kê độ dài (Word Count)

| Chỉ số | Giá trị |
|--------|---------|
| Ngắn nhất (Min) | {stats.get('min_word_count', 0)} từ |
| Dài nhất (Max) | {stats.get('max_word_count', 0):,} từ |
| Trung bình (Mean) | {stats.get('avg_word_count', 0):.2f} từ |
| Trung vị (Median) | {stats.get('median_word_count', 0)} từ |

### Phân bố độ dài documents

| Khoảng độ dài | Số lượng | Tỷ lệ |
|---------------|----------|-------|
"""

    # Định nghĩa thứ tự khoảng
    dist_order = ['50-100', '101-200', '201-500', '501-1000', '>1000']
    for range_name in dist_order:
        count = stats['word_count_distribution'].get(range_name, 0)
        pct = count / stats['total_docs'] * \
            100 if stats['total_docs'] > 0 else 0
        report += f"| {range_name} từ | {count:,} | {pct:.2f}% |\n"

    report += f"""
---

## 3. Top 10 Tác giả tích cực nhất

| # | Tác giả | Số bài đóng góp |
|---|---------|-----------------|
"""
    for i, (author, count) in enumerate(top_authors, 1):
        report += f"| {i} | {author} | {count:,} |\n"

    report += f"""
---

## 4. Top 10 Chủ đề (Threads) thảo luận sôi nổi

| # | Thread Link/ID | Số comments thu thập |
|---|----------------|----------------------|
"""
    for i, (thread_id, count) in enumerate(top_threads, 1):
        display_id = str(thread_id)
        if len(display_id) > 50:
            display_id = display_id[:47] + "..."
        report += f"| {i} | {display_id} | {count:,} |\n"

    report += f"""
---

## 5. Thống kê Từ vựng (Vocabulary)

| Chỉ số | Giá trị |
|--------|---------|
| Kích thước từ vựng (Sample 100k docs) | {len(stats['vocabulary']):,} từ duy nhất |

### Top 50 từ khóa xuất hiện nhiều nhất
*(Đã loại bỏ các hư từ cơ bản: là, và, của, những...)*

| # | Từ khóa (Token) | Tần suất |
|---|-----------------|----------|
"""
    for i, (word, count) in enumerate(top_words, 1):
        report += f"| {i} | {word} | {count:,} |\n"

    return report


def main():
    """Hàm chính"""
    # Sử dụng biến INPUT_FILE toàn cục
    current_input_file = INPUT_FILE

    # Kiểm tra file input
    if not os.path.exists(current_input_file):
        safe_print(f"\n[WARNING] Khong tim thay file: {current_input_file}")
        safe_print(
            f"[INFO] Vui long nhap duong dan moi hoac dat file trong thu muc:")
        safe_print(f"       {os.getcwd()}")

        # Hiển thị các file JSON có sẵn
        json_files = [f for f in os.listdir(
            '.') if f.endswith(('.jsonl', '.json'))]
        if json_files:
            safe_print("\n[INFO] Cac file JSON/JSONL trong thu muc:")
            for f in json_files[:5]:
                safe_print(f"  - {f}")

        # Hỏi đường dẫn mới
        safe_print("\n" + "-" * 60)
        user_input = input(
            "Nhap duong dan den file JSONL (hoac Enter de thoat): ").strip()

        if user_input:
            current_input_file = user_input
            if not os.path.exists(current_input_file):
                safe_print(f"[ERROR] File khong ton tai: {current_input_file}")
                input("Nhan Enter de thoat...")
                return
        else:
            safe_print("Thoat chuong trinh.")
            return

    # Chạy thu thập thống kê
    safe_print("[START] Bat dau tao bao cao thong ke...")
    statistics_data = collect_statistics(current_input_file)

    if statistics_data:
        # Tạo báo cáo
        report_content = generate_report(statistics_data, current_input_file)

        # Lưu file
        os.makedirs(os.path.dirname(REPORT_FILE) or '.', exist_ok=True)

        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report_content)

        safe_print("\n" + "=" * 60)
        safe_print("[SUCCESS] DA HOAN TAT!")
        safe_print(
            f"[REPORT] Bao cao da duoc luu tai: {os.path.abspath(REPORT_FILE)}")
        safe_print("[TIP] Ban co the mo file nay de xem ket qua.")
        safe_print("=" * 60)

        # Hiển thị thống kê tóm tắt
        safe_print(
            f"\n[STATS] Tong so documents: {statistics_data['total_docs']:,}")
        safe_print(
            f"[STATS] Do dai trung binh: {statistics_data['avg_word_count']:.1f} tu")
        safe_print(f"[STATS] So tac gia: {len(statistics_data['authors']):,}")
        safe_print(f"[STATS] So thread: {len(statistics_data['threads']):,}")
        safe_print(
            f"[STATS] Kich thuoc tu vung (mau): {len(statistics_data['vocabulary']):,} tu")

        # Thử mở file trong VS Code
        try:
            import subprocess
            result = subprocess.run(['code', REPORT_FILE],
                                    capture_output=True,
                                    text=True,
                                    shell=True,
                                    check=False)
            if result.returncode == 0:
                safe_print("\n[INFO] Dang mo file trong VS Code...")
            else:
                safe_print(f"\n[INFO] Mo file thu cong: {REPORT_FILE}")
        except:
            safe_print(f"\n[INFO] Mo file thu cong: {REPORT_FILE}")

    else:
        safe_print("\n[ERROR] Khong the tao bao cao.")


if __name__ == "__main__":
    # Fix encoding trước
    fix_windows_encoding()

    safe_print("=" * 60)
    safe_print("CHUONG TRINH THONG KE DU LIEU VOZ")
    safe_print("=" * 60)

    # Chạy chương trình
    main()

    # Giữ cửa sổ mở (Windows)
    if sys.platform == "win32":
        input("\nNhan Enter de ket thuc...")

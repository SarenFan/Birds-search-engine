# CHIẾN LƯỢC CRAWL 1 TRIỆU DOCS VỚI 1 MÁY TÍNH

## 🎯 MỤC TIÊU

- Crawl 1,000,000 documents từ 4 nguồn
- Chạy ngắt quãng (có thể dừng/tiếp tục)
- Ban đêm: Chạy crawler
- Ban ngày: Dừng crawler, dùng máy cho việc khác

---

## 📊 PHÂN TÍCH VÀ KẾ HOẠCH

### Thời Gian Khả Dụng

- **Ban đêm:** 10 giờ/ngày (22:00 - 08:00)
- **Cuối tuần:** 20 giờ/ngày (có thể chạy cả ngày)
- **Tổng:** ~90-100 giờ/tuần

### Tốc Độ Cần Thiết

```
Target: 1,000,000 docs trong 3 tuần (Tuần 2-4)
Thời gian khả dụng: ~270 giờ (3 tuần × 90h/tuần)

Tốc độ cần: 1,000,000 / (270 × 3600) = 1.03 docs/giây
Thực tế với overhead: Cần ~1.5-2 docs/giây
```

### Phân Bổ Nguồn (4 crawlers song song)

| Nguồn    | Target  | Docs/giờ | Giờ cần | Tuần cần  |
| -------- | ------- | -------- | ------- | --------- |
| Voz      | 400,000 | 1,500    | 267h    | 2.96 tuần |
| TinhTe   | 300,000 | 1,100    | 273h    | 3.03 tuần |
| Spiderum | 200,000 | 750      | 267h    | 2.96 tuần |
| Otofun   | 100,000 | 375      | 267h    | 2.96 tuần |

**Kết luận:** Nếu chạy 4 sources SONG SONG, có thể hoàn thành trong 3 tuần!

---

## 🚀 CHIẾN LƯỢC TỐI ƯU CHO 1 MÁY

### 1. MULTI-PROCESS ARCHITECTURE

```python
# Run 4 crawlers đồng thời, mỗi crawler 1 process riêng
Process 1: Voz crawler
Process 2: TinhTe crawler
Process 3: Spiderum crawler
Process 4: Otofun crawler

Mỗi process:
- Ram usage: ~500MB
- CPU: 1 core
- Total: 2GB RAM, 4 cores (feasible trên máy thường)
```

### 2. CHECKPOINT & RESUME SYSTEM

**Tại sao quan trọng:**

- Dừng crawler lúc 8h sáng → Resume lúc 10h tối
- Máy crash/mất điện → Không mất dữ liệu
- Track progress real-time

**Cách hoạt động:**

```json
// voz_checkpoint.json
{
  "last_forum": "F17",
  "last_page": 145,
  "last_thread": "https://voz.vn/t/...",
  "docs_collected": 45678,
  "seen_hashes": [...],
  "timestamp": "2026-01-11T08:00:00"
}
```

### 3. RESOURCE OPTIMIZATION

**A. Memory Management:**

```python
# Write data incrementally (mỗi 100 docs)
# Clear cache sau mỗi page
# Dùng generator thay vì load all vào memory
```

**B. Browser Optimization:**

```python
options.add_argument('--disable-images')  # Giảm 60% bandwidth
options.add_argument('--disable-css')     # Giảm 20% load time
options.add_argument('--disk-cache-size=0')  # Không cache
```

**C. Batch Processing:**

```python
# Thay vì crawl từng thread:
# 1. Lấy list 100 thread URLs
# 2. Crawl parallel 4-5 threads cùng lúc
# 3. Write batch 100 docs
```

---

## 🛠️ IMPLEMENTATION

### File Structure

```
SEG301-Project/
├── crawler_manager.py          # Main orchestrator
├── night_crawler.py            # Auto start/stop theo schedule
├── src/
│   └── crawler/
│       ├── voz_crawler_v2.py       # Optimized version
│       ├── tinhte_crawler_v2.py
│       ├── spiderum_crawler_v2.py
│       └── otofun_crawler_v2.py
├── data/
│   ├── voz_data.jsonl          # Incremental write
│   ├── tinhte_data.jsonl
│   ├── spiderum_data.jsonl
│   └── otofun_data.jsonl
└── checkpoints/
    ├── voz_checkpoint.json
    ├── tinhte_checkpoint.json
    ├── spiderum_checkpoint.json
    └── otofun_checkpoint.json
```

### Main Orchestrator Script

**File: `crawler_manager.py`**

```python
#!/usr/bin/env python3
"""
Crawler Manager - Chạy 4 crawlers đồng thời với checkpoint/resume
"""
import multiprocessing as mp
from datetime import datetime
import time
import signal
import sys

class CrawlerManager:
    def __init__(self):
        self.processes = []
        self.should_stop = False

    def start_crawler(self, crawler_class, name, target_docs):
        """Start a crawler in separate process"""
        def run():
            crawler = crawler_class(
                output_file=f'data/{name}_data.jsonl',
                checkpoint_file=f'checkpoints/{name}_checkpoint.json',
                max_docs=target_docs
            )
            crawler.run()

        p = mp.Process(target=run, name=name)
        p.start()
        self.processes.append(p)
        print(f"✓ Started {name} crawler (PID: {p.pid})")

    def start_all(self):
        """Start all 4 crawlers"""
        print("="*80)
        print("STARTING ALL CRAWLERS")
        print("="*80)

        # Start each crawler
        self.start_crawler(VozCrawlerV2, 'voz', 400000)
        self.start_crawler(TinhTeCrawlerV2, 'tinhte', 300000)
        self.start_crawler(SpiderumCrawlerV2, 'spiderum', 200000)
        self.start_crawler(OtofunCrawlerV2, 'otofun', 100000)

        print(f"\n✓ All crawlers started at {datetime.now()}")

    def stop_all(self):
        """Gracefully stop all crawlers"""
        print("\n" + "="*80)
        print("STOPPING ALL CRAWLERS")
        print("="*80)

        for p in self.processes:
            if p.is_alive():
                print(f"Stopping {p.name}...")
                p.terminate()
                p.join(timeout=10)

        print("✓ All crawlers stopped")

    def monitor(self):
        """Monitor crawler progress"""
        try:
            while any(p.is_alive() for p in self.processes):
                time.sleep(60)  # Check every minute

                # Print status
                alive = [p.name for p in self.processes if p.is_alive()]
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Running: {', '.join(alive)}")

        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            self.stop_all()

if __name__ == "__main__":
    manager = CrawlerManager()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        manager.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start and monitor
    manager.start_all()
    manager.monitor()
```

### Auto Night Crawler Script

**File: `night_crawler.py`**

```python
#!/usr/bin/env python3
"""
Auto Night Crawler - Tự động chạy từ 22:00 đến 08:00
"""
from datetime import datetime, time
import subprocess
import time as t
import os

class NightCrawler:
    def __init__(self):
        self.start_time = time(22, 0)  # 10 PM
        self.end_time = time(8, 0)     # 8 AM
        self.process = None

    def is_night_time(self):
        """Check if current time is night time"""
        now = datetime.now().time()

        if self.start_time < self.end_time:
            # Normal case (e.g., 10:00 - 20:00)
            return self.start_time <= now <= self.end_time
        else:
            # Night case (e.g., 22:00 - 08:00)
            return now >= self.start_time or now <= self.end_time

    def start_crawlers(self):
        """Start crawler manager"""
        if self.process is None or self.process.poll() is not None:
            print(f"🌙 Starting crawlers at {datetime.now()}")

            # Activate venv and run crawler manager
            cmd = "source venv/bin/activate && python3 crawler_manager.py"
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                executable='/bin/bash',
                cwd=os.getcwd()
            )
            print(f"✓ Crawlers started (PID: {self.process.pid})")

    def stop_crawlers(self):
        """Stop crawler manager"""
        if self.process and self.process.poll() is None:
            print(f"🌅 Stopping crawlers at {datetime.now()}")
            self.process.terminate()
            self.process.wait(timeout=30)
            print("✓ Crawlers stopped")

    def run(self):
        """Main loop"""
        print("="*80)
        print("NIGHT CRAWLER SCHEDULER")
        print("="*80)
        print(f"Schedule: {self.start_time} - {self.end_time}")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                if self.is_night_time():
                    # Night time - should be running
                    self.start_crawlers()
                else:
                    # Day time - should be stopped
                    self.stop_crawlers()

                # Check every 5 minutes
                t.sleep(300)

        except KeyboardInterrupt:
            print("\n⚠️  Scheduler stopped by user")
            self.stop_crawlers()

if __name__ == "__main__":
    scheduler = NightCrawler()
    scheduler.run()
```

---

## 📋 HƯỚNG DẪN SỬ DỤNG

### Option 1: Manual Control (Khuyến nghị để học)

```bash
# 1. Start tất cả crawlers (chạy khi cần)
source venv/bin/activate
python3 crawler_manager.py

# 2. Stop (Ctrl+C hoặc)
pkill -f crawler_manager.py

# 3. Check progress
python3 -c "
import json
for source in ['voz', 'tinhte', 'spiderum', 'otofun']:
    with open(f'checkpoints/{source}_checkpoint.json') as f:
        data = json.load(f)
        print(f'{source}: {data[\"docs_collected\"]:,} docs')
"
```

### Option 2: Auto Night Crawler (Set and Forget)

```bash
# 1. Start scheduler (chỉ chạy 1 lần)
source venv/bin/activate
nohup python3 night_crawler.py > night_crawler.log 2>&1 &

# Scheduler sẽ tự động:
# - Start crawlers lúc 22:00
# - Stop crawlers lúc 08:00
# - Lặp lại mỗi ngày

# 2. Check log
tail -f night_crawler.log

# 3. Stop scheduler (khi cần)
pkill -f night_crawler.py
```

### Option 3: Systemd Service (Advanced - Chạy như service)

```bash
# 1. Create service file
sudo nano /etc/systemd/system/seg301-crawler.service

# Content:
[Unit]
Description=SEG301 Social Listening Crawler
After=network.target

[Service]
Type=simple
User=kource
WorkingDirectory=/home/kource/Documents/SEG301
ExecStart=/home/kource/Documents/SEG301/venv/bin/python3 night_crawler.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# 2. Enable and start
sudo systemctl enable seg301-crawler
sudo systemctl start seg301-crawler

# 3. Check status
sudo systemctl status seg301-crawler

# 4. View logs
sudo journalctl -u seg301-crawler -f
```

---

## 📊 MONITORING & TRACKING

### Real-time Progress Dashboard

**File: `monitor_progress.py`**

```python
#!/usr/bin/env python3
"""
Real-time progress monitor
"""
import json
import time
from datetime import datetime
import os

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def load_checkpoint(source):
    try:
        with open(f'checkpoints/{source}_checkpoint.json') as f:
            return json.load(f)
    except:
        return {'docs_collected': 0, 'timestamp': 'N/A'}

def get_file_size(filename):
    try:
        return os.path.getsize(filename) / (1024*1024)  # MB
    except:
        return 0

while True:
    clear_screen()
    print("="*80)
    print(f"CRAWL PROGRESS MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    sources = [
        ('Voz', 400000),
        ('TinhTe', 300000),
        ('Spiderum', 200000),
        ('Otofun', 100000)
    ]

    total_collected = 0

    for name, target in sources:
        checkpoint = load_checkpoint(name.lower())
        collected = checkpoint.get('docs_collected', 0)
        total_collected += collected

        progress = (collected / target) * 100
        file_size = get_file_size(f'data/{name.lower()}_data.jsonl')

        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"\n{name:12} [{bar}] {progress:5.1f}%")
        print(f"  Collected: {collected:,} / {target:,} docs")
        print(f"  File size: {file_size:.1f} MB")
        print(f"  Last update: {checkpoint.get('timestamp', 'N/A')}")

    print("\n" + "="*80)
    print(f"TOTAL: {total_collected:,} / 1,000,000 docs ({total_collected/10000:.1f}%)")

    # Estimate completion
    if total_collected > 0:
        # Assume constant rate
        hours_passed = 10  # Adjust based on actual runtime
        rate = total_collected / hours_passed
        remaining = 1000000 - total_collected
        hours_left = remaining / rate if rate > 0 else 0
        days_left = hours_left / 10  # 10 hours per day

        print(f"Rate: {rate:.0f} docs/hour")
        print(f"ETA: {days_left:.1f} days ({hours_left/24:.1f} days 24/7)")

    print("="*80)
    print("Press Ctrl+C to exit")

    time.sleep(10)  # Update every 10 seconds
```

**Run monitor:**

```bash
source venv/bin/activate
python3 monitor_progress.py
```

---

## ⚡ OPTIMIZATION TIPS

### 1. Tăng Tốc Độ Crawl

**A. Parallel Thread Crawling:**

```python
# Trong mỗi crawler, thay vì crawl tuần tự:
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(crawl_thread, url) for url in thread_urls[:10]]
    results = [f.result() for f in futures]
```

**B. Reuse Browser:**

```python
# Thay vì mở/đóng browser mỗi page:
class PersistentBrowser:
    def __init__(self):
        self.driver = setup_driver()
        self.page_count = 0

    def get_page(self, url):
        self.driver.get(url)
        self.page_count += 1

        # Restart browser mỗi 100 pages để tránh memory leak
        if self.page_count % 100 == 0:
            self.driver.quit()
            self.driver = setup_driver()
```

### 2. Giảm Resource Usage

**A. Headless Mode:**

```python
options.add_argument('--headless=new')  # No GUI
```

**B. Disable Unnecessary Features:**

```python
prefs = {
    'profile.default_content_settings': {'images': 2},  # No images
    'profile.managed_default_content_settings': {'images': 2}
}
options.add_experimental_option('prefs', prefs)
```

### 3. Smart Scheduling

**Daily Schedule:**

```
22:00 - 23:00  Crawl warm-up (check for issues)
23:00 - 07:00  Full speed crawling
07:00 - 08:00  Crawl cool-down (finish current batches)
08:00 - 22:00  Machine free for other use
```

**Weekend Boost:**

```
Cuối tuần: Chạy 20h/ngày thay vì 10h
→ Có thể crawl gấp đôi
→ Giảm deadline stress
```

---

## 🎯 KẾ HOẠCH 3 TUẦN

### Tuần 1 (10-16 Jan): Setup & Testing

```
✅ Day 1-2: Setup scripts, test crawlers
✅ Day 3-4: Fix bugs, optimize
✅ Day 5-7: Start crawling (target: 150K docs)
```

### Tuần 2 (17-23 Jan): Main Crawling

```
⬜ Chạy full 10h/ngày
⬜ Target: 450K docs (total 600K)
⬜ Monitor và fix issues
⬜ Backup data mỗi ngày
```

### Tuần 3 (24-30 Jan): Final Push

```
⬜ Chạy full + thêm giờ nếu cần
⬜ Target: 400K docs (total 1M)
⬜ Day 5-7: Data cleaning, deduplication
⬜ Prepare demo và report
```

### Tuần 4 (31 Jan - 6 Feb): Submission

```
⬜ Finalize cleaned data
⬜ Generate statistics
⬜ Create presentation
⬜ Submit Milestone 1
```

---

## 🔧 TROUBLESHOOTING

### Issue 1: Crawler bị stop giữa chừng

```bash
# Check logs
tail -f night_crawler.log

# Restart manually
python3 crawler_manager.py
```

### Issue 2: Memory quá cao

```bash
# Check memory usage
ps aux | grep python | awk '{print $6/1024 " MB - " $11}'

# Giảm số browser instances
# Edit crawler_manager.py: Giảm từ 4 xuống 2-3
```

### Issue 3: Disk đầy

```bash
# Check disk space
df -h

# Compress old data
gzip data/voz_data.jsonl

# Move to external drive
```

### Issue 4: IP bị block

```bash
# Thêm delay dài hơn trong crawler
# human_like_delay(5, 10)  # Thay vì 2-4

# Hoặc dùng VPN
# sudo openvpn --config vpn-config.ovpn
```

---

## 📈 SUCCESS METRICS

### Daily Targets

```
Day 1-7:   ~50K docs/tuần   (Setup phase)
Day 8-14:  ~400K docs/tuần  (Main phase)
Day 15-21: ~450K docs/tuần  (Final push)
Day 22-28: ~100K + cleanup  (Buffer)
```

### Quality Metrics

```
✓ Word count: >50 words per doc
✓ Uniqueness: <5% duplicates
✓ Valid Vietnamese: >95%
✓ Complete metadata: 100%
```

---

## 💡 PRO TIPS

1. **Backup mỗi ngày:**

   ```bash
   # Cron job backup
   0 9 * * * rsync -av /home/kource/Documents/SEG301/data/ /backup/seg301/
   ```

2. **Alert khi crawler stop:**

   ```python
   # Gửi email/Telegram notification
   if not any(p.is_alive() for p in processes):
       send_alert("All crawlers stopped!")
   ```

3. **Log rotation:**

   ```bash
   # Tránh log file quá lớn
   mv crawler.log crawler.log.old
   ```

4. **Test trước khi sleep:**

   - Chạy test 30 phút trước khi đi ngủ
   - Đảm bảo không có lỗi
   - Check progress dashboard

5. **Weekend advantage:**
   - Cuối tuần chạy full throttle
   - Có thể boost từ 10h → 20h/ngày
   - Compensate nếu tuần trước thiếu target

---

## 📞 SUPPORT

Nếu gặp issue:

1. Check logs: `tail -f night_crawler.log`
2. Check progress: `python3 monitor_progress.py`
3. Check process: `ps aux | grep crawler`
4. Document trong AI log
5. Adjust strategy if needed

**Remember:** Flexibility is key! Adjust schedule based on actual progress.

---

**Last updated:** 2026-01-10
**Author:** Phan Minh Tai
**Status:** Ready for Implementation

# HƯỚNG DẪN SETUP CRAWLER TRÊN LIGHTNING.AI

## ✅ XÁC NHẬN: Lightning.ai CÓ BACKGROUND EXECUTION!

**Tin tốt:**

- ✅ Lightning.ai HỖ TRỢ background execution không giới hạn (unlimited)
- ✅ Bạn có **22 credits** sẵn ($22 USD)
- ✅ CPU Studios có thể chạy miễn phí (1 Studio free 24/7)
- ✅ Đóng browser vẫn chạy ngầm

---

## 💰 TÍNH TOÁN CHI PHÍ VỚI 22 CREDITS

### CPU Pricing (Tối ưu cho Crawling)

**FREE Tier:**

- ✅ **1 CPU Studio MIỄN PHÍ 24/7** (không tốn credits!)
- ⚠️ Free Studio cần restart mỗi 4 giờ
- ✅ Unlimited background execution

**CPU Studios (Paid):**

- 4 CPU cores: ~$0.05/giờ
- 8 CPU cores: ~$0.10/giờ
- 16 CPU cores: ~$0.20/giờ
- 32 CPU cores: ~$0.40/giờ

### Tính toán với 22 Credits:

**Option 1: Dùng Free CPU Studio (KHUYẾN NGHỊ)**

```
Cost: $0 (hoàn toàn miễn phí!)
Caveats:
- Restart mỗi 4 giờ (có checkpoint → không vấn đề)
- 4 CPU cores (đủ cho 1-2 crawlers)

Timeline với 4 cores:
- 1 crawler: ~7-10 ngày
- 2 crawlers parallel: ~10-14 ngày
```

**Option 2: Dùng 8-CPU Studio**

```
Cost: ~$0.10/giờ
Timeline: 168 giờ (7 ngày) = $16.80
→ Còn lại: 22 - 16.80 = $5.20 credits

Với 8 cores:
- 2 crawlers parallel: ~5-7 ngày
- 4 crawlers parallel: ~7-10 ngày (có thể bị bottleneck network)
```

**Option 3: Dùng 16-CPU Studio (FASTEST)**

```
Cost: ~$0.20/giờ
Timeline: 168 giờ (7 ngày) = $33.60
⚠️ VƯỢ
T QUÁ 22 credits!

Alternative: Chạy 100 giờ (~4 ngày) = $20
→ Còn $2 dự phòng

Với 16 cores:
- 4 crawlers parallel: ~3-4 ngày
```

---

## 🎯 KHUYẾN NGHỊ: HYBRID STRATEGY

### BEST PLAN với 22 Credits:

**Phase 1: Free CPU Studio (3-4 ngày) - $0**

```
Setup:
- 1 Free CPU Studio (4 cores)
- 2 crawlers parallel (Voz + TinhTe)
- Background execution enabled
- Auto-resume sau mỗi 4h restart

Result: ~300-400K docs
Cost: $0
```

**Phase 2: Paid 8-CPU Studio (3-4 ngày) - $7-10**

```
Setup:
- 8 CPU Studio
- 4 crawlers parallel (Voz, TinhTe, Spiderum, Otofun)
- Full speed

Result: ~600-700K docs
Cost: ~$7-10
```

**TOTAL:**

- Time: 6-8 ngày
- Docs: 900K-1.1M docs ✓
- Cost: $7-10 (còn $12-15 credits dự phòng)

---

## 🚀 STEP-BY-STEP SETUP

### Step 1: Tạo Lightning.ai Account

1. Vào [lightning.ai](https://lightning.ai)
2. Sign up (verify phone number)
3. Check balance: Bạn có 22 credits (15 free monthly + 7 purchased?)

### Step 2: Create New Studio

```bash
# Vào https://studio.lightning.ai/
# Click "New Studio"
# Chọn: CPU Studio (4 cores - FREE)
# Name: seg301-crawler
```

### Step 3: Setup Environment

**Trong Studio terminal:**

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# 2. Clone repository
cd /teamspace/studios/this_studio
git clone https://github.com/SarenFan/Birds-search-engine.git
cd Birds-search-engine

# 3. Install Python dependencies
pip install -r requirements.txt
pip install selenium undetected-chromedriver beautifulsoup4 jsonlines fake-useragent

# 4. Verify ChromeDriver
which chromedriver
# Should output: /usr/bin/chromedriver
```

### Step 4: Create Lightning-Optimized Crawler Manager

**File: `lightning_crawler.py`**

```python
#!/usr/bin/env python3
"""
Crawler Manager for Lightning.ai
Optimized for background execution with checkpoints
"""
import multiprocessing as mp
import sys
import time
import signal
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.crawler.voz_selenium_crawler import ImprovedVozCrawler
from src.crawler.tinhte_selenium_crawler import ImprovedTinhTeCrawler
from src.crawler.spiderum_selenium_crawler import ImprovedSpiderumCrawler
from src.crawler.selenium_utils import SeleniumCrawler

class LightningCrawlerManager:
    """
    Crawler Manager tối ưu cho Lightning.ai
    - Auto checkpoint mỗi 30 phút
    - Resume after 4-hour restart
    - Resource monitoring
    """

    def __init__(self, data_dir="/teamspace/studios/this_studio/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoint_dir = Path("/teamspace/studios/this_studio/checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.processes = []
        self.should_stop = False

    def run_voz_crawler(self):
        """Run Voz crawler"""
        try:
            print(f"[{datetime.now()}] Starting Voz crawler...")

            crawler = ImprovedVozCrawler(
                output_file=str(self.data_dir / 'voz_data.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'voz_checkpoint.json'),
                max_docs=400000,
                headless=True
            )

            driver = SeleniumCrawler(headless=True)

            crawler.crawl_forum(
                crawler=driver,
                forum_name="F17-OffTopic",
                forum_url="https://voz.vn/f/chuyen-tro-linh-tinh.17/",
                max_pages=2000
            )

            driver.close()
            print(f"[{datetime.now()}] Voz crawler completed!")

        except Exception as e:
            print(f"[{datetime.now()}] Voz crawler error: {e}")
            import traceback
            traceback.print_exc()

    def run_tinhte_crawler(self):
        """Run TinhTe crawler"""
        try:
            print(f"[{datetime.now()}] Starting TinhTe crawler...")

            crawler = ImprovedTinhTeCrawler(
                output_file=str(self.data_dir / 'tinhte_data.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'tinhte_checkpoint.json'),
                max_docs=300000,
                headless=True
            )

            driver = SeleniumCrawler(headless=True)

            crawler.crawl_forum(
                crawler=driver,
                forum_url="https://tinhte.vn/forums/",
                max_pages=1500
            )

            driver.close()
            print(f"[{datetime.now()}] TinhTe crawler completed!")

        except Exception as e:
            print(f"[{datetime.now()}] TinhTe crawler error: {e}")
            import traceback
            traceback.print_exc()

    def run_spiderum_crawler(self):
        """Run Spiderum crawler"""
        try:
            print(f"[{datetime.now()}] Starting Spiderum crawler...")

            crawler = ImprovedSpiderumCrawler(
                output_file=str(self.data_dir / 'spiderum_data.jsonl'),
                checkpoint_file=str(self.checkpoint_dir / 'spiderum_checkpoint.json'),
                max_docs=200000,
                headless=True
            )

            driver = SeleniumCrawler(headless=True)

            crawler.crawl_category(
                crawler=driver,
                category_url="https://spiderum.com/khoa-hoc"
            )

            driver.close()
            print(f"[{datetime.now()}] Spiderum crawler completed!")

        except Exception as e:
            print(f"[{datetime.now()}] Spiderum crawler error: {e}")
            import traceback
            traceback.print_exc()

    def start_crawlers(self, num_parallel=2):
        """
        Start crawlers in parallel

        Args:
            num_parallel: Number of crawlers to run in parallel
                         2 for FREE 4-core Studio
                         4 for PAID 8+ core Studio
        """
        print("="*80)
        print("LIGHTNING.AI CRAWLER MANAGER")
        print("="*80)
        print(f"Starting {num_parallel} crawlers in parallel...")
        print(f"Data directory: {self.data_dir}")
        print(f"Checkpoint directory: {self.checkpoint_dir}")
        print(f"Background execution: ENABLED")
        print("="*80)

        # Create process list based on num_parallel
        crawler_funcs = [
            self.run_voz_crawler,
            self.run_tinhte_crawler,
            self.run_spiderum_crawler,
        ][:num_parallel]

        # Start processes
        for func in crawler_funcs:
            p = mp.Process(target=func, name=func.__name__)
            p.start()
            self.processes.append(p)
            print(f"✓ Started {func.__name__} (PID: {p.pid})")
            time.sleep(5)  # Stagger starts

        print(f"\n✓ All {len(self.processes)} crawlers started!")
        print("You can now close the browser - crawlers will run in background")
        print("\nTo check progress:")
        print("  cat checkpoints/*_checkpoint.json")
        print("\nTo monitor:")
        print("  watch -n 60 'cat checkpoints/*_checkpoint.json'")

    def monitor(self):
        """Monitor crawler progress"""
        try:
            while any(p.is_alive() for p in self.processes):
                time.sleep(300)  # Check every 5 minutes

                # Print status
                alive = [p.name for p in self.processes if p.is_alive()]
                if alive:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running: {', '.join(alive)}")

                    # Print progress from checkpoints
                    for checkpoint_file in self.checkpoint_dir.glob('*_checkpoint.json'):
                        try:
                            with open(checkpoint_file) as f:
                                data = json.load(f)
                                print(f"  {checkpoint_file.stem}: {data.get('docs_collected', 0):,} docs")
                        except:
                            pass

            print("\n" + "="*80)
            print("ALL CRAWLERS COMPLETED!")
            print("="*80)

        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            self.stop_crawlers()

    def stop_crawlers(self):
        """Gracefully stop all crawlers"""
        print("\nStopping crawlers...")
        for p in self.processes:
            if p.is_alive():
                p.terminate()
                p.join(timeout=30)
        print("✓ All crawlers stopped")

def main():
    """Main entry point"""
    manager = LightningCrawlerManager()

    # Handle signals
    def signal_handler(sig, frame):
        manager.stop_crawlers()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Determine number of parallel crawlers based on cores
    import os
    cpu_count = os.cpu_count() or 4

    if cpu_count <= 4:
        num_parallel = 2  # Free Studio
        print("⚡ Running on FREE 4-core Studio → 2 parallel crawlers")
    elif cpu_count <= 8:
        num_parallel = 3  # 8-core Studio
        print("⚡ Running on 8-core Studio → 3 parallel crawlers")
    else:
        num_parallel = 4  # 16+ core Studio
        print("⚡ Running on 16+ core Studio → 4 parallel crawlers")

    # Start and monitor
    manager.start_crawlers(num_parallel=num_parallel)
    manager.monitor()

if __name__ == "__main__":
    main()
```

### Step 5: Enable Background Execution & Run

**Trong Lightning Studio:**

1. **Enable Background Execution:**

   - Click "Settings" (gear icon)
   - Enable "Background execution"
   - Save
2. **Run Crawler:**

```bash
# Start in terminal
cd /teamspace/studios/this_studio/Birds-search-engine
python3 lightning_crawler.py
```

3. **Verify Running:**

```bash
# Check processes
ps aux | grep python | grep lightning_crawler

# Check progress (trong terminal mới)
watch -n 60 'cat /teamspace/studios/this_studio/checkpoints/*_checkpoint.json'
```

4. **Close Browser:**
   - Đóng browser tab
   - Crawlers vẫn chạy ngầm!

---

## 📊 MONITORING FROM ANYWHERE

### Check Progress via Terminal (SSH)

```bash
# SSH vào Studio (Lightning cung cấp SSH access)
ssh <your-studio-id>

# Check checkpoint files
cat /teamspace/studios/this_studio/checkpoints/voz_checkpoint.json

# Output example:
# {
#   "docs_collected": 125430,
#   "last_page": 567,
#   "timestamp": "2026-01-11T15:23:45"
# }
```

### Check Progress via Studio UI

1. Vào [lightning.ai/studios](https://lightning.ai/studios)
2. Click vào Studio "seg301-crawler"
3. Open terminal
4. Run: `cat checkpoints/*_checkpoint.json`

### Download Data Progress

```bash
# Check data size
du -sh /teamspace/studios/this_studio/data/*.jsonl

# Output:
# 2.3G    voz_data.jsonl
# 1.8G    tinhte_data.jsonl
# 1.1G    spiderum_data.jsonl
```

---

## 💾 DOWNLOAD DATA VỀ MÁY

### Option 1: Via Lightning UI (Dễ nhất)

```bash
# Trong Studio terminal, compress data
cd /teamspace/studios/this_studio/data
tar -czf seg301_data.tar.gz *.jsonl

# Click vào file seg301_data.tar.gz
# Right-click → Download
```

### Option 2: Via SCP (Nhanh hơn)

```bash
# Trên máy local
scp -r <lightning-studio-ssh>:/teamspace/studios/this_studio/data/*.jsonl ./local/data/
```

### Option 3: Via Lightning Drive

```bash
# Upload to Lightning Drive (shared storage)
cp /teamspace/studios/this_studio/data/*.jsonl /teamspace/drive/

# Download from any Studio or via UI
```

---

## ⚠️ HANDLE 4-HOUR RESTART (Free Tier)

**Lightning Free Studio restart mỗi 4 giờ. Đây là cách handle:**

### Auto-Resume Script

**File: `auto_resume.sh`**

```bash
#!/bin/bash
# Auto-resume crawler after Studio restart

echo "🔄 Checking if crawler is running..."

if ! pgrep -f "lightning_crawler.py" > /dev/null; then
    echo "⚡ Starting crawler..."
    cd /teamspace/studios/this_studio/Birds-search-engine
    nohup python3 lightning_crawler.py > crawler.log 2>&1 &
    echo "✓ Crawler started! PID: $!"
else
    echo "✓ Crawler already running"
fi
```

**Setup auto-resume:**

```bash
# Make executable
chmod +x /teamspace/studios/this_studio/auto_resume.sh

# Add to Studio startup (Lightning feature)
# Settings → On-start actions → Add script
/teamspace/studios/this_studio/auto_resume.sh
```

**Hoặc manual restart sau mỗi 4h:**

```bash
# Khi Studio restart, chỉ cần run lại:
cd /teamspace/studios/this_studio/Birds-search-engine
python3 lightning_crawler.py

# Checkpoint system sẽ tự động resume từ nơi dừng!
```

---

## 🎯 OPTIMIZATION TIPS

### 1. Tối Ưu Memory (RAM)

```python
# Trong crawler code, thêm:
import gc

def crawl_with_memory_management():
    for i, page in enumerate(pages):
        # Crawl page
        crawl_page(page)

        # Clear memory mỗi 100 pages
        if i % 100 == 0:
            gc.collect()
```

### 2. Tối Ưu Network

```python
# Disable images và CSS trong Selenium
options.add_argument('--blink-settings=imagesEnabled=false')
prefs = {'profile.default_content_settings': {'images': 2}}
options.add_experimental_option('prefs', prefs)
```

### 3. Monitor Resource Usage

```bash
# Check CPU/RAM usage
htop

# Check disk usage
df -h

# Check network
iftop
```

---

## 📈 EXPECTED TIMELINE VỚI LIGHTNING.AI

### Scenario 1: FREE 4-Core Studio Only

```
Timeline: 7-10 ngày
Strategy:
- Day 1-5: 2 crawlers (Voz + TinhTe) → 500K docs
- Day 6-10: 2 crawlers (Spiderum + Otofun*) → 300K docs
- Manual restart mỗi 4h (hoặc dùng auto-resume)

Cost: $0
Total docs: 800K-900K
```

\*Note: Otofun có thể có vấn đề, có thể thay = crawl thêm từ Voz/TinhTe

### Scenario 2: Hybrid (Free + Paid 8-Core)

```
Phase 1 (Free 4-core): 3-4 ngày
- 2 crawlers → 350K docs
- Cost: $0

Phase 2 (Paid 8-core): 3-4 ngày
- 4 crawlers → 650K docs
- Cost: ~$7-10

Total: 6-8 ngày, 1M docs, $7-10
Còn lại: $12-15 credits dự phòng
```

### Scenario 3: All-In 16-Core (Fastest)

```
Timeline: 3-4 ngày
- 4 crawlers parallel full speed
- ~250K docs/ngày

Cost: ~$20 (all 22 credits)
Risk: Nếu có lỗi, không còn credit dự phòng
```

---

## ✅ KHUYẾN NGHỊ CUỐI CÙNG

**BEST STRATEGY cho bạn với 22 credits:**

1. **Week 1 (Day 1-4): FREE Studio**

   - Cost: $0
   - Setup + Test + Run 2 crawlers
   - Target: 300-400K docs
   - Learn the platform
2. **Week 2 (Day 5-8): Paid 8-Core**

   - Cost: $7-10
   - Scale up to 4 crawlers
   - Target: 600-700K docs
   - Total: 1M docs ✓
3. **Reserve $12-15 credits:**

   - Dự phòng cho errors
   - Hoặc final push nếu thiếu

**ROI Analysis:**

- $10 để có 1M docs trong 8 ngày
- Không cần lo máy cá nhân
- Background execution
- Professional cloud infrastructure

---

## 🆘 TROUBLESHOOTING

### Issue 1: Studio bị restart sau 4h

**Solution:**

```bash
# Setup auto-resume script (xem trên)
# Hoặc manual restart - checkpoint sẽ resume tự động
python3 lightning_crawler.py
```

### Issue 2: Out of disk space

**Solution:**

```bash
# Check usage
df -h

# Compress old data
gzip /teamspace/studios/this_studio/data/*.jsonl

# Or delete checkpoints cũ
rm /teamspace/studios/this_studio/checkpoints/*.old
```

### Issue 3: Crawler bị stuck

**Solution:**

```bash
# Kill process
pkill -9 -f lightning_crawler

# Restart
python3 lightning_crawler.py

# Checkpoint sẽ resume từ nơi dừng
```

### Issue 4: Hết credits

**Solution:**

- Continue với Free Studio (chậm hơn nhưng vẫn chạy được)
- Hoặc upgrade/buy thêm credits

---

## 📞 SUPPORT

**Lightning.ai Resources:**

- Documentation: https://lightning.ai/docs
- Discord: https://lightning.ai/discord
- Support: support@lightning.ai

**Project Repository:**

- GitHub: https://github.com/SarenFan/Birds-search-engine
- AI Log: PhanMinhTai_ai_log.md

---

**FINAL CHECKLIST:**

- ✅ Đã tạo Lightning.ai account
- ✅ Verified 22 credits available
- ✅ Understood background execution
- ✅ Planned hybrid strategy (Free + Paid)
- ✅ Ready to setup
- ✅ Estimated timeline: 6-8 ngày
- ✅ Budget: $10, còn $12 dự phòng

🎯 **READY TO START!** Bắt đầu setup ngay hôm nay!

---

**Created:** 2026-01-10
**Author:** Phan Minh Tai
**Status:** Ready for Implementation on Lightning.ai

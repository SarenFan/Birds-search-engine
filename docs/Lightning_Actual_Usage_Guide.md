# HƯỚNG DẪN CHẠY CRAWLER TRÊN LIGHTNING.AI

## 🎯 QUAN TRỌNG: Lightning.ai ĐÃ THAY ĐỔI ARCHITECTURE!

**Lightning.ai hiện tại (2026) không còn hỗ trợ CLI Jobs như trước.**

Thay vào đó, bạn phải dùng **Lightning Studios** qua Web UI để chạy background jobs.

---

## ✅ CÁCH CHẠY ĐÚNG: QUA LIGHTNING STUDIOS

### Bước 1: Tạo Lightning.ai Account

1. Vào https://lightning.ai
2. Sign up (verify email/phone)
3. Check credits: Bạn có **22 credits** sẵn

### Bước 2: Tạo Studio (Miễn phí!)

1. Click **"New Studio"**
2. Chọn: **CPU Studio** (4 cores - FREE)
3. Name: `seg301-crawler`
4. Wait ~30-60s để Studio khởi động

### Bước 3: Setup Environment trong Studio

**Mở Terminal trong Studio** và chạy:

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# 2. Clone repository
cd ~
git clone https://github.com/SarenFan/Birds-search-engine.git
cd Birds-search-engine

# 3. Install Python packages
pip install -r requirements.txt

# 4. Verify ChromeDriver
which chromedriver
# Should output: /usr/bin/chromedriver
```

### Bước 4: Enable Background Execution

**CỰC KỲ QUAN TRỌNG để crawler không dừng khi đóng tab!**

1. Click **Settings** (⚙️ icon) trong Studio
2. Tìm **"Background Execution"**
3. Toggle ON (bật)
4. Save settings

### Bước 5: Run Crawler Background

```bash
# Trong Studio terminal

# Option 1: Sequential Mode (An toàn, ổn định)
nohup python3 lightning_job_crawler.py --mode sequential > crawler.log 2>&1 &

# Option 2: Parallel Mode (Nhanh hơn, cần nhiều tài nguyên)
nohup python3 lightning_job_crawler.py --mode parallel --workers 2 > crawler.log 2>&1 &

# Check process đang chạy
ps aux | grep lightning_job_crawler

# Follow logs
tail -f crawler.log
```

### Bước 6: ĐÓNG BROWSER - Crawler vẫn chạy ngầm!

✅ Bây giờ bạn có thể:

- Đóng tab browser
- Tắt máy tính
- Đi ngủ
- Crawler vẫn chạy 24/7 trên Lightning.ai!

### Bước 7: Check Progress (Bất cứ lúc nào)

```bash
# Reopen Studio từ https://lightning.ai/studios
# Click vào "seg301-crawler"
# Open terminal

# Check crawler status
ps aux | grep lightning_job_crawler

# Check logs
tail -100 crawler.log

# Check progress từ checkpoints
cat /tmp/lightning_artifacts/checkpoints/*.json

# Example output:
# voz_checkpoint.json: {"docs_collected": 125430, "last_page": 567}
# tinhte_checkpoint.json: {"docs_collected": 89234, "last_page": 412}

# Check data size
du -sh /tmp/lightning_artifacts/data/*.jsonl
```

### Bước 8: Download Data khi xong

**Option 1: Via Studio UI (Dễ nhất)**

```bash
# Compress data
cd /tmp/lightning_artifacts/data
tar -czf seg301_data.tar.gz *.jsonl

# Download:
# - Click vào file seg301_data.tar.gz trong Studio file browser
# - Right click → Download
```

**Option 2: Via Lightning Drive (Cho data lớn)**

```bash
# Copy to shared Lightning Drive
cp /tmp/lightning_artifacts/data/*.jsonl ~/lightning_drive/

# Sau đó download từ Lightning.ai dashboard → Drive
```

---

## ⚙️ CONFIGURATION OPTIONS

### Sequential Mode (Khuyến nghị cho FREE Studio)

```bash
python3 lightning_job_crawler.py --mode sequential
```

**Ưu điểm:**

- ✅ Ổn định, ít lỗi
- ✅ Tiêu tốn ít RAM/CPU
- ✅ Phù hợp FREE 4-core Studio

**Nhược điểm:**

- ⚠️ Chậm hơn (chạy lần lượt từng crawler)
- ⏱️ Timeline: ~7-10 ngày

### Parallel Mode (Cho Paid 8+ core Studio)

```bash
python3 lightning_job_crawler.py --mode parallel --workers 3
```

**Ưu điểm:**

- ✅ Nhanh hơn (chạy đồng thời nhiều crawlers)
- ⏱️ Timeline: ~5-7 ngày với 8 cores

**Nhược điểm:**

- ⚠️ Cần nhiều CPU/RAM
- 💰 Tốn credits nếu dùng Paid Studio

---

## 💰 CHI PHÍ VỚI 22 CREDITS

### Option 1: FREE Studio Only ($0)

```
Machine: 4 CPU cores (FREE 24/7)
Mode: Sequential
Timeline: 7-10 ngày
Restart: Mỗi 4 giờ (checkpoint auto-resume)
Cost: $0
Result: 800K-1M docs
Remaining: 22 credits (giữ nguyên)
```

### Option 2: Hybrid (FREE + Paid 8-Core)

```
Week 1: FREE Studio
- Sequential mode
- 300-400K docs
- Cost: $0

Week 2: Upgrade to 8-Core Studio
- Parallel mode (3 workers)
- 600-700K docs
- Cost: ~$7-10 (72-100 giờ × $0.10/giờ)

TOTAL:
- Timeline: 6-8 ngày
- Result: 1M docs ✓
- Cost: $7-10
- Remaining: $12-15 credits dự phòng
```

---

## 🔄 HANDLE FREE STUDIO RESTART (Mỗi 4 giờ)

**FREE Studio tự động restart sau 4 giờ. Đây là cách handle:**

### Setup Auto-Resume Script

Tạo file `auto_resume.sh`:

```bash
#!/bin/bash
# Kiểm tra và restart crawler nếu bị dừng

if ! pgrep -f "lightning_job_crawler.py" > /dev/null; then
    echo "⚡ Restarting crawler..."
    cd ~/Birds-search-engine
    nohup python3 lightning_job_crawler.py --mode sequential > crawler.log 2>&1 &
    echo "✓ Crawler restarted at $(date)"
fi
```

**Make executable:**

```bash
chmod +x ~/auto_resume.sh
```

**Add to crontab (chạy mỗi 5 phút):**

```bash
crontab -e

# Add this line:
*/5 * * * * ~/auto_resume.sh >> ~/auto_resume.log 2>&1
```

Với setup này, crawler sẽ tự động resume trong vòng 5 phút sau mỗi lần Studio restart!

---

## 📊 MONITORING

### Check Progress Real-time

```bash
# Watch checkpoint progress (update mỗi 60s)
watch -n 60 'cat /tmp/lightning_artifacts/checkpoints/*.json'

# Watch data size growth
watch -n 300 'du -sh /tmp/lightning_artifacts/data/*.jsonl'

# Watch crawler logs
tail -f crawler.log | grep -E "Collected|completed|ERROR"
```

### Summary Command

```bash
# Get full summary
python3 -c "
import json
from pathlib import Path

checkpoint_dir = Path('/tmp/lightning_artifacts/checkpoints')
total = 0

for f in checkpoint_dir.glob('*_checkpoint.json'):
    with open(f) as fp:
        data = json.load(fp)
        docs = data.get('docs_collected', 0)
        total += docs
        print(f'{f.stem}: {docs:,} docs')

print(f'TOTAL: {total:,} docs')
"
```

---

## ⚠️ TROUBLESHOOTING

### Issue 1: Studio bị restart sau 4h

**Symptom:** Crawler dừng, Studio bị sleep

**Solution:**

```bash
# Manual restart
cd ~/Birds-search-engine
nohup python3 lightning_job_crawler.py --mode sequential > crawler.log 2>&1 &

# Hoặc dùng auto_resume.sh script (xem trên)
```

### Issue 2: ChromeDriver not found

**Symptom:** `selenium.common.exceptions.WebDriverException`

**Solution:**

```bash
# Reinstall ChromeDriver
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Verify
which chromedriver
chromedriver --version
```

### Issue 3: Out of disk space

**Symptom:** `No space left on device`

**Solution:**

```bash
# Check disk usage
df -h

# Compress old data
gzip /tmp/lightning_artifacts/data/*.jsonl

# Or download và xóa data cũ
# (xem section Download Data)
```

### Issue 4: Crawler bị stuck

**Symptom:** Logs không update, process vẫn running

**Solution:**

```bash
# Kill stuck process
pkill -9 -f lightning_job_crawler

# Restart
cd ~/Birds-search-engine
nohup python3 lightning_job_crawler.py --mode sequential > crawler.log 2>&1 &

# Checkpoint sẽ auto-resume từ nơi dừng
```

---

## 📥 DOWNLOAD DATA VỀ MÁY

### Method 1: Compress & Download (< 5GB)

```bash
# Trong Studio terminal
cd /tmp/lightning_artifacts/data

# Compress all data
tar -czf seg301_data.tar.gz *.jsonl

# Check size
ls -lh seg301_data.tar.gz

# Download:
# - Open Studio file browser
# - Navigate to /tmp/lightning_artifacts/data
# - Right-click seg301_data.tar.gz
# - Download
```

### Method 2: Lightning Drive (> 5GB)

```bash
# Copy to Lightning Drive
mkdir -p ~/lightning_drive/seg301_data
cp /tmp/lightning_artifacts/data/*.jsonl ~/lightning_drive/seg301_data/

# Download via dashboard:
# https://lightning.ai → Drive → seg301_data
```

### Method 3: Direct SCP (Fastest)

```bash
# Get Studio SSH info
# Settings → SSH Access → Copy SSH command

# On local machine:
scp -r <lightning-studio-ssh>:/tmp/lightning_artifacts/data/*.jsonl ./local/data/
```

---

## 🎯 RECOMMENDED WORKFLOW

**Workflow tối ưu cho 22 credits:**

### Phase 1: Test Setup (Day 1)

```bash
# FREE Studio
# Test với sequential mode
# Chạy 2-4 giờ để verify mọi thứ hoạt động
# Check checkpoints, logs, data output
```

### Phase 2: Production Crawl (Day 2-8)

```bash
# FREE Studio
# Sequential mode 24/7
# Setup auto_resume.sh
# Monitor mỗi ngày 1 lần
# Target: 800K-1M docs
# Cost: $0
```

### Phase 3: Optional Speedup (Nếu cần)

```bash
# Nếu sau 5 ngày chưa đủ 1M docs:
# Upgrade to 8-Core Studio
# Parallel mode (3 workers)
# Run thêm 2-3 ngày
# Cost: ~$5-7
```

### Phase 4: Download & Verify (Day 9)

```bash
# Compress data
# Download về máy
# Verify doc count & data quality
# Delete Studio nếu không dùng nữa
```

---

## ✅ CHECKLIST TRƯỚC KHI BẮT ĐẦU

- [ ] Tạo Lightning.ai account
- [ ] Verify 22 credits có sẵn
- [ ] Tạo FREE CPU Studio
- [ ] Clone GitHub repository
- [ ] Install dependencies (chromium, requirements.txt)
- [ ] **Enable Background Execution** (QUAN TRỌNG!)
- [ ] Test run crawler (5-10 phút)
- [ ] Setup auto_resume.sh (cho Free tier)
- [ ] Start production crawl
- [ ] Đóng browser - đi ngủ 😴

---

## 📞 SUPPORT & RESOURCES

**Lightning.ai:**

- Dashboard: https://lightning.ai
- Documentation: https://lightning.ai/docs
- Support: https://lightning.ai/discord

**Project:**

- GitHub: https://github.com/SarenFan/Birds-search-engine
- AI Log: PhanMinhTai_ai_log.md

**Script Files:**

- `lightning_job_crawler.py` - Main crawler manager
- `auto_resume.sh` - Auto-restart script
- `requirements.txt` - Python dependencies

---

**Created:** 2026-01-10
**Author:** Phan Minh Tai
**Status:** Ready for production deployment
**Estimated Timeline:** 6-10 days for 1M documents
**Estimated Cost:** $0-10 from 22 credits

🚀 **READY TO START!**

# CHIẾN LƯỢC CRAWL TRÊN CLOUD (Lightning.ai & Alternatives)

## 🎯 GIẢI PHÁP CLOUD CHO CRAWLING 24/7

### TL;DR

✅ **CÓ THỂ** chạy crawler trên Lightning.ai hoặc cloud platforms khác
✅ **KHUYẾN NGHỊ:** Google Colab Pro hoặc Kaggle (dễ dùng hơn, ổn định hơn)
⚠️ **LƯU Ý:** Free tiers có giới hạn thời gian, cần strategy phù hợp

---

## 📊 SO SÁNH CÁC NÊN TẢNG CLOUD

### 1. Google Colab (⭐ KHUYẾN NGHỊ TOP 1)

**Free Tier:**

- ✅ CPU: 2 cores
- ✅ RAM: 12GB
- ✅ Storage: 100GB
- ⚠️ Timeout: 12 giờ/session (idle), 24h nếu active
- ✅ GPU: T4 (không cần cho crawling)

**Colab Pro ($9.99/tháng):**

- ✅ Timeout: Lên đến 24h
- ✅ RAM: 25GB
- ✅ Background execution
- ✅ Priority access

**Ưu điểm:**

- 🟢 Dễ setup (Jupyter notebook)
- 🟢 Tích hợp Google Drive (lưu data tự động)
- 🟢 Không cần credit card (free tier)
- 🟢 Có thể chạy multiple notebooks

**Nhược điểm:**

- 🔴 12h timeout trên free tier
- 🔴 Bị disconnect nếu đóng browser (free)

### 2. Kaggle (⭐ KHUYẾN NGHỊ TOP 2)

**Specs:**

- ✅ CPU: 4 cores
- ✅ RAM: 16GB
- ✅ Storage: 5GB workspace + 20GB dataset storage
- ✅ Timeout: 9 giờ/session, 30 giờ/tuần
- ✅ GPU: P100 (miễn phí!)

**Ưu điểm:**

- 🟢 Hoàn toàn miễn phí
- 🟢 Không cần credit card
- 🟢 Lưu dataset public/private
- 🟢 30 giờ/tuần (3 sessions × 9h)
- 🟢 Download dataset dễ dàng

**Nhược điểm:**

- 🔴 9h/session (nhưng có thể restart)
- 🔴 Quota: 30h/tuần

### 3. Lightning.ai (Grid.ai)

**Free Tier:**

- ✅ CPU: 2-4 cores
- ✅ RAM: 8-16GB
- ✅ Storage: Varies
- ⚠️ Timeout: Depends on plan

**Ưu điểm:**

- 🟢 Designed for ML workflows
- 🟢 Good for long-running jobs

**Nhược điểm:**

- 🔴 Phức tạp hơn Colab/Kaggle
- 🔴 Free tier limited
- 🔴 Ít documentation cho web scraping use case

### 4. PythonAnywhere (💰 Paid)

**Free Tier:**

- ⚠️ Very limited (1 CPU, 512MB RAM)
- ❌ Không phù hợp cho crawling scale

**Paid ($5/tháng):**

- ✅ Always-on tasks
- ✅ Good for scheduled tasks
- ✅ No timeout

### 5. AWS/GCP/Azure (💰💰 Expensive)

**Chi phí:**

- 💰 ~$30-50/tháng cho t2.medium (AWS EC2)
- 💰💰 Billing theo giờ

**Ưu điểm:**

- 🟢 Full control
- 🟢 Không timeout
- 🟢 Scale dễ dàng

**Nhược điểm:**

- 🔴 Đắt
- 🔴 Setup phức tạp
- 🔴 Cần credit card

---

## 🚀 CHIẾN LƯỢC TỐI ƯU: HYBRID APPROACH

### Phương Án A: Google Colab + Session Rotation (FREE)

**Strategy:**

1. Chạy crawler trên Colab
2. Mỗi 10 giờ, save checkpoint + data to Google Drive
3. Restart session mới, resume từ checkpoint
4. Repeat cho đến khi đủ 1M docs

**Timeline:**

```
Session 1:  0h -  10h → Save checkpoint @ 150K docs
Session 2: 10h -  20h → Save checkpoint @ 300K docs
Session 3: 20h -  30h → Save checkpoint @ 450K docs
...
Session 7: 60h -  70h → Save checkpoint @ 1M docs ✓

Total: ~7 sessions × 10h = 70 giờ thực tế
Với setup/restart: ~80-90 giờ
Trong vòng: 4-5 ngày (chạy 24/7)
```

**Cost:** $0 (hoàn toàn miễn phí)

### Phương Án B: Kaggle Multi-Session (FREE)

**Strategy:**

1. Chạy 3 sessions/tuần (30h quota)
2. Mỗi session: 9 giờ, crawl ~120K docs
3. Upload dataset sau mỗi session
4. 4 tuần = 12 sessions = ~1.4M docs

**Timeline:**

```
Tuần 1: 3 sessions × 9h × 13K docs/h = 351K docs
Tuần 2: 3 sessions × 9h × 13K docs/h = 351K docs
Tuần 3: 3 sessions × 9h × 13K docs/h = 351K docs
Total: ~1M docs trong 3 tuần
```

**Cost:** $0

### Phương Án C: Colab Pro (KHUYẾN NGHỊ NHẤT)

**Strategy:**

1. Subscribe Colab Pro ($9.99/tháng)
2. Chạy background execution
3. 24h/session × 4 sessions = hoàn thành trong 4 ngày

**Timeline:**

```
Day 1: 24h × 15K docs/h = 360K docs
Day 2: 24h × 15K docs/h = 360K docs
Day 3: 24h × 15K docs/h = 360K docs
Total: ~1M docs trong 3-4 ngày
```

**Cost:** $9.99 cho 1 tháng (cancel sau khi xong)

### Phương Án D: Local Night Crawl (ĐÃ THIẾT KẾ)

**Strategy:**

- Chạy trên máy cá nhân 10h/đêm
- 3 tuần = 210h = 1M docs

**Cost:** $0 + Điện (~$5)

---

## 💻 HƯỚNG DẪN CHI TIẾT: GOOGLE COLAB

### Step 1: Setup Colab Notebook

**File: `colab_crawler.ipynb`**

```python
# Cell 1: Install dependencies
!pip install selenium undetected-chromedriver beautifulsoup4 jsonlines fake-useragent

# Cell 2: Install Chrome and ChromeDriver for Colab
!apt-get update
!apt install -y chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin

# Cell 3: Mount Google Drive (for saving data)
from google.colab import drive
drive.mount('/content/drive')

# Create data directory
!mkdir -p /content/drive/MyDrive/SEG301_Data
!mkdir -p /content/drive/MyDrive/SEG301_Checkpoints

# Cell 4: Clone your repository
!git clone https://github.com/SarenFan/Birds-search-engine.git
%cd Birds-search-engine

# Cell 5: Modify crawler for Colab
# Use ChromeDriver from system instead of downloading
import os
os.environ['CHROMEDRIVER_PATH'] = '/usr/bin/chromedriver'

# Cell 6: Run crawler with checkpoint
from src.crawler.voz_selenium_crawler import ImprovedVozCrawler
from src.crawler.selenium_utils import SeleniumCrawler

# Configure to save to Google Drive
crawler = ImprovedVozCrawler(
    output_file='/content/drive/MyDrive/SEG301_Data/voz_data.jsonl',
    checkpoint_file='/content/drive/MyDrive/SEG301_Checkpoints/voz_checkpoint.json',
    max_docs=400000,
    headless=True
)

selenium_driver = SeleniumCrawler(headless=True)

# Start crawling
crawler.crawl_forum(
    crawler=selenium_driver,
    forum_name="F17-OffTopic",
    forum_url="https://voz.vn/f/chuyen-tro-linh-tinh.17/",
    max_pages=1000
)

print("✓ Crawling completed!")

# Cell 7: Create zip for download (optional)
!cd /content/drive/MyDrive/SEG301_Data && \
 zip -r voz_data.zip voz_data.jsonl

print("✓ Data zipped! Download from Google Drive.")
```

### Step 2: Keep Colab Alive (Free Tier)

**Option A: Auto-clicker Extension**

```javascript
// Console script (press F12, paste này vào Console)
function KeepAlive() {
  document.querySelector("colab-connect-button").click();
}
setInterval(KeepAlive, 60000); // Click every 1 minute
```

**Option B: Python Keep-Alive**

```python
# Add to notebook cell
from IPython.display import Javascript
import time

def keep_alive():
    display(Javascript('''
        function ClickConnect(){
            console.log("Clicking connect");
            document.querySelector("colab-toolbar-button#connect").click()
        }
        setInterval(ClickConnect, 60000)
    '''))

keep_alive()
```

### Step 3: Multi-Process for Speed

```python
# Cell: Run 4 crawlers parallel
import multiprocessing as mp
from functools import partial

def run_crawler(source_config):
    name, url, target = source_config
    crawler = ImprovedVozCrawler(
        output_file=f'/content/drive/MyDrive/SEG301_Data/{name}_data.jsonl',
        checkpoint_file=f'/content/drive/MyDrive/SEG301_Checkpoints/{name}_checkpoint.json',
        max_docs=target,
        headless=True
    )
    # ... crawl logic

# Run parallel
configs = [
    ('voz', 'https://voz.vn/f/chuyen-tro-linh-tinh.17/', 400000),
    ('tinhte', 'https://tinhte.vn/forums/', 300000),
    ('spiderum', 'https://spiderum.com/khoa-hoc', 200000),
    ('otofun', 'https://otofun.net/forums/', 100000),
]

with mp.Pool(4) as pool:
    pool.map(run_crawler, configs)
```

### Step 4: Download Data về Máy

**Option A: Qua Google Drive UI**

1. Vào Google Drive
2. Download zip file

**Option B: Dùng rclone (Faster)**

```bash
# Trên máy local
# 1. Install rclone
sudo apt install rclone  # Linux
# hoặc brew install rclone  # Mac

# 2. Configure Google Drive
rclone config

# 3. Download
rclone copy gdrive:SEG301_Data /home/kource/Documents/SEG301/data/ --progress
```

**Option C: Dùng Google Drive Python API**

```python
# Trong Colab notebook
from google.colab import files

# Download trực tiếp
files.download('/content/drive/MyDrive/SEG301_Data/voz_data.jsonl')
```

---

## 🎯 KHUYẾN NGHỊ CỤ THỂ CHO BẠN

### Option 1: Colab Pro (1 tháng) - NHANH NHẤT ⚡

**Pros:**

- ✅ Xong trong 4-5 ngày
- ✅ Không cần lo máy tính
- ✅ Background execution
- ✅ Lưu trực tiếp Google Drive

**Cons:**

- 💰 $9.99 (tương đương 250K VND)

**Verdict:** ⭐⭐⭐⭐⭐ (5/5) - Best cho deadline gấp

### Option 2: Colab Free + Session Rotation - MIỄN PHÍ 💚

**Pros:**

- ✅ Hoàn toàn free
- ✅ Xong trong 1 tuần
- ✅ Tự động lưu Google Drive

**Cons:**

- 🔴 Phải restart mỗi 10-12h
- 🔴 Cần monitor

**Verdict:** ⭐⭐⭐⭐ (4/5) - Best cho sinh viên không budget

### Option 3: Kaggle - CÂN BẰNG ⚖️

**Pros:**

- ✅ Miễn phí
- ✅ 30h/tuần stable
- ✅ Dataset management tốt

**Cons:**

- 🔴 Chậm hơn (3 tuần)
- 🔴 Quota limit

**Verdict:** ⭐⭐⭐⭐ (4/5) - Tốt nếu không gấp

### Option 4: Local Night Crawl - ĐÃ THIẾT KẾ 🏠

**Pros:**

- ✅ Free
- ✅ Full control
- ✅ Không phụ thuộc cloud

**Cons:**

- 🔴 3 tuần mới xong
- 🔴 Máy phải chạy mỗi đêm
- 🔴 Ảnh hưởng công việc ban ngày (một chút)

**Verdict:** ⭐⭐⭐ (3/5) - OK nhưng chậm

---

## 📋 DECISION MATRIX

| Tiêu chí         | Colab Pro | Colab Free | Kaggle   | Local Night |
| ---------------- | --------- | ---------- | -------- | ----------- |
| Thời gian        | 4-5 ngày  | 7-10 ngày  | 21 ngày  | 21 ngày     |
| Chi phí          | $10       | $0         | $0       | ~$5 điện    |
| Effort           | Thấp      | Trung bình | Thấp     | Trung bình  |
| Reliability      | Cao       | Trung bình | Cao      | Cao         |
| Setup Complexity | Thấp      | Thấp       | Thấp     | Trung bình  |
| **TỔNG ĐIỂM**    | **9/10**  | **7/10**   | **7/10** | **6/10**    |

---

## 🎓 KHUYẾN NGHỊ CUỐI CÙNG

### Cho Milestone 1 (Deadline: Tuần 4)

**Hiện tại: Tuần 1 (10/01/2026)**
**Thời gian còn lại: 3 tuần**

#### ✅ PLAN A (RECOMMENDED): Colab Free + Night Local Hybrid

**Week 1 (10-16 Jan):**

- Day 1-2: Setup Colab notebook
- Day 3-7: Chạy Colab Free (2-3 sessions × 10h = 300K docs)

**Week 2 (17-23 Jan):**

- Chạy Colab tiếp (300K docs)
- Parallel: Start local night crawler (150K docs)
- **Total: 750K docs**

**Week 3 (24-30 Jan):**

- Finish với local night crawler (250K docs)
- **Total: 1M docs ✓**

**Cost:** $0
**Risk:** Thấp (có 2 sources)

#### ✅ PLAN B (SAFE): Subscribe Colab Pro

**Week 1 (10-16 Jan):**

- Subscribe Colab Pro ($10)
- Setup và test

**Week 2 (17-20 Jan):**

- Chạy 4 sessions × 24h = 1M docs
- Done! 🎉

**Week 3-4:**

- Data cleaning
- Relaxed timeline

**Cost:** $10
**Risk:** Rất thấp

#### ✅ PLAN C (SAFE BUT SLOW): Local Only

- Dùng strategy đã thiết kế
- 3 tuần night crawling
- Done đúng deadline

**Cost:** $0
**Risk:** Trung bình (phụ thuộc máy cá nhân)

---

## 🛠️ IMPLEMENTATION GUIDE

### Setup Colab Crawler (15 phút)

1. **Tạo Colab Notebook:**

   - Vào [colab.research.google.com](https://colab.research.google.com)
   - New Notebook
   - Copy code từ template trên

2. **Test với 100 docs:**

   - Chạy từng cell theo thứ tự
   - Verify data lưu vào Google Drive

3. **Production run:**

   - Set `max_docs=400000`
   - Run và để yên

4. **Monitor:**
   - Check Google Drive mỗi 2-3 giờ
   - Checkpoint file sẽ update progress

### Troubleshooting

**Issue 1: Colab timeout**

- Solution: Dùng keep-alive script
- Hoặc: Subscribe Pro

**Issue 2: IP blocked**

- Solution: Thêm delays dài hơn
- Colab có IP pool khác nhau mỗi session

**Issue 3: Out of RAM**

- Solution: Write data mỗi 1000 docs
- Clear cache thường xuyên

---

## 💡 PRO TIPS

1. **Colab Pro Worth It?**

   - Nếu budget có $10 → 100% đáng
   - Tiết kiệm 2 tuần + stress

2. **Multiple Google Accounts:**

   - Tạo 2-3 accounts
   - Mỗi account 1 crawler
   - 2x-3x tốc độ

3. **Kaggle + Colab Combo:**

   - Colab: Voz + TinhTe
   - Kaggle: Spiderum + Otofun
   - Parallel = Faster

4. **Backup Strategy:**

   - Google Drive: Primary
   - Dropbox/OneDrive: Secondary
   - Local download: Cuối cùng

5. **Monitor từ Phone:**
   - Google Drive app
   - Check checkpoint files
   - Peace of mind

---

## 📊 COST-BENEFIT ANALYSIS

### Scenario: Sinh viên có $10 budget

**Option A: Colab Pro 1 tháng**

```
Cost: $10
Time saved: 2 tuần
Stress reduction: 80%
ROI: Excellent (đáng từng đồng)
```

**Option B: Free tools only**

```
Cost: $0
Time: 3 tuần
Extra effort: Cao
ROI: Good (nếu không có tiền)
```

### Recommendation:

- Có $10: Chọn Colab Pro không cần suy nghĩ
- Không có: Hybrid Colab Free + Local

---

**FINAL ANSWER TO YOUR QUESTION:**

> "Tôi có thể chạy trên lightning.ai treo máy full-time để crawl rồi lưu và tải data về máy không?"

✅ **CÓ THỂ**, nhưng khuyến nghị dùng **Google Colab** (dễ hơn, tài liệu nhiều hơn)

✅ **BEST SOLUTION:** Colab Pro ($10) → Xong trong 4-5 ngày

✅ **FREE SOLUTION:** Colab Free + Session rotation → Xong trong 7-10 ngày

✅ **DATA STORAGE:** Lưu trực tiếp vào Google Drive, download về máy dễ dàng

🎯 **ACTION PLAN:** Setup Colab notebook ngay hôm nay, test với 100 docs, production run từ ngày mai!

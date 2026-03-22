# SEARCH ENGINE EVALUATION REPORT
## SEG301 - Social Listening Project

**Ngay danh gia:** 2026-02-22 07:02
**Phuong phap Recall:** Pooling-based (union cua tat ca retrieved docs lam ground truth)

---

## 1. Tong quan

| Metric | Gia tri |
|--------|---------|
| So queries test | 20 |
| K (top results) | 10 |
| Search methods | BM25, Vector, Hybrid |

---

## 2. Ket qua Precision@10 va Recall

| Search Method | Avg Precision@10 | Avg Recall |
|---------------|-------------------|------------|
| **BM25** (lexical) | 0.8250 | 0.4265 |
| **Vector** (semantic) | 0.9950 | 0.5608 |
| **Hybrid** (combined) | 0.9150 | 0.4918 |

---

## 3. Chi tiet tung query — Precision & Recall

| # | Query | BM25 P | BM25 R | Vec P | Vec R | Hyb P | Hyb R |
|---|-------|--------|--------|-------|-------|-------|-------|
| 1 | mua laptop gaming | 1.00 | 0.50 | 1.00 | 0.50 | 1.00 | 0.50 |
| 2 | kinh nghiệm mua nhà | 0.80 | 0.44 | 1.00 | 0.56 | 0.90 | 0.50 |
| 3 | xin visa nhật bản | 1.00 | 0.38 | 1.00 | 0.38 | 1.00 | 0.38 |
| 4 | công việc lương cao | 0.90 | 0.47 | 1.00 | 0.53 | 1.00 | 0.53 |
| 5 | điện thoại giá rẻ | 0.90 | 0.47 | 1.00 | 0.53 | 0.90 | 0.47 |
| 6 | học lập trình python | 1.00 | 0.50 | 1.00 | 0.50 | 1.00 | 0.50 |
| 7 | du lịch đà nẵng | 0.30 | 0.23 | 1.00 | 0.77 | 0.80 | 0.62 |
| 8 | thưởng tết công ty | 1.00 | 0.53 | 1.00 | 0.53 | 1.00 | 0.53 |
| 9 | mua xe máy honda | 1.00 | 0.53 | 1.00 | 0.53 | 1.00 | 0.53 |
| 10 | bệnh tiểu đường | 0.80 | 0.44 | 1.00 | 0.56 | 0.90 | 0.50 |
| 11 | game mobile hay | 1.00 | 0.45 | 1.00 | 0.45 | 1.00 | 0.45 |
| 12 | nuôi con nhỏ | 1.00 | 0.50 | 1.00 | 0.50 | 1.00 | 0.50 |
| 13 | đầu tư chứng khoán | 0.30 | 0.23 | 1.00 | 0.77 | 0.70 | 0.54 |
| 14 | cafe sài gòn | 0.90 | 0.47 | 1.00 | 0.53 | 1.00 | 0.53 |
| 15 | mua nhà hà nội | 0.90 | 0.47 | 1.00 | 0.53 | 0.90 | 0.47 |
| 16 | làm thêm sinh viên | 0.00 | 0.00 | 0.90 | 1.00 | 0.20 | 0.22 |
| 17 | review sách hay | 1.00 | 0.53 | 1.00 | 0.53 | 1.00 | 0.53 |
| 18 | giảm cân hiệu quả | 1.00 | 0.45 | 1.00 | 0.45 | 1.00 | 0.45 |
| 19 | mua đồ công nghệ | 1.00 | 0.50 | 1.00 | 0.50 | 1.00 | 0.50 |
| 20 | lập gia đình trẻ | 0.70 | 0.41 | 1.00 | 0.59 | 1.00 | 0.59 |

---

## 4. Phan tich tung query: Tai sao AI tot hon / te hon?

**Query 1: "mua laptop gaming"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'mua laptop gaming'. Hybrid ket hop uu diem cua ca hai.

**Query 2: "kinh nghiệm mua nhà"**

> Vector (100%) > BM25 (80%): Query 'kinh nghiệm mua nhà' can hieu ngu nghia — cac semantic variants nhu 'tư vấn mua nhà, kinh nghiệm bất động sản' duoc Vector tim tot hon nho embedding.

**Query 3: "xin visa nhật bản"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'xin visa nhật bản'. Hybrid ket hop uu diem cua ca hai.

**Query 4: "công việc lương cao"**

> BM25 (90%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'công việc lương cao'. Hybrid ket hop uu diem cua ca hai.

**Query 5: "điện thoại giá rẻ"**

> BM25 (90%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'điện thoại giá rẻ'. ca hai ket hop uu diem cua ca hai.

**Query 6: "học lập trình python"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'học lập trình python'. Hybrid ket hop uu diem cua ca hai.

**Query 7: "du lịch đà nẵng"**

> Vector (100%) > BM25 (30%): Query 'du lịch đà nẵng' can hieu ngu nghia — cac semantic variants nhu 'đi chơi miền trung, nghỉ dưỡng biển' duoc Vector tim tot hon nho embedding.

**Query 8: "thưởng tết công ty"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'thưởng tết công ty'. Hybrid ket hop uu diem cua ca hai.

**Query 9: "mua xe máy honda"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'mua xe máy honda'. Hybrid ket hop uu diem cua ca hai.

**Query 10: "bệnh tiểu đường"**

> Vector (100%) > BM25 (80%): Query 'bệnh tiểu đường' can hieu ngu nghia — cac semantic variants nhu 'bệnh đường, sức khỏe tim mạch' duoc Vector tim tot hon nho embedding.

**Query 11: "game mobile hay"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'game mobile hay'. Hybrid ket hop uu diem cua ca hai.

**Query 12: "nuôi con nhỏ"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'nuôi con nhỏ'. Hybrid ket hop uu diem cua ca hai.

**Query 13: "đầu tư chứng khoán"**

> Vector (100%) > BM25 (30%): Query 'đầu tư chứng khoán' can hieu ngu nghia — cac semantic variants nhu 'kiếm tiền từ đầu tư, tài chính cá nhân' duoc Vector tim tot hon nho embedding.

**Query 14: "cafe sài gòn"**

> BM25 (90%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'cafe sài gòn'. Hybrid ket hop uu diem cua ca hai.

**Query 15: "mua nhà hà nội"**

> BM25 (90%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'mua nhà hà nội'. ca hai ket hop uu diem cua ca hai.

**Query 16: "làm thêm sinh viên"**

> Vector (90%) > BM25 (0%): Query 'làm thêm sinh viên' can hieu ngu nghia — cac semantic variants nhu 'kiếm tiền khi còn đi học, công việc bán thời gian' duoc Vector tim tot hon nho embedding.

**Query 17: "review sách hay"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'review sách hay'. Hybrid ket hop uu diem cua ca hai.

**Query 18: "giảm cân hiệu quả"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'giảm cân hiệu quả'. Hybrid ket hop uu diem cua ca hai.

**Query 19: "mua đồ công nghệ"**

> BM25 (100%) ~ Vector (100%): Hai phuong phap cho ket qua tuong duong voi query 'mua đồ công nghệ'. Hybrid ket hop uu diem cua ca hai.

**Query 20: "lập gia đình trẻ"**

> Vector (100%) > BM25 (70%): Query 'lập gia đình trẻ' can hieu ngu nghia — cac semantic variants nhu 'lấy vợ sớm, cuộc sống hôn nhân' duoc Vector tim tot hon nho embedding.

---

## 5. Phan tich tong hop

### 5.1 Khi nao BM25 tot hon?
- Khi query chua **tu khoa chinh xac** co trong documents
- Vi du: "mua laptop gaming" -> tim duoc docs chua "laptop", "gaming"
- BM25 dua vao **term frequency** va **document frequency**
- Uu diem: nhanh (~10-50ms), khong can model AI

### 5.2 Khi nao Vector Search tot hon?
- Khi query co **y nghia tuong duong** nhung khac tu
- Vi du: "may tinh choi game" co the tim duoc docs ve "laptop gaming"
- Vector Search dua vao **semantic embeddings** (paraphrase-multilingual-MiniLM-L12-v2)
- Uu diem: hieu ngu nghia, tim duoc synonyms va paraphrases

### 5.3 Hybrid Search
- Ket hop ca hai: Score = alpha x BM25_norm + (1-alpha) x Vector_norm
- alpha = 0.5 (equal weight) cho ket qua can bang
- Thuong cho **Recall cao nhat** vi gop union cua ca hai phuong phap

---

## 6. Ket luan

**Vector Search** vuot troi (P=0.9950) nho kha nang hieu ngu nghia.

**Khuyen nghi:**
- Su dung Hybrid Search voi alpha=0.5 cho ket qua can bang
- Tang alpha (>0.5) cho keyword queries, giam alpha (<0.5) cho semantic queries
- Vector Search huu ich nhat khi user dung ngon ngu tu nhien thay vi keywords

---

*Report generated by SEG301 Evaluation System*

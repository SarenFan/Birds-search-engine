# AI Chat Archive Log

Folder này chứa lịch sử các cuộc trò chuyện với Claude Code đã được archive khi conversation quá dài.

## 📁 Structure

Mỗi file được đặt tên theo format:
```
YYYYMMDD_HHMMSS_session_name.md
```

Ví dụ:
- `20260211_143022_seg301_indexing_work.md`
- `20260211_183045_claude_md_creation.md`

## 🔧 Cách sử dụng

### 1. Archive chat thủ công

```bash
# Copy chat content vào file tạm
cat > /tmp/chat_export.txt << 'EOF'
[Paste your chat content here]
EOF

# Archive
python scripts/archive_chat.py \
    --input /tmp/chat_export.txt \
    --title "Session Title" \
    --name "session_name" \
    --tokens 150000
```

### 2. Xem danh sách archives

```bash
python scripts/archive_chat.py --list
```

### 3. Xem thống kê

```bash
python scripts/archive_chat.py --stats
```

### 4. Tự động archive (khi approaching compact)

```bash
# Trigger manually khi thấy token usage cao
./scripts/auto_archive_hook.sh 150000
```

## 📊 Metadata

Mỗi archive file chứa:
- **Title**: Tiêu đề session
- **Archived time**: Thời gian lưu trữ
- **Tokens used**: Số token đã dùng (nếu có)
- **Model**: Model đã sử dụng (nếu có)
- **Content**: Toàn bộ nội dung chat

## 🎯 Khi nào nên archive?

- Token usage > 150,000 (approaching 200K limit)
- Conversation quá dài, khó theo dõi
- Trước khi chuyển sang task/topic mới
- Cuối ngày làm việc

## 💡 Tips

1. **Đặt tên session có ý nghĩa**: Dùng `--name` để dễ tìm lại sau này
2. **Ghi metadata đầy đủ**: Thêm `--tokens` và `--model` để tracking
3. **Archive thường xuyên**: Đừng đợi đến khi bị compact mới archive
4. **Review định kỳ**: Xem lại archives để học hỏi và tối ưu workflow

## 🗑️ Cleanup

Archives cũ có thể được di chuyển vào subfolder hoặc compress:

```bash
# Tạo archive theo tháng
mkdir -p archives/2026-02
mv 202602*.md archives/2026-02/

# Compress old archives
tar -czf archives/2026-02.tar.gz archives/2026-02/
rm -rf archives/2026-02/
```

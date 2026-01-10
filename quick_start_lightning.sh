#!/bin/bash
# Quick Start Script cho Lightning.ai Crawler
# Author: Phan Minh Tai
# Date: 2026-01-10

echo "=================================================="
echo "🚀 LIGHTNING.AI CRAWLER - QUICK START"
echo "=================================================="
echo ""

echo "📋 Checklist:"
echo "  1. Đã tạo Lightning.ai account? (https://lightning.ai)"
echo "  2. Đã verify 22 credits?"
echo "  3. Đã tạo FREE CPU Studio?"
echo ""

read -p "Nhấn Enter để tiếp tục hoặc Ctrl+C để thoát..."

echo ""
echo "🔧 Installing system dependencies..."
echo "Running: sudo apt-get update && sudo apt-get install -y chromium-browser chromium-chromedriver"
echo ""
echo "⚠️  QUAN TRỌNG: Script này chỉ chạy TRONG Lightning Studio!"
echo "⚠️  Đừng chạy trên máy local!"
echo ""

read -p "Bạn đang trong Lightning Studio? (y/n): " in_studio

if [ "$in_studio" != "y" ]; then
    echo ""
    echo "❌ Script này chỉ chạy trong Lightning Studio!"
    echo ""
    echo "📖 Hướng dẫn:"
    echo "  1. Vào https://lightning.ai"
    echo "  2. Tạo New Studio (CPU - FREE)"
    echo "  3. Clone repo: git clone https://github.com/SarenFan/Birds-search-engine.git"
    echo "  4. cd Birds-search-engine"
    echo "  5. Run script này: bash quick_start_lightning.sh"
    echo ""
    exit 1
fi

echo ""
echo "✅ Bắt đầu setup..."
echo ""

# Update packages
echo "📦 Updating packages..."
sudo apt-get update -qq

# Install Chrome & ChromeDriver
echo "🌐 Installing Chromium & ChromeDriver..."
sudo apt-get install -y chromium-browser chromium-chromedriver > /dev/null 2>&1

# Verify ChromeDriver
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver installed: $(chromedriver --version | head -1)"
else
    echo "❌ ChromeDriver installation failed!"
    exit 1
fi

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup completed!"
echo ""

# Enable background execution reminder
echo "⚠️  QUAN TRỌNG: Enable Background Execution!"
echo ""
echo "   1. Click Settings (⚙️) trong Studio"
echo "   2. Toggle ON: Background Execution"
echo "   3. Save"
echo ""

read -p "Đã enable Background Execution? (y/n): " bg_enabled

if [ "$bg_enabled" != "y" ]; then
    echo ""
    echo "⚠️  Hãy enable Background Execution trước khi chạy crawler!"
    echo "   Nếu không, crawler sẽ dừng khi đóng browser!"
    echo ""
    exit 1
fi

echo ""
echo "🎯 Chọn chế độ chạy:"
echo "  1. Sequential (An toàn, phù hợp FREE Studio)"
echo "  2. Parallel (Nhanh hơn, cần 8+ cores)"
echo ""

read -p "Chọn (1/2): " mode_choice

if [ "$mode_choice" == "1" ]; then
    MODE="sequential"
    WORKERS=""
else
    MODE="parallel"
    read -p "Số workers (2-4): " worker_count
    WORKERS="--workers $worker_count"
fi

echo ""
echo "🚀 Starting crawler in background..."
echo "   Mode: $MODE"
echo "   Command: nohup python3 lightning_job_crawler.py --mode $MODE $WORKERS > crawler.log 2>&1 &"
echo ""

nohup python3 lightning_job_crawler.py --mode $MODE $WORKERS > crawler.log 2>&1 &

sleep 2

# Check if process started
if pgrep -f "lightning_job_crawler.py" > /dev/null; then
    PID=$(pgrep -f "lightning_job_crawler.py")
    echo "✅ Crawler started successfully!"
    echo "   Process ID: $PID"
    echo ""
    echo "📊 Monitoring commands:"
    echo "   tail -f crawler.log                    # Follow logs"
    echo "   cat /tmp/lightning_artifacts/checkpoints/*.json  # Check progress"
    echo "   ps aux | grep lightning_job_crawler    # Check process"
    echo ""
    echo "🎉 Bây giờ bạn có thể:"
    echo "   ✓ Đóng tab browser"
    echo "   ✓ Tắt máy tính"
    echo "   ✓ Đi ngủ"
    echo "   → Crawler sẽ chạy 24/7 trên Lightning.ai!"
    echo ""
    echo "📥 Check progress sau: reopen Studio → tail -f crawler.log"
    echo ""
else
    echo "❌ Failed to start crawler!"
    echo "Check logs: cat crawler.log"
    exit 1
fi

echo "=================================================="
echo "🎯 SETUP COMPLETED!"
echo "=================================================="

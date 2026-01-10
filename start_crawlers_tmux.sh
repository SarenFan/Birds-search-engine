#!/bin/bash
#
# Start 3 Parallel Crawlers with TMUX on Lightning.ai
# Mỗi crawler chạy trong 1 tmux window riêng
#

STUDIO_ID="s_01kem22xtq9zcsd56hsvk42nfv"
SESSION_NAME="crawler-100k"

echo "🌩️  STARTING CRAWLERS ON LIGHTNING.AI WITH TMUX"
echo "================================================"

# SSH and setup tmux
ssh -t ${STUDIO_ID}@ssh.lightning.ai << 'ENDSSH'

cd Birds-search-engine

# Kill old tmux session if exists
tmux kill-session -t crawler-100k 2>/dev/null

# Start Xvfb if not running
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "Starting Xvfb..."
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    sleep 2
fi

export DISPLAY=:99

# Create directories
mkdir -p /tmp/lightning_artifacts/test_data
mkdir -p /tmp/lightning_artifacts/test_checkpoints
mkdir -p /tmp/crawler_logs

echo ""
echo "🚀 Creating tmux session: crawler-100k"
echo "========================================="

# Create new tmux session (detached)
tmux new-session -d -s crawler-100k -n VOZ

# Window 1: VOZ Crawler
tmux send-keys -t crawler-100k:VOZ "cd ~/Birds-search-engine" C-m
tmux send-keys -t crawler-100k:VOZ "export DISPLAY=:99" C-m
tmux send-keys -t crawler-100k:VOZ "source venv/bin/activate" C-m
tmux send-keys -t crawler-100k:VOZ "echo '🔵 Starting VOZ Crawler...'" C-m
tmux send-keys -t crawler-100k:VOZ "python3 -c \"
from pathlib import Path
from src.crawler.voz_selenium_crawler import ImprovedVozCrawler
from src.crawler.selenium_utils import SeleniumCrawler

print('[VOZ] Initializing...')
data_dir = Path('/tmp/lightning_artifacts/test_data')
checkpoint_dir = Path('/tmp/lightning_artifacts/test_checkpoints')

crawler = ImprovedVozCrawler(
    output_file=str(data_dir / 'test_voz.jsonl'),
    checkpoint_file=str(checkpoint_dir / 'test_voz_checkpoint.json'),
    max_docs=40000,
    headless=True
)

driver = SeleniumCrawler(headless=True, driver_path=f'{Path.home()}/.local/bin/chromedriver')

try:
    print('[VOZ] Starting crawl...')
    crawler.crawl_forum(
        crawler=driver,
        forum_name='F17-OffTopic',
        forum_url='https://voz.vn/f/chuyen-tro-linh-tinh.17/',
        max_pages=200
    )
    print(f'[VOZ] ✅ COMPLETED! Docs: {crawler.docs_collected:,}')
finally:
    if driver and driver.driver:
        driver.driver.quit()
\" 2>&1 | tee /tmp/crawler_logs/voz.log" C-m

sleep 3

# Window 2: TinhTe Crawler
tmux new-window -t crawler-100k -n TinhTe
tmux send-keys -t crawler-100k:TinhTe "cd ~/Birds-search-engine" C-m
tmux send-keys -t crawler-100k:TinhTe "export DISPLAY=:99" C-m
tmux send-keys -t crawler-100k:TinhTe "source venv/bin/activate" C-m
tmux send-keys -t crawler-100k:TinhTe "echo '🟢 Starting TinhTe Crawler...'" C-m
tmux send-keys -t crawler-100k:TinhTe "python3 -c \"
from pathlib import Path
from src.crawler.tinhte_selenium_crawler import ImprovedTinhTeCrawler
from src.crawler.selenium_utils import SeleniumCrawler

print('[TinhTe] Initializing...')
data_dir = Path('/tmp/lightning_artifacts/test_data')
checkpoint_dir = Path('/tmp/lightning_artifacts/test_checkpoints')

crawler = ImprovedTinhTeCrawler(
    output_file=str(data_dir / 'test_tinhte.jsonl'),
    checkpoint_file=str(checkpoint_dir / 'test_tinhte_checkpoint.json'),
    max_docs=30000,
    headless=True
)

driver = SeleniumCrawler(headless=True, driver_path=f'{Path.home()}/.local/bin/chromedriver')

try:
    print('[TinhTe] Starting crawl...')
    crawler.crawl_forum(
        crawler=driver,
        forum_url='https://tinhte.vn/forums/',
        max_pages=150
    )
    print(f'[TinhTe] ✅ COMPLETED! Docs: {crawler.docs_collected:,}')
finally:
    if driver and driver.driver:
        driver.driver.quit()
\" 2>&1 | tee /tmp/crawler_logs/tinhte.log" C-m

sleep 3

# Window 3: Spiderum Crawler
tmux new-window -t crawler-100k -n Spiderum
tmux send-keys -t crawler-100k:Spiderum "cd ~/Birds-search-engine" C-m
tmux send-keys -t crawler-100k:Spiderum "export DISPLAY=:99" C-m
tmux send-keys -t crawler-100k:Spiderum "source venv/bin/activate" C-m
tmux send-keys -t crawler-100k:Spiderum "echo '🟣 Starting Spiderum Crawler...'" C-m
tmux send-keys -t crawler-100k:Spiderum "python3 -c \"
from pathlib import Path
from src.crawler.spiderum_selenium_crawler import ImprovedSpiderumCrawler
from src.crawler.selenium_utils import SeleniumCrawler

print('[Spiderum] Initializing...')
data_dir = Path('/tmp/lightning_artifacts/test_data')
checkpoint_dir = Path('/tmp/lightning_artifacts/test_checkpoints')

crawler = ImprovedSpiderumCrawler(
    output_file=str(data_dir / 'test_spiderum.jsonl'),
    checkpoint_file=str(checkpoint_dir / 'test_spiderum_checkpoint.json'),
    max_docs=20000,
    headless=True
)

driver = SeleniumCrawler(headless=True, driver_path=f'{Path.home()}/.local/bin/chromedriver')

try:
    print('[Spiderum] Starting crawl...')
    crawler.crawl_category(
        crawler=driver,
        category_url='https://spiderum.com/khoa-hoc'
    )
    print(f'[Spiderum] ✅ COMPLETED! Docs: {crawler.docs_collected:,}')
finally:
    if driver and driver.driver:
        driver.driver.quit()
\" 2>&1 | tee /tmp/crawler_logs/spiderum.log" C-m

sleep 2

# Window 4: Monitor
tmux new-window -t crawler-100k -n Monitor
tmux send-keys -t crawler-100k:Monitor "watch -n 10 'echo \"📊 CRAWLER STATUS\" && echo \"==================\" && echo \"\" && echo \"🔍 Processes:\" && ps aux | grep -E \"(voz|tinhte|spiderum)\" | grep python | grep -v grep && echo \"\" && echo \"📄 Data Files:\" && ls -lh /tmp/lightning_artifacts/test_data/*.jsonl 2>/dev/null && echo \"\" && echo \"📈 Document Count:\" && for f in /tmp/lightning_artifacts/test_data/*.jsonl; do [ -f \"\$f\" ] && echo \"  \$(basename \$f): \$(wc -l < \$f) docs\"; done'" C-m

echo ""
echo "✅ TMUX SESSION CREATED!"
echo "========================"
echo ""
echo "📊 Tmux Windows:"
echo "  0: VOZ      - VOZ crawler (target: 40K docs)"
echo "  1: TinhTe   - TinhTe crawler (target: 30K docs)"
echo "  2: Spiderum - Spiderum crawler (target: 20K docs)"
echo "  3: Monitor  - Real-time monitoring"
echo ""
echo "🔧 Control Commands:"
echo "  # Attach to tmux session:"
echo "  tmux attach -t crawler-100k"
echo ""
echo "  # Switch between windows:"
echo "  Ctrl+B then 0/1/2/3"
echo ""
echo "  # Detach (keep running):"
echo "  Ctrl+B then D"
echo ""
echo "  # List sessions:"
echo "  tmux ls"
echo ""
echo "  # Kill session:"
echo "  tmux kill-session -t crawler-100k"
echo ""
echo "📋 Log Files:"
echo "  /tmp/crawler_logs/voz.log"
echo "  /tmp/crawler_logs/tinhte.log"
echo "  /tmp/crawler_logs/spiderum.log"
echo ""
echo "Press Enter to detach and let crawlers run in background..."
read

# Detach from tmux
tmux detach -s crawler-100k

echo ""
echo "🎉 Crawlers are now running in background!"
echo "   SSH connection will close but crawlers continue."
echo ""
echo "💡 To check status later:"
echo "   ssh ${STUDIO_ID}@ssh.lightning.ai"
echo "   tmux attach -t crawler-100k"

ENDSSH

echo ""
echo "✅ Setup complete! Crawlers running on Lightning.ai"

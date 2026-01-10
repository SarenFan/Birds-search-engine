#!/bin/bash
#
# Monitor Crawlers on Lightning.ai via tmux
#

STUDIO_ID="s_01kem22xtq9zcsd56hsvk42nfv"

echo "📊 CHECKING CRAWLER STATUS ON LIGHTNING.AI"
echo "==========================================="
echo ""

ssh ${STUDIO_ID}@ssh.lightning.ai << 'ENDSSH'

echo "🔍 TMUX Sessions:"
echo "=================="
tmux ls 2>/dev/null || echo "No tmux sessions"

echo ""
echo "📊 Crawler Processes:"
echo "===================="
ps aux | grep -E "(voz|tinhte|spiderum)" | grep python | grep -v grep | wc -l | xargs echo "Active crawlers:"
ps aux | grep -E "(voz|tinhte|spiderum)" | grep python | grep -v grep | awk '{print $2, $11, $12, $13}' | head -10

echo ""
echo "📄 Data Files:"
ls -lh /tmp/lightning_artifacts/test_data/*.jsonl 2>/dev/null || echo "  No data files yet"

echo ""
echo "📈 Documents Collected:"
for f in /tmp/lightning_artifacts/test_data/*.jsonl 2>/dev/null; do
    if [ -f "$f" ]; then
        count=$(wc -l < "$f")
        echo "  $(basename $f): $count documents"
    fi
done

echo ""
echo "📋 Recent Logs:"
echo "  VOZ:      tail -20 /tmp/crawler_logs/voz.log"
echo "  TinhTe:   tail -20 /tmp/crawler_logs/tinhte.log"
echo "  Spiderum: tail -20 /tmp/crawler_logs/spiderum.log"

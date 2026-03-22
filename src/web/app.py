"""
Web UI for Search Engine - Full Featured
Flask-based web interface with BM25, Vector, and Hybrid search
Features: Search, Filter (top_k), Pagination, Mode Selection
"""

import os
import sys
import time
import json
import signal
import gc
from flask import Flask, render_template, request, jsonify

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ranking.bm25 import BM25
from indexer.spimi import InvertedIndex

app = Flask(__name__, template_folder='templates', static_folder='static')

# Global search engines
bm25 = None
index = None
hybrid_search = None
documents = {}  # For content preview


def init_search_engines():
    """Initialize search engines"""
    global bm25, index, hybrid_search, documents

    print("Initializing search engines...")

    # Load documents for content preview
    # Try multiple possible data paths
    data_paths = [
        'data/data_clean/voz_cleaned.jsonl',
        'data/voz_data.jsonl',
        'data/data_raw/lightning_ai/data/voz_1m.jsonl',
    ]
    loaded = False
    for data_path in data_paths:
        if os.path.exists(data_path):
            try:
                print(f"Loading documents from {data_path}...")
                with open(data_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        doc = json.loads(line)
                        documents[doc.get('doc_id', '')] = {
                            'content': doc.get('content', '')[:300],
                            'author': doc.get('author', 'Unknown'),
                            'timestamp': doc.get('timestamp', '')
                        }
                print(f"Loaded {len(documents):,} document previews")
                loaded = True
                break
            except Exception as e:
                print(f"Failed to load {data_path}: {e}")
    if not loaded:
        print("Warning: No document data found for content preview")

    # BM25 (always available)
    try:
        index = InvertedIndex.load('data/index/inverted_index.pkl')
        bm25 = BM25(index)
        print("BM25 search ready")
    except Exception as e:
        print(f"BM25 failed: {e}")

    # Hybrid (optional, needs vector index)
    try:
        from search.hybrid_search import HybridSearch
        hybrid_search = HybridSearch(existing_index=index, existing_bm25=bm25)
        print("Hybrid search ready")
    except Exception as e:
        print(f"Hybrid search not available: {e}")


@app.route('/')
def home():
    """Main search page"""
    return render_template('search.html')


@app.route('/search', methods=['POST'])
def search():
    """Search API endpoint with filtering and pagination"""
    data = request.get_json()
    query = data.get('query', '')
    mode = data.get('mode', 'bm25')
    top_k = int(data.get('top_k', 10))
    alpha = float(data.get('alpha', 0.3))

    if not query:
        return jsonify({'error': 'Empty query', 'results': []})

    start_time = time.time()
    results = []
    total_matching = 0

    try:
        if mode == 'bm25' and bm25:
            search_results, total_matching = bm25.search(query, top_k)
            results = [{
                'doc_id': doc_id,
                'score': round(score, 4),
                'title': info.get('title', ''),
                'url': info.get('url', ''),
                'content_preview': documents.get(doc_id, {}).get('content', '')[:200],
                'author': documents.get(doc_id, {}).get('author', 'Unknown'),
            } for doc_id, score, info in search_results]

        elif mode in ['vector', 'hybrid'] and hybrid_search:
            search_results, total_matching = hybrid_search.search(query, mode=mode, top_k=top_k, alpha=alpha)
            results = [{
                'doc_id': r.doc_id,
                'score': round(r.hybrid_score, 4),
                'bm25_score': round(r.bm25_score, 4),
                'vector_score': round(r.vector_score, 4),
                'title': r.title,
                'url': r.url,
                'content_preview': documents.get(r.doc_id, {}).get('content', '')[:200],
                'author': documents.get(r.doc_id, {}).get('author', 'Unknown'),
            } for r in search_results]

        elif bm25:
            search_results, total_matching = bm25.search(query, top_k)
            results = [{
                'doc_id': doc_id,
                'score': round(score, 4),
                'title': info.get('title', ''),
                'url': info.get('url', ''),
                'content_preview': documents.get(doc_id, {}).get('content', '')[:200],
                'author': documents.get(doc_id, {}).get('author', 'Unknown'),
            } for doc_id, score, info in search_results]

    except Exception as e:
        return jsonify({'error': str(e), 'results': []})

    elapsed = (time.time() - start_time) * 1000

    return jsonify({
        'query': query,
        'mode': mode,
        'total_matching': total_matching,
        'total_count': len(results),
        'time_ms': round(elapsed, 2),
        'results': results
    })


@app.route('/stats')
def stats():
    """Get search engine stats"""
    stats = {
        'bm25_available': bm25 is not None,
        'hybrid_available': hybrid_search is not None,
        'vector_available': hybrid_search.has_vector if hybrid_search else False,
        'total_docs': index.total_docs if index else 0,
        'vocabulary_size': index.total_terms if index else 0,
    }
    
    return jsonify(stats)


# Create templates directory and files
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')


def create_templates():
    """Create HTML templates with Filter and Pagination"""
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # Main search template with Filter and Pagination
    search_html = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voz Search Engine</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: #888;
            font-size: 1rem;
        }
        
        .search-box {
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .search-input-container {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        #searchInput {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1.1rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        #searchInput:focus {
            border-color: #00d9ff;
        }
        
        #searchBtn {
            padding: 14px 28px;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            border: none;
            border-radius: 12px;
            color: #000;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        #searchBtn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,217,255,0.3);
        }
        
        .controls-row {
            display: flex;
            gap: 20px;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .mode-selector {
            display: flex;
            gap: 10px;
        }
        
        .mode-btn {
            padding: 8px 20px;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 25px;
            background: transparent;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
        }
        
        .mode-btn:hover, .mode-btn.active {
            border-color: #00d9ff;
            background: rgba(0,217,255,0.2);
        }
        
        .filter-control {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #aaa;
            font-size: 0.9rem;
        }
        
        .filter-control input[type="range"] {
            width: 100px;
            accent-color: #00d9ff;
        }

        #alphaControl {
            display: none;
        }

        #alphaControl.visible {
            display: flex;
        }
        
        .results-container {
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .results-count {
            color: #00d9ff;
        }
        
        .results-time {
            color: #888;
            font-size: 0.9rem;
        }
        
        .result-item {
            padding: 18px;
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            margin-bottom: 12px;
            transition: transform 0.2s, background 0.2s;
        }
        
        .result-item:hover {
            transform: translateX(5px);
            background: rgba(0,0,0,0.35);
        }
        
        .result-title {
            font-size: 1.1rem;
            color: #00ff88;
            margin-bottom: 8px;
        }
        
        .result-title a {
            color: inherit;
            text-decoration: none;
        }
        
        .result-title a:hover {
            text-decoration: underline;
        }
        
        .result-preview {
            color: #bbb;
            font-size: 0.9rem;
            margin-bottom: 10px;
            line-height: 1.5;
        }
        
        .result-meta {
            display: flex;
            gap: 15px;
            font-size: 0.8rem;
            color: #888;
            flex-wrap: wrap;
        }
        
        .result-score {
            background: rgba(0,217,255,0.2);
            padding: 3px 10px;
            border-radius: 10px;
            color: #00d9ff;
        }
        
        .result-author {
            color: #ff9f43;
        }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .page-btn {
            padding: 8px 14px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: transparent;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .page-btn:hover, .page-btn.active {
            border-color: #00d9ff;
            background: rgba(0,217,255,0.2);
        }
        
        .page-btn:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #00d9ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        
        .stats-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.9);
            padding: 10px;
            text-align: center;
            font-size: 0.85rem;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Voz Search</h1>
            <p class="subtitle">SEG301 Social Listening - BM25 + Vector + Hybrid Search</p>
        </header>
        
        <div class="search-box">
            <div class="search-input-container">
                <input type="text" id="searchInput" placeholder="Nhập từ khóa tìm kiếm..." autofocus>
                <button id="searchBtn">Tìm kiếm</button>
            </div>
            
            <div class="controls-row">
                <div class="mode-selector">
                    <button class="mode-btn active" data-mode="bm25">📊 BM25</button>
                    <button class="mode-btn" data-mode="vector">🧠 Vector</button>
                    <button class="mode-btn" data-mode="hybrid">⚡ Hybrid</button>
                </div>
                
                <div class="filter-control">
                    <label>Số kết quả:</label>
                    <input type="number" id="topKInput" min="1" max="500" value="10"
                           style="width:70px; padding:6px 10px; border:2px solid rgba(255,255,255,0.2);
                           border-radius:8px; background:rgba(0,0,0,0.3); color:#00d9ff;
                           font-size:0.95rem; text-align:center; outline:none;">
                </div>

                <div class="filter-control" id="alphaControl">
                    <label>Alpha (BM25 ↔ Vector):</label>
                    <input type="range" id="alphaSlider" min="0" max="1" value="0.3" step="0.1">
                    <span id="alphaValue">0.3</span>
                </div>
            </div>
        </div>
        
        <div class="results-container">
            <div class="results-header">
                <span class="results-count" id="resultsCount">Sẵn sàng tìm kiếm</span>
                <span class="results-time" id="resultsTime"></span>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top:15px">Đang tìm kiếm...</p>
            </div>
            
            <div id="resultsList"></div>
            
            <div class="pagination" id="pagination" style="display:none;"></div>
        </div>
    </div>
    
    <div class="stats-bar" id="statsBar">Loading stats...</div>
    
    <script>
        let currentMode = 'bm25';
        let currentPage = 1;
        let cachedResults = [];
        let cachedMeta = {};
        const PER_PAGE = 10;

        const alphaControl = document.getElementById('alphaControl');
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMode = btn.dataset.mode;
                alphaControl.classList.toggle('visible', currentMode === 'hybrid');
            });
        });

        const alphaSlider = document.getElementById('alphaSlider');
        const alphaValueEl = document.getElementById('alphaValue');
        alphaSlider.addEventListener('input', () => {
            alphaValueEl.textContent = alphaSlider.value;
        });

        const topKInput = document.getElementById('topKInput');

        async function doSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;

            const topK = Math.max(1, parseInt(topKInput.value) || 10);
            topKInput.value = topK;

            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultsList').textContent = '';
            document.getElementById('pagination').style.display = 'none';

            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        query: query,
                        mode: currentMode,
                        top_k: topK,
                        alpha: parseFloat(alphaSlider.value)
                    })
                });

                const data = await response.json();
                cachedResults = data.results || [];
                cachedMeta = {
                    query: data.query,
                    mode: data.mode,
                    total_matching: data.total_matching || 0,
                    total_count: data.total_count || cachedResults.length,
                    time_ms: data.time_ms
                };

                currentPage = 1;
                renderPage(currentPage);
            } catch (error) {
                document.getElementById('resultsList').textContent = 'Lỗi: ' + error.message;
            }

            document.getElementById('loading').style.display = 'none';
        }

        function renderPage(page) {
            currentPage = page;
            const totalPages = Math.ceil(cachedResults.length / PER_PAGE) || 1;
            const startIdx = (page - 1) * PER_PAGE;
            const endIdx = Math.min(startIdx + PER_PAGE, cachedResults.length);
            const pageResults = cachedResults.slice(startIdx, endIdx);

            const m = cachedMeta;
            let countText = '';
            if (cachedResults.length > 0) {
                countText = 'Hiển thị ' + (startIdx+1) + '-' + endIdx + ' / ' + m.total_count + ' kết quả';
                if (m.total_matching > m.total_count) {
                    countText += ' (tổng ' + m.total_matching.toLocaleString() + ' docs matching)';
                }
                countText += ' (' + currentMode.toUpperCase() + ')';
                if (currentMode === 'hybrid') countText += ' | α=' + alphaSlider.value;
            } else {
                countText = 'Không tìm thấy kết quả';
            }
            document.getElementById('resultsCount').textContent = countText;
            document.getElementById('resultsTime').textContent = '⏱️ ' + m.time_ms + ' ms';

            const container = document.getElementById('resultsList');
            container.textContent = '';

            if (pageResults.length === 0) {
                const noRes = document.createElement('div');
                noRes.className = 'no-results';
                noRes.textContent = 'Không tìm thấy kết quả';
                container.appendChild(noRes);
            } else {
                pageResults.forEach((r, i) => {
                    const item = document.createElement('div');
                    item.className = 'result-item';

                    const title = document.createElement('div');
                    title.className = 'result-title';
                    const link = document.createElement('a');
                    link.href = r.url;
                    link.target = '_blank';
                    link.textContent = r.title || r.doc_id;
                    title.textContent = (startIdx + i + 1) + '. ';
                    title.appendChild(link);

                    const preview = document.createElement('div');
                    preview.className = 'result-preview';
                    preview.textContent = (r.content_preview || '') + '...';

                    const meta = document.createElement('div');
                    meta.className = 'result-meta';

                    const scoreSpan = document.createElement('span');
                    scoreSpan.className = 'result-score';
                    scoreSpan.textContent = 'Score: ' + r.score;
                    meta.appendChild(scoreSpan);

                    if (r.bm25_score !== undefined) {
                        const bs = document.createElement('span');
                        bs.textContent = 'BM25: ' + r.bm25_score;
                        meta.appendChild(bs);
                    }
                    if (r.vector_score !== undefined) {
                        const vs = document.createElement('span');
                        vs.textContent = 'Vector: ' + r.vector_score;
                        meta.appendChild(vs);
                    }

                    const authorSpan = document.createElement('span');
                    authorSpan.className = 'result-author';
                    authorSpan.textContent = '👤 ' + (r.author || 'Unknown');
                    meta.appendChild(authorSpan);

                    const idSpan = document.createElement('span');
                    idSpan.textContent = 'ID: ' + r.doc_id;
                    meta.appendChild(idSpan);

                    item.appendChild(title);
                    item.appendChild(preview);
                    item.appendChild(meta);
                    container.appendChild(item);
                });
            }

            renderPagination(page, totalPages);
        }

        function renderPagination(current, total) {
            const pag = document.getElementById('pagination');
            if (total <= 1) { pag.style.display = 'none'; return; }
            pag.textContent = '';
            pag.style.display = 'flex';

            function addBtn(text, page, disabled) {
                const btn = document.createElement('button');
                btn.className = 'page-btn' + (page === current ? ' active' : '');
                btn.textContent = text;
                btn.disabled = disabled;
                if (!disabled) btn.addEventListener('click', () => renderPage(page));
                pag.appendChild(btn);
            }

            addBtn('« Đầu', 1, current === 1);
            addBtn('‹ Trước', current - 1, current === 1);
            for (let i = Math.max(1, current-2); i <= Math.min(total, current+2); i++) {
                addBtn(String(i), i, false);
            }
            addBtn('Sau ›', current + 1, current === total);
            addBtn('Cuối »', total, current === total);
        }

        // Event listeners (outside renderPagination)
        document.getElementById('searchBtn').addEventListener('click', doSearch);
        document.getElementById('searchInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') doSearch();
        });

        // Load stats
        fetch('/stats')
            .then(r => r.json())
            .then(stats => {
                document.getElementById('statsBar').textContent = 
                    `📊 Docs: ${stats.total_docs || 0} | Vocab: ${stats.vocabulary_size || 0} | ` +
                    `BM25: ${stats.bm25_available ? '✅' : '❌'} | ` +
                    `Vector: ${stats.vector_available ? '✅' : '❌'} | ` +
                    `Hybrid: ${stats.hybrid_available ? '✅' : '❌'}`;
            });
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'search.html'), 'w', encoding='utf-8') as f:
        f.write(search_html)
    
    print("✅ Templates created with Filter and Pagination")


def cleanup_and_exit(signum=None, frame=None):
    """Giải phóng RAM khi tắt server (Ctrl+C)"""
    global bm25, index, hybrid_search, documents
    print("\n\n🧹 Đang giải phóng RAM...")

    if hybrid_search is not None:
        if hasattr(hybrid_search, 'vector_engine') and hybrid_search.vector_engine is not None:
            if hasattr(hybrid_search.vector_engine, 'model'):
                del hybrid_search.vector_engine.model
            if hasattr(hybrid_search.vector_engine, 'vector_index'):
                del hybrid_search.vector_engine.vector_index
            del hybrid_search.vector_engine
        del hybrid_search
        hybrid_search = None
        print("  ✅ Hybrid search freed")

    if bm25 is not None:
        del bm25
        bm25 = None
        print("  ✅ BM25 freed")

    if index is not None:
        del index
        index = None
        print("  ✅ Inverted index freed")

    documents.clear()
    print("  ✅ Document cache freed")

    gc.collect()

    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("  ✅ GPU VRAM freed")
    except ImportError:
        pass

    print("👋 Tất cả RAM đã được giải phóng. Tạm biệt!")
    sys.exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Voz Search Web UI')
    parser.add_argument('--host', default='0.0.0.0', help='Host')
    parser.add_argument('--port', '-p', type=int, default=5000, help='Port')
    parser.add_argument('--debug', action='store_true', help='Debug mode')

    args = parser.parse_args()

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    # Create templates
    create_templates()

    # Initialize search
    init_search_engines()

    print(f"\n🚀 Starting server at http://localhost:{args.port}")
    print("💡 Nhấn Ctrl+C để tắt server và giải phóng RAM")
    app.run(host=args.host, port=args.port, debug=args.debug)

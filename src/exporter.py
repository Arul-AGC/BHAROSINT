# src/exporter.py
"""
Export engine for BHAROSINT results.
Supports JSON, CSV, and styled HTML intelligence reports.
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional


def _ensure_dir(filepath: str):
    """Create parent directories if they don't exist."""
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)


def _build_filename(query: str, fmt: str, output_dir: str) -> str:
    """
    Generate a timestamped filename from the query.
    
    Why timestamp? OSINT analysts run the same query multiple times over days/weeks
    to track how information evolves. Without timestamps, they'd overwrite old reports.
    """
    # Sanitize query for filename — remove anything that's not alphanumeric or underscore
    safe_query = "".join(c if c.isalnum() or c == " " else "" for c in query)
    safe_query = safe_query.strip().replace(" ", "_")[:40]  # Cap length to avoid OS limits
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bharosint_{safe_query}_{timestamp}.{fmt}"
    
    return os.path.join(output_dir, filename)


def export_json(results: List[Dict], analysis: Optional[Dict], query: str,
                output_dir: str = "reports") -> str:
    """
    Export results and analysis to a structured JSON file.
    
    Returns the filepath of the created file.
    """
    filepath = _build_filename(query, "json", output_dir)
    _ensure_dir(filepath)
    
    payload = {
        "meta": {
            "tool": "BHAROSINT v2",
            "query": query,
            "exported_at": datetime.now().isoformat(),
            "total_results": len(results),
        },
        "results": results,
    }
    
    # Only include analysis if it was computed
    if analysis:
        payload["analysis"] = analysis
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
    
    return filepath


def export_csv(results: List[Dict], analysis: Optional[Dict], query: str,
               output_dir: str = "reports") -> str:
    """
    Export results to a flat CSV file.
    
    CSV is inherently flat (rows and columns), but our data is nested (dicts with
    varying keys). The approach: detect ALL unique keys across all result items,
    use them as column headers, and fill missing values with empty strings.
    This is called 'schema inference' — figuring out the shape of data at runtime.
    """
    filepath = _build_filename(query, "csv", output_dir)
    _ensure_dir(filepath)
    
    if not results:
        # Write an empty CSV with just the query as a comment
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["(No results found for query)", query])
        return filepath
    
    # Collect all unique keys across all result dicts to build the column headers
    all_keys = []
    seen_keys = set()
    for item in results:
        for key in item.keys():
            if key not in seen_keys:
                seen_keys.add(key)
                all_keys.append(key)
    
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        for item in results:
            # Convert any non-string values (lists, dicts) to string representation
            sanitized = {}
            for k, v in item.items():
                if isinstance(v, (list, dict)):
                    sanitized[k] = json.dumps(v, ensure_ascii=False)
                else:
                    sanitized[k] = v
            writer.writerow(sanitized)
    
    return filepath


def export_html(results: List[Dict], analysis: Optional[Dict], query: str,
                output_dir: str = "reports") -> str:
    """
    Export a fully styled HTML intelligence report.
    
    This is the portfolio showpiece — dark-themed, professional layout that
    looks like a Security Operations Center (SOC) dashboard.
    """
    filepath = _build_filename(query, "html", output_dir)
    _ensure_dir(filepath)
    
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    result_count = len(results)
    
    # --- Build the results table rows ---
    result_rows = ""
    for i, r in enumerate(results, 1):
        # Handle both search results and social results
        title = r.get("title") or r.get("original_text") or r.get("translated_text") or "-"
        snippet = r.get("snippet") or r.get("translated_text") or ""
        link = r.get("link") or r.get("url") or ""
        lang = r.get("lang") or r.get("source") or "-"
        
        # Truncate long text for table readability
        if len(snippet) > 200:
            snippet = snippet[:200] + "…"
        if len(title) > 100:
            title = title[:100] + "…"
        
        link_html = f'<a href="{_html_escape(link)}" target="_blank">{_html_escape(link[:60])}</a>' if link else "-"
        
        result_rows += f"""
        <tr>
            <td class="num">{i}</td>
            <td class="lang-badge">{_html_escape(str(lang))}</td>
            <td>{_html_escape(title)}</td>
            <td class="snippet">{_html_escape(snippet)}</td>
            <td class="link">{link_html}</td>
        </tr>"""
    
    # --- Build the analysis section ---
    analysis_html = ""
    if analysis:
        # Summary
        summary = analysis.get("summary", "(no summary)")
        
        # Keywords
        keywords = analysis.get("keywords", [])
        keywords_html = "".join(f'<span class="keyword-tag">{_html_escape(k)}</span>' for k in keywords)
        
        # Sentiment
        sentiment = analysis.get("sentiment", {})
        sent_label = sentiment.get("label", "N/A")
        sent_score = sentiment.get("score", 0)
        sent_class = "positive" if sent_score > 0 else "negative" if sent_score < 0 else "neutral"
        pos_terms = ", ".join(sentiment.get("positive_terms", [])) or "none"
        neg_terms = ", ".join(sentiment.get("negative_terms", [])) or "none"
        
        # Threat
        threat = analysis.get("threat", {})
        threat_level = threat.get("level", "NONE")
        threat_score = threat.get("score", 0)
        threat_class = "critical" if threat_level == "CRITICAL" else "high" if threat_level == "HIGH" else "medium" if threat_level == "MEDIUM" else "low"
        threat_terms = ", ".join(threat.get("threat_terms", [])) or "none"
        strong_terms = ", ".join(threat.get("strong_terms", [])) or "none"
        
        # Entities
        entities = analysis.get("entities", {})
        entities_rows = ""
        for etype, items in entities.items():
            if items:
                items_html = ", ".join(_html_escape(str(item)) for item in items)
                entities_rows += f'<tr><td class="entity-type">{_html_escape(etype.capitalize())}</td><td>{items_html}</td></tr>'
        
        # Stats
        stats = analysis.get("stats", {})
        
        analysis_html = f"""
        <section class="analysis-section">
            <h2>🧠 NLP Analysis</h2>
            
            <div class="card-grid">
                <div class="card summary-card">
                    <h3>📋 Summary</h3>
                    <p>{_html_escape(summary)}</p>
                </div>
                
                <div class="card sentiment-card">
                    <h3>💬 Sentiment</h3>
                    <div class="metric">
                        <span class="metric-label">Verdict</span>
                        <span class="metric-value {sent_class}">{sent_label} ({sent_score:+d})</span>
                    </div>
                    <div class="terms-row">
                        <span class="term-positive">⊕ {_html_escape(pos_terms)}</span>
                        <span class="term-negative">⊖ {_html_escape(neg_terms)}</span>
                    </div>
                </div>
                
                <div class="card threat-card">
                    <h3>⚠️ Threat Level</h3>
                    <div class="metric">
                        <span class="metric-label">Level</span>
                        <span class="metric-value threat-{threat_class}">{threat_level} (Score: {threat_score})</span>
                    </div>
                    <div class="terms-row">
                        <span class="term-negative">Threats: {_html_escape(threat_terms)}</span>
                        <span class="term-negative">Strong: {_html_escape(strong_terms)}</span>
                    </div>
                </div>
                
                <div class="card stats-card">
                    <h3>📊 Statistics</h3>
                    <div class="metric">
                        <span class="metric-label">Items Analyzed</span>
                        <span class="metric-value">{stats.get('items_analyzed', 0)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Tokens</span>
                        <span class="metric-value">{stats.get('total_tokens', 0)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Unique Terms</span>
                        <span class="metric-value">{stats.get('unique_terms', 0)}</span>
                    </div>
                </div>
            </div>
            
            <div class="card keywords-card">
                <h3>🔑 Top Keywords</h3>
                <div class="keywords-cloud">{keywords_html}</div>
            </div>
            
            {"<div class='card entities-card'><h3>🏷️ Entities</h3><table class='entities-table'><tr><th>Type</th><th>Items</th></tr>" + entities_rows + "</table></div>" if entities_rows else ""}
        </section>"""
    
    # --- Assemble the full HTML ---
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BHAROSINT Report — {_html_escape(query)}</title>
    <style>
        /* ===== RESET & BASE ===== */
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        :root {{
            --bg-primary: #0a0a12;
            --bg-secondary: #111122;
            --bg-card: #161630;
            --bg-card-hover: #1c1c40;
            --border: #2a2a4a;
            --text-primary: #e0e0f0;
            --text-secondary: #8888aa;
            --accent-cyan: #00e5ff;
            --accent-green: #00e676;
            --accent-red: #ff1744;
            --accent-yellow: #ffea00;
            --accent-orange: #ff9100;
            --accent-purple: #b388ff;
            --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
            --font-sans: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }}
        
        body {{
            font-family: var(--font-sans);
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* ===== HEADER ===== */
        .header {{
            background: linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 50%, #0d1a2e 100%);
            border-bottom: 1px solid var(--border);
            padding: 2.5rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        .header::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: 
                radial-gradient(ellipse at 20% 50%, rgba(0, 229, 255, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 50%, rgba(179, 136, 255, 0.08) 0%, transparent 50%);
            pointer-events: none;
        }}
        .header h1 {{
            font-family: var(--font-mono);
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }}
        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        .header .meta-row {{
            margin-top: 1rem;
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        .meta-chip {{
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.4rem 1rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}
        .meta-chip strong {{
            color: var(--accent-cyan);
        }}
        
        /* ===== CONTENT ===== */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        h2 {{
            font-family: var(--font-mono);
            font-size: 1.4rem;
            color: var(--accent-cyan);
            margin-bottom: 1.2rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}
        
        /* ===== RESULTS TABLE ===== */
        .results-section {{
            margin-bottom: 3rem;
        }}
        .results-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        .results-table th {{
            background: var(--bg-secondary);
            color: var(--accent-cyan);
            font-family: var(--font-mono);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.75rem;
            padding: 0.8rem 1rem;
            text-align: left;
            border-bottom: 2px solid var(--border);
            position: sticky;
            top: 0;
        }}
        .results-table td {{
            padding: 0.7rem 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            vertical-align: top;
        }}
        .results-table tr:hover td {{
            background: var(--bg-card-hover);
        }}
        .results-table .num {{
            color: var(--text-secondary);
            font-family: var(--font-mono);
            font-size: 0.8rem;
            width: 3rem;
        }}
        .results-table .lang-badge {{
            font-family: var(--font-mono);
            font-size: 0.75rem;
            color: var(--accent-purple);
            width: 5rem;
        }}
        .results-table .snippet {{
            color: var(--text-secondary);
            font-size: 0.8rem;
            max-width: 350px;
        }}
        .results-table .link a {{
            color: var(--accent-cyan);
            text-decoration: none;
            font-size: 0.8rem;
            word-break: break-all;
        }}
        .results-table .link a:hover {{
            text-decoration: underline;
        }}
        
        /* ===== ANALYSIS CARDS ===== */
        .analysis-section {{
            margin-bottom: 3rem;
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.2rem;
            margin-bottom: 1.2rem;
        }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1.5rem;
            transition: border-color 0.2s;
        }}
        .card:hover {{
            border-color: rgba(0, 229, 255, 0.3);
        }}
        .card h3 {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            color: var(--text-primary);
        }}
        .card p {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.7;
        }}
        
        /* Metrics inside cards */
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.4rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }}
        .metric:last-of-type {{ border-bottom: none; }}
        .metric-label {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        .metric-value {{
            font-family: var(--font-mono);
            font-weight: 600;
            font-size: 0.95rem;
        }}
        .metric-value.positive {{ color: var(--accent-green); }}
        .metric-value.negative {{ color: var(--accent-red); }}
        .metric-value.neutral {{ color: var(--accent-yellow); }}
        .metric-value.threat-critical {{ color: var(--accent-red); text-shadow: 0 0 10px rgba(255,23,68,0.5); }}
        .metric-value.threat-high {{ color: var(--accent-orange); }}
        .metric-value.threat-medium {{ color: var(--accent-yellow); }}
        .metric-value.threat-low {{ color: var(--accent-green); }}
        
        .terms-row {{
            margin-top: 0.6rem;
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
            font-size: 0.8rem;
        }}
        .term-positive {{ color: var(--accent-green); }}
        .term-negative {{ color: var(--accent-red); }}
        
        /* Keywords cloud */
        .keywords-cloud {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .keyword-tag {{
            background: rgba(0, 229, 255, 0.1);
            border: 1px solid rgba(0, 229, 255, 0.25);
            color: var(--accent-cyan);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-family: var(--font-mono);
            transition: background 0.2s;
        }}
        .keyword-tag:hover {{
            background: rgba(0, 229, 255, 0.2);
        }}
        
        /* Entities table */
        .entities-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        .entities-table th {{
            text-align: left;
            color: var(--accent-purple);
            font-family: var(--font-mono);
            font-size: 0.75rem;
            text-transform: uppercase;
            padding: 0.5rem 0.8rem;
            border-bottom: 1px solid var(--border);
        }}
        .entities-table td {{
            padding: 0.5rem 0.8rem;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }}
        .entity-type {{
            color: var(--accent-purple);
            font-family: var(--font-mono);
            font-weight: 600;
            white-space: nowrap;
        }}
        
        /* ===== FOOTER ===== */
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
            margin-top: 2rem;
        }}
        .footer a {{
            color: var(--accent-cyan);
            text-decoration: none;
        }}
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.4rem; }}
            .container {{ padding: 1rem; }}
            .card-grid {{ grid-template-columns: 1fr; }}
            .results-table {{ font-size: 0.75rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚔ BHAROSINT</h1>
        <div class="subtitle">Multilingual Open Source Intelligence Report</div>
        <div class="meta-row">
            <span class="meta-chip"><strong>Query:</strong> {_html_escape(query)}</span>
            <span class="meta-chip"><strong>Results:</strong> {result_count}</span>
            <span class="meta-chip"><strong>Generated:</strong> {timestamp}</span>
        </div>
    </div>
    
    <div class="container">
        <section class="results-section">
            <h2>🔍 Intelligence Results</h2>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Source</th>
                        <th>Title</th>
                        <th>Snippet</th>
                        <th>Link</th>
                    </tr>
                </thead>
                <tbody>
                    {result_rows if result_rows else '<tr><td colspan="5" style="text-align:center; color:var(--text-secondary);">No results found</td></tr>'}
                </tbody>
            </table>
        </section>
        
        {analysis_html}
    </div>
    
    <div class="footer">
        Generated by <a href="https://github.com/Arul-AGC/BHAROSINT" target="_blank">BHAROSINT v2</a> — Multilingual OSINT Framework
    </div>
</body>
</html>"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    return filepath


def _html_escape(text: str) -> str:
    """Escape HTML special characters to prevent XSS in generated reports."""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def export_results(results: List[Dict], analysis: Optional[Dict], query: str,
                   fmt: str = "json", output_dir: str = "reports") -> str:
    """
    Unified export dispatcher.
    
    This is the PUBLIC API — callers use this single function regardless of format.
    Internally it delegates to the right format-specific function.
    This pattern is called 'Strategy dispatch' — the format string selects the strategy.
    """
    exporters = {
        "json": export_json,
        "csv": export_csv,
        "html": export_html,
    }
    
    exporter_fn = exporters.get(fmt.lower())
    if not exporter_fn:
        raise ValueError(f"Unknown export format: '{fmt}'. Supported: {', '.join(exporters.keys())}")
    
    filepath = exporter_fn(results, analysis, query, output_dir)
    return filepath

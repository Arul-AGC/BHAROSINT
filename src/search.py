# src/search.py
"""
DuckDuckGo search engine with rate limiting, exponential backoff,
and structured logging.
"""

import re
import time
from ddgs import DDGS
from src.config import CFG
from src.logger import get_logger

log = get_logger("search")

# ─── Input Validation ─────────────────────────────────────────────

# Strip characters that could break search APIs or be used for injection
_SANITIZE_RE = re.compile(r"[<>{}\[\]|\\^~`]")

def sanitize_query(query: str) -> str:
    """Remove potentially dangerous characters from search queries."""
    if not query:
        return ""
    cleaned = _SANITIZE_RE.sub("", query).strip()
    # Cap length to prevent abuse
    return cleaned[:500]


# ─── Language Filtering ───────────────────────────────────────────

def _filter_by_language(items, lang_code):
    """Soft language filtering: keeps items that appear to match target language."""
    filtered = []
    for item in items:
        text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()

        if lang_code == "hi" and any("\u0900" <= c <= "\u097F" for c in text):
            filtered.append(item)
        elif lang_code == "ta" and any("\u0B80" <= c <= "\u0BFF" for c in text):
            filtered.append(item)
        elif lang_code == "te" and any("\u0C00" <= c <= "\u0C7F" for c in text):
            filtered.append(item)
        elif lang_code == "ml" and any("\u0D00" <= c <= "\u0D7F" for c in text):
            filtered.append(item)
        elif lang_code == "bn" and any("\u0980" <= c <= "\u09FF" for c in text):
            filtered.append(item)
        elif lang_code == "en":
            filtered.append(item)

    return filtered if filtered else items


# ─── Core Search with Retry + Backoff ─────────────────────────────

def duckduckgo_search(query, limit=10, lang="en"):
    """
    DuckDuckGo search with exponential backoff.

    On failure, waits progressively longer before retrying:
      Attempt 1: immediate
      Attempt 2: wait 1s
      Attempt 3: wait 2s
      Attempt 4: wait 4s
    This prevents hammering DDG when rate-limited.
    """
    query = sanitize_query(query)
    if not query:
        log.warning("Empty query after sanitization, skipping search")
        return []

    max_retries = CFG["search"]["max_retries"]
    delay = CFG["search"]["request_delay"]

    for attempt in range(1, max_retries + 1):
        try:
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=limit)

                for item in search_results:
                    formatted_item = {
                        "title": item.get("title", ""),
                        "snippet": item.get("body", ""),
                        "link": item.get("href", "")
                    }
                    results.append(formatted_item)

            results = _filter_by_language(results, lang)
            log.debug("Search [%s] lang=%s → %d results", query[:40], lang, len(results))
            return results

        except Exception as e:
            backoff = delay * (2 ** (attempt - 1))  # Exponential: 0.8, 1.6, 3.2
            log.warning(
                "Search attempt %d/%d failed: %s — retrying in %.1fs",
                attempt, max_retries, str(e)[:80], backoff
            )
            if attempt < max_retries:
                time.sleep(backoff)

    log.error("Search exhausted all %d retries for query: %s", max_retries, query[:60])
    return []
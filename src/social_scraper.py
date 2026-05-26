# src/social_scraper.py
"""
Social media intelligence gathering via DuckDuckGo site queries.

Uses rate limiting, exponential backoff, and structured logging.
"""

import time
from ddgs import DDGS
from src.translator import translate_snippet
from src.config import CFG
from src.logger import get_logger
from src.search import sanitize_query

log = get_logger("social")

# ─── Platform Scrapers ────────────────────────────────────────────

def _scrape_platform(query, platform, site_domain, limit=5):
    """Generic site-scoped search with retry and backoff."""
    query = sanitize_query(query)
    if not query:
        return []

    max_retries = CFG["search"]["max_retries"]
    delay = CFG["search"]["request_delay"]
    full_query = f"site:{site_domain} {query}"

    log.info("Scraping %s for: %s", platform, query[:50])

    for attempt in range(1, max_retries + 1):
        try:
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(full_query, max_results=limit)
                for item in search_results:
                    title = item.get("title", "")
                    body = item.get("body", "")
                    raw_text = f"{title} - {body}".strip(" -")
                    results.append({
                        "source": platform.capitalize(),
                        "platform": platform.lower(),
                        "author": None,
                        "original_text": raw_text,
                        "translated_text": translate_snippet(raw_text, target="en"),
                        "url": item.get("href", ""),
                        "date": None,
                    })

            log.debug("%s scrape → %d results", platform, len(results))
            return results

        except Exception as e:
            backoff = delay * (2 ** (attempt - 1))
            log.warning(
                "%s attempt %d/%d failed: %s — retrying in %.1fs",
                platform, attempt, max_retries, str(e)[:80], backoff
            )
            if attempt < max_retries:
                time.sleep(backoff)

    log.error("%s scrape exhausted all retries for: %s", platform, query[:60])
    return []


def scrape_twitter(query, limit=5):
    return _scrape_platform(query, "Twitter", "twitter.com", limit)


def scrape_reddit(query, limit=5):
    return _scrape_platform(query, "Reddit", "reddit.com", limit)


# ─── Aggregator ───────────────────────────────────────────────────

def collect_social_data(query, sources=None, limit=5):
    if sources is None:
        sources = ["twitter", "reddit"]

    all_results = []
    delay = CFG["search"]["request_delay"]

    if "twitter" in sources:
        all_results.extend(scrape_twitter(query, limit))
        time.sleep(delay)  # Spacing between platforms

    if "reddit" in sources:
        all_results.extend(scrape_reddit(query, limit))

    log.info("Social scrape total: %d posts", len(all_results))
    return all_results
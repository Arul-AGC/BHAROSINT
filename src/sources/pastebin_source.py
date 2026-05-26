# src/sources/pastebin_source.py
"""
Paste site monitoring via DuckDuckGo.
Searches pastebin.com, ghostbin, etc. for leaked data, credentials, or mentions.
"""

import time
from ddgs import DDGS
from src.config import CFG
from src.logger import get_logger
from src.search import sanitize_query

log = get_logger("pastebin")

PASTE_SITES = ["pastebin.com", "ghostbin.com", "controlc.com", "justpaste.it"]

def search_paste_sites(query: str, limit: int = 3) -> list:
    """Query various paste sites for potential leaks."""
    query = sanitize_query(query)
    if not query:
        return []
        
    max_retries = CFG["search"]["max_retries"]
    delay = CFG["search"]["request_delay"]
    
    all_results = []
    
    log.info("Scraping paste sites for: %s", query[:50])

    for site in PASTE_SITES:
        full_query = f"site:{site} {query}"
        
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
                            "source": "Paste Dump",
                            "platform": site,
                            "title": title,
                            "snippet": body,
                            "link": item.get("href", ""),
                        })

                all_results.extend(results)
                break  # Success, no need to retry this site

            except Exception as e:
                backoff = delay * (2 ** (attempt - 1))
                log.warning(
                    "%s scrape attempt %d/%d failed: %s — retrying in %.1fs",
                    site, attempt, max_retries, str(e)[:80], backoff
                )
                if attempt < max_retries:
                    time.sleep(backoff)
                    
        # Spacing between sites
        time.sleep(delay)

    log.debug("Paste sites returned %d total results", len(all_results))
    return all_results

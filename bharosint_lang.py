# bharosint_lang.py
"""
Multilingual search orchestrator.

Translates query into each configured language, searches DDG for each,
deduplicates by URL, and respects rate-limit spacing between requests.
"""

import time
from src.translator import translate_query
from src.search import duckduckgo_search
from src.config import CFG
from src.logger import get_logger

log = get_logger("lang")

LANGUAGES = CFG.get("languages", {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Bengali": "bn",
})


def regional_search(query):
    """Perform multilingual search and print results to console."""
    log.info("Starting multilingual search for: %s", query[:60])
    all_results = []
    delay = CFG["search"]["request_delay"]
    limit = CFG["search"]["results_per_lang"]

    try:
        for lang_name, lang_code in LANGUAGES.items():
            translated = translate_query(query, lang_code)
            log.info("[%s] (%s) → %s", lang_name, lang_code, translated[:60])
            results = duckduckgo_search(translated, limit=limit, lang=lang_code)
            for r in results:
                r["lang"] = lang_name
                all_results.append(r)

            # Rate-limit spacing between language queries
            time.sleep(delay)

        seen = set()
        unique = []
        for r in all_results:
            link = r.get("link") or r.get("href") or ""
            if link and link not in seen:
                seen.add(link)
                unique.append(r)

        log.info("Multilingual search complete: %d unique results", len(unique))
        for i, r in enumerate(unique, 1):
            print(f"{i}. [{r['lang']}]")
            print(f"   Title   : {r.get('title','')}")
            print(f"   Snippet : {r.get('snippet','')}")
            print(f"   URL     : {r.get('link','')}\n")

    except Exception as e:
        log.error("Regional search failed: %s", e)


def regional_search_results(query):
    """Return a list of result dicts for NLP processing."""
    all_results = []
    delay = CFG["search"]["request_delay"]
    limit = CFG["search"]["results_per_lang"]

    for lang_name, lang_code in LANGUAGES.items():
        try:
            translated = translate_query(query, lang_code)
            log.info("[%s] (%s) → %s", lang_name, lang_code, translated[:60])
            results = duckduckgo_search(translated, limit=limit, lang=lang_code)
            for r in results:
                r["lang"] = lang_name
                r.setdefault("title", "")
                r.setdefault("snippet", "")
                r.setdefault("link", "")
                all_results.append(r)

            # Rate-limit spacing
            time.sleep(delay)

        except Exception as e:
            log.warning("Search for %s failed: %s — skipping", lang_name, e)
            continue

    seen = set()
    unique = []
    for r in all_results:
        link = r.get("link") or r.get("href") or ""
        if link and link not in seen:
            seen.add(link)
            unique.append(r)

    return unique
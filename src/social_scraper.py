# src/social_scraper.py
from ddgs import DDGS
from src.translator import translate_snippet

def scrape_twitter(query, limit=5):
    print(f"[>] Fallback Twitter via DuckDuckGo: {query}")
    results = []
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(f"site:twitter.com {query}", max_results=limit)
            for item in search_results:
                title = item.get("title", "")
                body = item.get("body", "")
                raw_text = f"{title} - {body}".strip(" -")
                results.append({
                    "source": "Twitter",
                    "platform": "twitter",
                    "author": None,
                    "original_text": raw_text,
                    "translated_text": translate_snippet(raw_text, target="en"),
                    "url": item.get("href", ""),
                    "date": None
                })
    except Exception as e:
        print(f"[!] Twitter fallback failed: {e}")
    return results

def scrape_reddit(query, limit=5):
    print(f"[>] Scraping Reddit via DuckDuckGo: {query}")
    results = []
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(f"site:reddit.com {query}", max_results=limit)
            for item in search_results:
                title = item.get("title", "")
                body = item.get("body", "")
                raw_text = f"{title} - {body}".strip(" -")
                results.append({
                    "source": "Reddit",
                    "platform": "reddit",
                    "author": None,
                    "original_text": raw_text,
                    "translated_text": translate_snippet(raw_text, target="en"),
                    "url": item.get("href", ""),
                    "date": None
                })
    except Exception as e:
        print(f"[!] Reddit scraping failed: {e}")
    return results

def collect_social_data(query, sources=None, limit=5):
    if sources is None:
        sources = ["twitter", "reddit"]

    all_results = []
    if "twitter" in sources:
        all_results.extend(scrape_twitter(query, limit))
    if "reddit" in sources:
        all_results.extend(scrape_reddit(query, limit))

    print(f"[+] Found {len(all_results)} total social posts.")
    return all_results
# src/search.py
from ddgs import DDGS

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

def duckduckgo_search(query, limit=10, lang="en"):
    """DuckDuckGo search using the stable DDGS API."""
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
        return results

    except Exception as e:
        print(f"[!] Error in duckduckgo_search: {e}") 
        return []
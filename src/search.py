# src/search.py
# Backwards-compatible DuckDuckGo search wrapper.
# Exposes duckduckgo_search(query, max_results=5) exactly as before,
# implemented using the ddgs library internally.

from ddgs import DDGS

def duckduckgo_search(query, max_results=5):
    """
    Perform a DuckDuckGo text search and return a list of dicts:
      [{"title": ..., "link": ..., "snippet": ...}, ...]
    This function keeps the same public name/signature your main files expect.
    """
    try:
        results = []
        with DDGS() as ddgs:
            # ddgs.text yields dicts with keys like 'title', 'href', 'body'
            for item in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": item.get("title", "No title"),
                    "link": item.get("href", "No link"),
                    "snippet": item.get("body", "")
                })
        return results
    except Exception as e:
        # Keep messages visible for debugging but non-fatal for the app
        print(f"[!] ddgs_search error: {e}")
        return []

# bharosint_lang.py

from src.translator import translate_query
from src.search import duckduckgo_search

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Bengali": "bn"
}

def regional_search(query):
    """Perform multilingual search and print results to console."""
    print(f"\n[+] Searching multiple languages for: {query}\n")
    all_results = []
    try:
        for lang_name, lang_code in LANGUAGES.items():
            translated = translate_query(query, lang_code)
            print(f"[>] {lang_name:9} ({lang_code}) → {translated}")
            results = duckduckgo_search(translated, limit=8, lang=lang_code)
            for r in results:
                r["lang"] = lang_name
                all_results.append(r)

        seen = set()
        unique = []
        for r in all_results:
            link = r.get("link") or r.get("href") or ""
            if link and link not in seen:
                seen.add(link)
                unique.append(r)

        print(f"\n[+] Found {len(unique)} multilingual search results:\n")
        for i, r in enumerate(unique, 1):
            print(f"{i}. [{r['lang']}]")
            print(f"   Title   : {r.get('title','')}")
            print(f"   Snippet : {r.get('snippet','')}")
            print(f"   URL     : {r.get('link','')}\n")

    except Exception as e:
        print(f"[!] Regional search failed: {e}\n")

def regional_search_results(query):
    """Return a list of result dicts for NLP processing."""
    all_results = []
    for lang_name, lang_code in LANGUAGES.items():
        try:
            translated = translate_query(query, lang_code)
            results = duckduckgo_search(translated, limit=8, lang=lang_code)
            for r in results:
                r["lang"] = lang_name
                r.setdefault("title", "")
                r.setdefault("snippet", "")
                r.setdefault("link", "")
                all_results.append(r)
        except Exception:
            continue

    seen = set()
    unique = []
    for r in all_results:
        link = r.get("link") or r.get("href") or ""
        if link and link not in seen:
            seen.add(link)
            unique.append(r)

    return unique
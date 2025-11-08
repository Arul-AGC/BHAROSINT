from src.search import duckduckgo_search
from src.translator import detect_language, translate_query, translate_snippet

def regional_search(query, max_results=5):
    detected_lang = detect_language(query)

    if detected_lang == "en":
        # Translate English keywords into major Indian languages
        indian_langs = ["hi", "ta", "te", "ml", "bn", "gu"]
        queries = [query] + [translate_query(query, lang) for lang in indian_langs]
    else:
        # Translate regional queries to English for scraping
        queries = [query, translate_query(query, "en")]

    all_results = []
    for q in queries:
        results = duckduckgo_search(q, max_results=max_results)
        for r in results:
            # Translate non-English titles to English
            r["title"] = translate_snippet(r["title"], "en")
            all_results.append(r)

    # Deduplicate
    unique_results = []
    seen_links = set()
    for r in all_results:
        if r["link"] not in seen_links:
            seen_links.add(r["link"])
            unique_results.append(r)

    return unique_results

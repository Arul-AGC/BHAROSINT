from src.search import duckduckgo_search
from src.translator import detect_language, translate_query, translate_snippet
from src.utils import deduplicate_results, pretty_table

SUPPORTED_LANGS = ["hi", "ta", "bn"]  # Hindi, Tamil, Bengali

def regional_search(query: str):
    lang, conf = detect_language(query)
    print(f"Detected language: {lang} (confidence {conf:.2f})")

    results_all = []

    # Case 1: English input → expand into Indic queries
    if lang == "en":
        print("Input detected as English — expanding to regional queries.")
        for target_lang in SUPPORTED_LANGS:
            translated_query = translate_query(query, target_lang)
            results = duckduckgo_search(translated_query)
            for r in results:
                r["translated_title"] = translate_snippet(r["title"])
            results_all.extend(results)

    # Case 2: Indic input → search directly & translate back
    else:
        print(f"Input detected as {lang}. Searching in that language and translating back.")
        results = duckduckgo_search(query)
        for r in results:
            r["translated_title"] = translate_snippet(r["title"])
        results_all.extend(results)

    # Deduplicate & pretty print
    results_all = deduplicate_results(results_all)
    pretty_table(results_all)

# src/translator.py
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory, LangDetectException
from typing import Optional
import time

DetectorFactory.seed = 0

LANG_ALIAS = {
    "english": "en", "en": "en",
    "hindi": "hi", "hi": "hi",
    "tamil": "ta", "ta": "ta",
    "telugu": "te", "te": "te",
    "malayalam": "ml", "ml": "ml",
    "bengali": "bn", "bn": "bn",
}

def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "unknown"
    try:
        code = detect(text)
        return code
    except LangDetectException:
        return "unknown"
    except Exception:
        return "unknown"

def _normalize_lang_code(code: Optional[str]) -> str:
    if not code:
        return "en"
    code = code.strip().lower()
    return LANG_ALIAS.get(code, code[:2]) 

def translate_query(text: str, target_lang: str = "en") -> str:
    if not text or not text.strip():
        return text

    target = _normalize_lang_code(target_lang)

    try:
        src_lang = detect_language(text)
    except Exception:
        src_lang = "unknown"

    if src_lang == target:
        return text

    attempts = 2
    for attempt in range(attempts):
        try:
            translated = GoogleTranslator(source="auto", target=target).translate(text)
            if translated and isinstance(translated, str):
                if translated.strip() == text.strip():
                    return text
                return translated
        except Exception:
            time.sleep(0.3)
            continue

    return text

def translate_snippet(text: str, target: str = "en") -> str:
    return translate_query(text, target)
# src/translator.py
"""
Translator utilities using deep-translator as a stable fallback.
Provides:
- detect_language(text) -> returns best-guess lang code (uses langdetect)
- translate_query(text, target_lang) -> translates into target language
- translate_snippet(text, target_lang='en') -> translates snippet to English by default
"""

from deep_translator import GoogleTranslator, exceptions as dt_exceptions
from langdetect import detect, DetectorFactory, LangDetectException

DetectorFactory.seed = 0  # deterministic langdetect results


def detect_language(text: str) -> (str, float):
    """
    Return (lang_code, confidence). If detection fails, returns ('unknown', 0.0).
    """
    try:
        if not text or not text.strip():
            return "unknown", 0.0
        code = detect(text)
        # langdetect doesn't provide numeric confidence, return 1.0 as placeholder
        return code, 1.0
    except LangDetectException:
        return "unknown", 0.0
    except Exception:
        return "unknown", 0.0


def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translate text to target_lang using deep-translator GoogleTranslator (best-effort).
    If translation fails, returns the original text.
    Note: target_lang should be an ISO code like 'en','hi','ta','bn' etc.
    """
    if not text:
        return ""
    try:
        # GoogleTranslator uses 'auto' detection for source by default
        translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
        return translated
    except dt_exceptions.NotValidPayload as e:
        # Bad input, return original
        return text
    except dt_exceptions.ServerException:
        return text
    except Exception:
        # Last-resort: return original
        return text


# Convenience wrappers used by the rest of the code:
def translate_query(query: str, target_lang: str) -> str:
    return translate_text(query, target_lang)


def translate_snippet(snippet: str, target_lang: str = "en") -> str:
    return translate_text(snippet, target_lang)

import pytest
from src.translator import detect_language, translate_query, _normalize_lang_code

def test_detect_language():
    assert detect_language("Hello world") == "en"
    # Even if it fails on short strings, it shouldn't crash
    assert detect_language("") == "unknown"

def test_normalize_lang_code():
    assert _normalize_lang_code("hindi") == "hi"
    assert _normalize_lang_code("tamil") == "ta"
    assert _normalize_lang_code("UNKNOWN") == "un"
    assert _normalize_lang_code(None) == "en"

def test_translate_query_same_lang(mocker):
    # If the target language is the same as the detected one, it should return original
    mocker.patch("src.translator.detect_language", return_value="en")
    result = translate_query("test query", "en")
    assert result == "test query"

def test_translate_query_empty():
    assert translate_query("") == ""
    assert translate_query("   ") == "   "

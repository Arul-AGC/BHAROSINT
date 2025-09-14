from langdetect import detect, DetectorFactory
from googletrans import Translator

DetectorFactory.seed = 0
translator = Translator()

def detect_language(text: str):
    try:
        lang = detect(text)
        return lang, 1.0
    except:
        return "unknown", 0.0

def translate_query(query: str, target_lang: str):
    return translator.translate(query, dest=target_lang).text

def translate_snippet(text: str):
    return translator.translate(text, dest="en").text

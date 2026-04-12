# src/nlp_engine.py
import re
import math
from collections import Counter, defaultdict

try:
    import spacy
    # Load the English model for native English text and translations
    nlp_en = spacy.load("en_core_web_sm")
    # Load the Multilingual model for native Indian language text
    try:
        nlp_xx = spacy.load("xx_ent_wiki_sm")
    except Exception:
        nlp_xx = None
except Exception:
    raise RuntimeError("Spacy models missing. Run: python3 -m spacy download en_core_web_sm && python3 -m spacy download xx_ent_wiki_sm")

try:
    import nltk
    from nltk.corpus import stopwords
except Exception:
    raise RuntimeError("nltk is required. Install it (pip install nltk) and run once to download corpora.")

def _ensure_nltk():
    try:
        stopwords.words("english")
    except LookupError:
        nltk.download("stopwords", quiet=True)

_ensure_nltk()

EN_STOPWORDS = set(stopwords.words("english"))
TA_STOPWORDS = {"ஆகும்", "என்று", "இல்", "மற்றும்", "ஒரு", "இந்த", "என்ற", "ஆனால்", "உள்ள", "என", "அவர்", "அல்லது", "எனவே", "இது", "அதை", "அவர்கள்"}

URL_RE = re.compile(r"https?://\S+|www\.\S+")
HTML_TAG_RE = re.compile(r"<[^>]+>")
# Advanced IoC (Indicator of Compromise) Regex patterns
IPV4_RE = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
MD5_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")
SHA256_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")
CVE_RE = re.compile(r"(CVE-(19|20)\d{2}-\d{4,7})", re.IGNORECASE)

def clean_text(text: str) -> str:
    if not text:
        return ""
    s = HTML_TAG_RE.sub(" ", text)
    s = URL_RE.sub(" ", s)
    s = s.replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", s).strip()

def sentence_split(text: str):
    """Splits text into sentences and strictly deduplicates them to prevent echo-chamber summaries."""
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text)
    
    seen = set()
    unique_sents = []
    for p in parts:
        clean_p = p.strip()
        # Prevent exact duplicate sentences (ignoring case)
        if len(clean_p) > 5 and clean_p.lower() not in seen:
            seen.add(clean_p.lower())
            unique_sents.append(clean_p)
            
    return unique_sents

def tokenize(text: str):
    if not text:
        return []
    return re.findall(r"[\w\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F\u0D00-\u0D7F\u0980-\u09FF]+", text.lower())

def extract_iocs(corpus_text: str):
    """Extract Cyber Threat Intelligence Indicators."""
    return {
        "IP Addresses": list(set(IPV4_RE.findall(corpus_text))),
        "CVE Vulnerabilities": list(set([m[0].upper() for m in CVE_RE.findall(corpus_text)])),
        "MD5/SHA256 Hashes": list(set(MD5_RE.findall(corpus_text) + SHA256_RE.findall(corpus_text)))
    }

def extract_entities_spacy(corpus_text: str):
    """Use Spacy's NLP pipeline for deterministic Named Entity Recognition."""
    entities = {"persons": set(), "organizations": set(), "locations": set(), "dates": set()}
    
    docs = []
    # Process text through English model (100k char limit)
    if nlp_en:
        docs.append(nlp_en(corpus_text[:100000]))
    # Process text through Multilingual model
    if nlp_xx:
        docs.append(nlp_xx(corpus_text[:100000]))
    
    for doc in docs:
        for ent in doc.ents:
            clean_ent = ent.text.strip().title()
            if len(clean_ent) < 2 or clean_ent.lower() in EN_STOPWORDS:
                continue
                
            # Note: xx_ent_wiki_sm uses 'PER', English uses 'PERSON'
            if ent.label_ in ["PERSON", "PER"]:
                entities["persons"].add(clean_ent)
            elif ent.label_ in ["ORG"]:
                entities["organizations"].add(clean_ent)
            # 'GPE' (Geopolitical Entity) vs 'LOC' (Location)
            elif ent.label_ in ["GPE", "LOC"]:
                entities["locations"].add(clean_ent)
            elif ent.label_ == "DATE":
                entities["dates"].add(clean_ent)
            
    return {k: sorted(list(v)) for k, v in entities.items()}

def summarize_textrank_math(corpus_text: str, num_sentences: int = 3):
    """
    Mathematical Extractive Summarization using TF-IDF and Sentence Graphing.
    Mimics the TextRank algorithm without requiring heavy external graph libraries.
    """
    sentences = sentence_split(corpus_text)
    if len(sentences) <= num_sentences:
        return corpus_text

    # 1. Calculate Word Frequencies (Term Frequency)
    tokens = tokenize(corpus_text)
    filtered_tokens = [t for t in tokens if t not in EN_STOPWORDS and t not in TA_STOPWORDS and len(t) > 2]
    word_frequencies = Counter(filtered_tokens)
    
    if not word_frequencies:
        return "Insufficient text for summarization."

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / max_frequency)

    # 2. Score Sentences based on mathematically weighted words
    sentence_scores = {}
    for sent in sentences:
        sent_tokens = tokenize(sent)
        if 5 < len(sent_tokens) < 40: # Ignore overly short or long sentences
            score = 0
            for word in sent_tokens:
                if word in word_frequencies:
                    score += word_frequencies[word]
            sentence_scores[sent] = score

    # 3. Extract top sentences and maintain chronological order
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    
    # Sort them back into the order they appeared in the text
    summary = []
    for sent in sentences:
        if sent in top_sentences:
            summary.append(sent)
            
    return " ".join(summary)

# --- Lexicon-based Sentiment & Threat Analysis ---
POS_LEXICON = {
    "good", "safe", "secure", "recovered", "success", "peace", "stable", 
    "positive", "win", "resolved", "released", "protected", "thriving", 
    "rescued", "neutralized", "prevented", "healthy", "growth", "boom", 
    "praise", "applaud", "celebrate", "improved", "arrested", "captured", "patched"
}
NEG_LEXICON = {
    "attack", "blast", "bomb", "explosion", "dead", "killed", "injured", 
    "terror", "panic", "threat", "breach", "leak", "detected", "crash", 
    "ransomware", "malware", "phishing", "hacked", "stolen", "vulnerability", 
    "exploit", "critical", "compromised", "death", "murder", "casualty", 
    "fraud", "scam", "corrupt", "violation", "outage", "stabbing", "shooting"
}

def sentiment_score(corpus_text: str):
    txt = clean_text(corpus_text).lower()
    tokens = tokenize(txt)
    score = 0
    pos_hits, neg_hits = [], []
    for t in tokens:
        if t in POS_LEXICON:
            score += 1
            pos_hits.append(t)
        if t in NEG_LEXICON:
            score -= 1
            neg_hits.append(t)
            
    label = "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
    return {"label": label, "score": score, "positive_terms": sorted(set(pos_hits)), "negative_terms": sorted(set(neg_hits))}

THREAT_KEYWORDS = {
    "bomb", "blast", "explosion", "attack", "terror", "terrorist", "IED", 
    "shooting", "fire", "breach", "leak", "cyberattack", "malware", 
    "ransomware", "phishing", "ddos", "botnet", "hijack", "trojan", 
    "spyware", "keylogger", "vulnerability", "exploit", "zero-day", 
    "payload", "darkweb", "cartel", "smuggling", "naxal", "militant", "insurgent"
}
STRONG_TERMS = {
    "killed", "dead", "injured", "hostage", "suicide", "confirmed", 
    "suspect", "arrested", "terrorist", "assassination", "slain", 
    "kidnapped", "abducted", "casualties", "fatal", "massacre", 
    "critical", "breached", "stolen", "extortion", "ransom"
}

def threat_score(corpus_text: str):
    txt = clean_text(corpus_text).lower()
    tokens = tokenize(txt)
    score = 0
    found = {"threat_terms": [], "strong_terms": []}
    for t in tokens:
        if t in THREAT_KEYWORDS:
            score += 5
            found["threat_terms"].append(t)
        if t in STRONG_TERMS:
            score += 3
            found["strong_terms"].append(t)
            
    if score >= 20: level = "CRITICAL"
    elif score >= 10: level = "HIGH"
    elif score >= 4: level = "MEDIUM"
    elif score > 0: level = "LOW"
    else: level = "NONE"
    
    return {"score": score, "level": level, **{k: sorted(set(v)) for k, v in found.items()}}

def keywords_from_corpus(corpus_text: str, top_n: int = 20):
    tokens = tokenize(clean_text(corpus_text))
    tokens = [t for t in tokens if t not in EN_STOPWORDS and t not in TA_STOPWORDS and len(t) > 2]
    freq = Counter(tokens)
    return [t for t, c in freq.most_common(top_n)]

def analyze_corpus(items, text_fields=None):
    if text_fields is None:
        text_fields = ["translated_text", "original_text", "snippet", "title"]

    parts = []
    for it in items:
        item_texts = set() # Prevent adding identical original and translated text
        for key in text_fields:
            v = it.get(key)
            if v and str(v).strip() not in item_texts:
                item_texts.add(str(v).strip())
                parts.append(str(v).strip())
                
    corpus = " . ".join(parts)  
    corpus_clean = clean_text(corpus)

    # 1. Spacy NER + Regex IoCs
    ents = extract_entities_spacy(corpus_clean)
    iocs = extract_iocs(corpus_clean)
    ents.update(iocs) 

    # 2. TextRank Algorithmic Summary
    summary = summarize_textrank_math(corpus_clean, num_sentences=4)

    # 3. Core NLP Metrics
    kw = keywords_from_corpus(corpus_clean, top_n=25)
    sent = sentiment_score(corpus_clean)
    threat = threat_score(corpus_clean)

    total_tokens = len(tokenize(corpus_clean))
    unique_terms = len(set(tokenize(corpus_clean)))

    return {
        "summary": summary,
        "keywords": kw,
        "entities": ents,
        "sentiment": sent,
        "threat": threat,
        "stats": {"total_tokens": total_tokens, "unique_terms": unique_terms, "items_analyzed": len(items)}
    }
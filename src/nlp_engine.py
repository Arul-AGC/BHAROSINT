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

# --- Negation-Aware Weighted Sentiment Analysis ---

# Negation words: if any of these appear within 3 tokens before a
# sentiment word, the polarity flips.  "not a threat" → positive context.
NEGATORS = {"not", "no", "never", "neither", "nor", "none", "isn't",
            "wasn't", "weren't", "won't", "don't", "doesn't", "didn't",
            "can't", "cannot", "hardly", "barely", "without", "prevented",
            "averted", "stopped", "failed"}

# Weighted lexicons: not all words carry equal emotional weight.
# Scale: 1 = mild, 2 = moderate, 3 = strong
POS_LEXICON = {
    "good": 1, "safe": 1, "stable": 1, "positive": 1, "win": 1,
    "secure": 2, "recovered": 2, "resolved": 2, "released": 1,
    "protected": 2, "thriving": 2, "rescued": 3, "neutralized": 3,
    "prevented": 2, "healthy": 1, "growth": 1, "boom": 1,
    "praise": 1, "celebrate": 1, "improved": 1, "patched": 2,
    "arrested": 2, "captured": 2, "success": 2, "peace": 2,
}

NEG_LEXICON = {
    "attack": 2, "blast": 3, "bomb": 3, "explosion": 3,
    "dead": 3, "killed": 3, "injured": 2, "terror": 3,
    "panic": 1, "threat": 1, "breach": 2, "leak": 1,
    "detected": 1, "crash": 1, "ransomware": 2, "malware": 2,
    "phishing": 1, "hacked": 2, "stolen": 2, "vulnerability": 1,
    "exploit": 2, "critical": 1, "compromised": 2, "death": 3,
    "murder": 3, "casualty": 3, "fraud": 2, "scam": 2,
    "corrupt": 2, "violation": 2, "outage": 1, "stabbing": 3,
    "shooting": 3, "massacre": 3,
}

def _has_negation(tokens, index, window=3):
    """Check if any negation word appears within `window` tokens before index."""
    start = max(0, index - window)
    return any(tokens[j] in NEGATORS for j in range(start, index))


def sentiment_score(corpus_text: str):
    txt = clean_text(corpus_text).lower()
    tokens = tokenize(txt)
    score = 0
    pos_hits, neg_hits = [], []

    for i, t in enumerate(tokens):
        negated = _has_negation(tokens, i)

        if t in POS_LEXICON:
            weight = POS_LEXICON[t]
            if negated:
                score -= weight  # "not safe" → negative
                neg_hits.append(t)
            else:
                score += weight
                pos_hits.append(t)

        if t in NEG_LEXICON:
            weight = NEG_LEXICON[t]
            if negated:
                score += weight  # "not a threat" → positive
                pos_hits.append(t)
            else:
                score -= weight
                neg_hits.append(t)

    label = "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
    return {
        "label": label,
        "score": score,
        "positive_terms": sorted(set(pos_hits)),
        "negative_terms": sorted(set(neg_hits)),
    }


# --- Normalized Threat Scoring ---
# Scores are calculated per 1000 tokens to avoid inflating threat level
# on long documents.  A 5000-word article about cybersecurity shouldn't
# automatically score CRITICAL just because "attack" appears 50 times.

THREAT_KEYWORDS = {
    "bomb": 5, "blast": 5, "explosion": 5, "attack": 3,
    "terror": 5, "terrorist": 5, "IED": 5, "shooting": 4,
    "fire": 1, "breach": 3, "leak": 2, "cyberattack": 4,
    "malware": 3, "ransomware": 4, "phishing": 2, "ddos": 3,
    "botnet": 3, "hijack": 4, "trojan": 3, "spyware": 3,
    "keylogger": 3, "vulnerability": 2, "exploit": 3, "zero-day": 5,
    "payload": 3, "darkweb": 3, "cartel": 4, "smuggling": 3,
    "naxal": 4, "militant": 4, "insurgent": 4,
}
STRONG_TERMS = {
    "killed": 5, "dead": 5, "injured": 3, "hostage": 5,
    "suicide": 5, "confirmed": 1, "suspect": 1, "arrested": 1,
    "terrorist": 5, "assassination": 5, "slain": 5,
    "kidnapped": 5, "abducted": 5, "casualties": 4, "fatal": 4,
    "massacre": 5, "critical": 2, "breached": 3, "stolen": 2,
    "extortion": 4, "ransom": 4,
}

def threat_score(corpus_text: str):
    txt = clean_text(corpus_text).lower()
    tokens = tokenize(txt)
    raw_score = 0
    found = {"threat_terms": [], "strong_terms": []}

    for t in tokens:
        if t in THREAT_KEYWORDS:
            raw_score += THREAT_KEYWORDS[t]
            found["threat_terms"].append(t)
        if t in STRONG_TERMS:
            raw_score += STRONG_TERMS[t]
            found["strong_terms"].append(t)

    # Normalize to score per 1000 tokens
    token_count = max(len(tokens), 1)
    normalized = round((raw_score / token_count) * 1000, 1)

    if normalized >= 80:
        level = "CRITICAL"
    elif normalized >= 40:
        level = "HIGH"
    elif normalized >= 15:
        level = "MEDIUM"
    elif normalized > 0:
        level = "LOW"
    else:
        level = "NONE"

    return {
        "score": raw_score,
        "normalized_score": normalized,
        "tokens_analyzed": token_count,
        "level": level,
        **{k: sorted(set(v)) for k, v in found.items()},
    }

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
import pytest
from src.nlp_engine import sentiment_score, threat_score, extract_iocs

# ─── Sentiment Tests ──────────────────────────────────────────────

def test_sentiment_score_positive():
    text = "The rescue operation was a massive success, everyone is safe and protected."
    result = sentiment_score(text)

    assert result["label"] == "Positive"
    assert result["score"] > 0
    assert "safe" in result["positive_terms"]
    assert "success" in result["positive_terms"]

def test_sentiment_score_negative():
    text = "A critical vulnerability led to a horrific data breach, leaving users compromised."
    result = sentiment_score(text)

    assert result["label"] == "Negative"
    assert result["score"] < 0
    assert "breach" in result["negative_terms"]
    assert "vulnerability" in result["negative_terms"]

def test_sentiment_negation_flips_negative():
    """'not a threat' should NOT score as negative — the negation flips it."""
    text = "This is not a threat and there is no attack happening."
    result = sentiment_score(text)
    # Both 'threat' and 'attack' are negated, so they should flip to positive
    assert result["score"] >= 0

def test_sentiment_negation_flips_positive():
    """'not safe' should score as negative."""
    text = "The system is not safe and not secure at all."
    result = sentiment_score(text)
    assert result["score"] < 0

def test_sentiment_weighted_scoring():
    """A massacre (weight=3) should score worse than a crash (weight=1)."""
    mild = sentiment_score("there was a small crash")
    severe = sentiment_score("there was a terrible massacre")
    assert severe["score"] < mild["score"]


# ─── Threat Tests ─────────────────────────────────────────────────

def test_threat_score_normalized():
    """Threat score should be normalized by corpus length."""
    result = threat_score("bomb explosion attack killed dead")
    # 5 tokens total, high density of threat terms → high normalized score
    assert result["normalized_score"] > 0
    assert "tokens_analyzed" in result
    assert result["level"] in ("HIGH", "CRITICAL")

def test_threat_score_diluted_in_long_text():
    """A single 'attack' in a 200-word article shouldn't be CRITICAL."""
    padding = " ".join(["technology"] * 200)
    text = f"There was an attack reported. {padding}"
    result = threat_score(text)
    # One threat word in 200+ tokens → low normalized score
    assert result["level"] in ("LOW", "MEDIUM", "NONE")

def test_threat_score_critical():
    text = "Terrorist attack confirmed. Hostage situation with 5 dead after massive bomb explosion."
    result = threat_score(text)
    assert result["level"] in ("HIGH", "CRITICAL")
    assert "bomb" in result["threat_terms"]
    assert "dead" in result["strong_terms"]


# ─── IoC Tests ────────────────────────────────────────────────────

def test_extract_iocs():
    text = """
    The suspect's IP was 192.168.1.100.
    He exploited CVE-2023-41234 using a payload with
    MD5 hash 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d.
    """

    iocs = extract_iocs(text)
    assert "192.168.1.100" in iocs["IP Addresses"]
    assert "CVE-2023-41234" in iocs["CVE Vulnerabilities"]
    assert "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d" in iocs["MD5/SHA256 Hashes"]

def test_extract_iocs_empty():
    """No IoCs in a clean text should return empty lists."""
    iocs = extract_iocs("The weather is nice today in Delhi.")
    assert iocs["IP Addresses"] == []
    assert iocs["CVE Vulnerabilities"] == []
    assert iocs["MD5/SHA256 Hashes"] == []

import pytest
from src.nlp_engine import sentiment_score, threat_score, extract_iocs

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

def test_threat_score_critical():
    text = "Terrorist attack confirmed. Hostage situation with 5 dead after massive bomb explosion."
    result = threat_score(text)
    
    # 5 pts for threat keywords (attack, bomb, explosion, terror) => 20
    # 3 pts for strong keywords (dead, hostage, confirmed) => 9
    # Total score should be around 29, which is way past the 20 criteria for CRITICAL
    assert result["level"] == "CRITICAL"
    assert result["score"] >= 20
    assert "bomb" in result["threat_terms"]
    assert "dead" in result["strong_terms"]

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

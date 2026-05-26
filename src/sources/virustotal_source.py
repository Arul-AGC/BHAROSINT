# src/sources/virustotal_source.py
"""
VirusTotal API integration.
Allows searching for domains, IPs, or hashes to retrieve threat intelligence.
"""

import requests
from src.config import CFG
from src.logger import get_logger

log = get_logger("virustotal")

def search_virustotal(query: str, search_type: str = "domain") -> list:
    """
    Query VirusTotal. 
    search_type can be 'domain', 'ip', or 'hash'.
    """
    api_key = CFG.get("api_keys", {}).get("virustotal", "")
    
    if not api_key:
        log.warning("VirusTotal API key not found in config.yaml. Skipping VT recon.")
        return []
        
    log.info("Querying VirusTotal for %s: %s", search_type, query[:50])
    
    headers = {
        "x-apikey": api_key
    }
    
    endpoint = ""
    if search_type == "domain":
        endpoint = f"https://www.virustotal.com/api/v3/domains/{query}"
    elif search_type == "ip":
        endpoint = f"https://www.virustotal.com/api/v3/ip_addresses/{query}"
    elif search_type == "hash":
        endpoint = f"https://www.virustotal.com/api/v3/files/{query}"
    else:
        log.error("Invalid VT search type: %s", search_type)
        return []

    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
        
        if resp.status_code == 404:
            log.debug("No records found on VirusTotal for %s", query)
            return []
            
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("attributes", {})
        
        stats = data.get("last_analysis_stats", {})
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0)
        
        reputation = data.get("reputation", 0)
        
        title = f"VT Report: {query}"
        snippet = f"Malicious: {malicious} | Suspicious: {suspicious} | Undetected: {undetected} | Reputation: {reputation}"
        
        return [{
            "source": "VirusTotal",
            "platform": "virustotal",
            "title": title,
            "snippet": snippet,
            "link": f"https://www.virustotal.com/gui/{search_type}/{query}",
            "malicious_hits": malicious
        }]
        
    except requests.exceptions.RequestException as e:
        log.error("VirusTotal API Error: %s", e)
        return []
    except Exception as e:
        log.error("Unexpected error during VirusTotal search: %s", e)
        return []

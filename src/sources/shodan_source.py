# src/sources/shodan_source.py
"""
Shodan API integration.
Allows searching for exposed infrastructure (e.g. IPs, webcams, databases)
associated with a query or keyword.
"""

import shodan
from src.config import CFG
from src.logger import get_logger

log = get_logger("shodan")

def search_shodan(query: str, limit: int = 5) -> list:
    """Query Shodan for exposed devices and infrastructure."""
    api_key = CFG.get("api_keys", {}).get("shodan", "")
    
    if not api_key:
        log.warning("Shodan API key not found in config.yaml. Skipping Shodan recon.")
        return []

    try:
        api = shodan.Shodan(api_key)
        log.info("Querying Shodan for: %s", query[:50])
        # We only request the first page of results to save credits
        results = api.search(query, limit=limit)
        
        parsed = []
        for match in results.get("matches", [])[:limit]:
            ip = match.get("ip_str", "")
            port = match.get("port", "")
            org = match.get("org", "Unknown Org")
            os = match.get("os", "Unknown OS")
            hostnames = match.get("hostnames", [])
            data = match.get("data", "")[:200]
            
            title = f"{ip}:{port} ({org})"
            snippet = f"OS: {os} | Hostnames: {', '.join(hostnames)} | Banner: {data.strip()}"
            
            parsed.append({
                "source": "Shodan",
                "platform": "shodan",
                "title": title,
                "snippet": snippet,
                "link": f"https://www.shodan.io/host/{ip}",
                "ip": ip,
            })
            
        log.debug("Shodan returned %d results", len(parsed))
        return parsed
        
    except shodan.APIError as e:
        log.error("Shodan API Error: %s", e)
        return []
    except Exception as e:
        log.error("Unexpected error during Shodan search: %s", e)
        return []

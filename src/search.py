import requests
from bs4 import BeautifulSoup

def duckduckgo_search(query, max_results=5):
    """Simple DuckDuckGo scraping wrapper"""
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select(".result__a")

    results = []
    for link in links[:max_results]:
        title = link.get_text()
        href = link.get("href")
        results.append({"title": title, "url": href})
    return results

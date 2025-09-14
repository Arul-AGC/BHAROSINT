import requests
from bs4 import BeautifulSoup
from rich.console import Console
from urllib.parse import unquote, urlparse, parse_qs

console = Console()

def duckduckgo_search(query, max_results=5):
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error fetching results!")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    # Grab result titles + links
    for a in soup.select(".result__a", limit=max_results):
        title = a.get_text()
        link = a["href"]
        
        if "uddg=" in link:
            link = unquote(link.split("uddg=")[1].split("&")[0])
        results.append({"title": title, "link": link})

    return results

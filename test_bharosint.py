import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

def duckduckgo_search(query, num_results=5):
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36"
    }

    response = requests.post(url, data=params, headers=headers)

    if response.status_code != 200:
        console.print(f"[red]Error fetching results! Status: {response.status_code}[/red]")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = [a.get("href") for a in soup.select("a.result__a", limit=num_results)]
    return links


if __name__ == "__main__":
    console.print("[bold green]BHAROSINT Test Search[/bold green]")
    keyword = "Traditional Foods in Tamil Nadu"
    results = duckduckgo_search(keyword)

    if results:
        console.print(f"[cyan]Top {len(results)} results for '{keyword}':[/cyan]")
        for i, link in enumerate(results, 1):
            console.print(f"[yellow]{i}.[/yellow] {link}")
    else:
        console.print("[red]No results found[/red]")

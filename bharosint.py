from bharosint_lang import regional_search
from src.search import duckduckgo_search
from rich.console import Console

console = Console()

def main_menu():
    console.print("[bold cyan]\n--- BHAROSINT Main Menu ---[/bold cyan]")
    console.print("1. English Search")
    console.print("2. Regional Language Search")
    console.print("3. Exit\n")

    choice = input("Enter choice: ")

    if choice == "1":
        query = input("Enter search query in English: ")
        results = duckduckgo_search(query)
        console.print(f"\n[green]Results for {query}[/green]")
        for r in results:
            console.print(f"- {r['title']} | {r['url']}")
    elif choice == "2":
        query = input("Enter query (English or Indic): ")
        regional_search(query)
    else:
        console.print("[red]Exiting...[/red]")

if __name__ == "__main__":
    main_menu()

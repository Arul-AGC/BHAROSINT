from rich.table import Table
from rich.console import Console

console = Console()

def deduplicate_results(results):
    seen = set()
    unique = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)
    return unique

def pretty_table(results):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Title (original)")
    table.add_column("Title (EN)")
    table.add_column("URL")

    for r in results:
        table.add_row(
            r.get("title", ""),
            r.get("translated_title", ""),
            r.get("url", "")
        )

    console.print(table)

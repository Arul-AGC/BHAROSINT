# src/utils.py
from rich.table import Table
from rich.console import Console
from rich import box
from urllib.parse import urlparse

console = Console()

def normalize_url(url: str) -> str:
    """Normalize URLs by removing trailing slashes and query fragments."""
    if not url:
        return ""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

def deduplicate_results(results):
    """Remove duplicate URLs from the search results list."""
    seen = set()
    unique = []
    for r in results:
        url = normalize_url(r.get("url", ""))
        if url and url not in seen:
            seen.add(url)
            r["url"] = url
            unique.append(r)
    return unique

def pretty_table(results):
    """Print a formatted results table using Rich."""
    if not results:
        console.print("[yellow]⚠️ No results found.[/yellow]")
        return

    table = Table(
        title="🌐 BHAROSINT Search Results",
        show_header=True,
        header_style="bold cyan",
        box=box.MINIMAL_DOUBLE_HEAD,
    )

    table.add_column("Title (Original)", style="bold white", no_wrap=False)
    table.add_column("Title (EN Translation)", style="green", no_wrap=False)
    table.add_column("URL", style="blue", overflow="fold")

    for r in results:
        table.add_row(
            r.get("title", "—"),
            r.get("translated_title", "—"),
            r.get("url", "—")
        )

    console.print(table)
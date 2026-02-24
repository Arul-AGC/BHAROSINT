# src/formatter.py
from typing import List, Dict
import textwrap

try:
    from rich.console import Console
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.text import Text
    import rich.box 
    console = Console()
    _HAVE_RICH = True
except Exception:
    _HAVE_RICH = False
    console = None

def display_social_results(items: List[Dict], title: str = "Social Media Results"):
    if not items:
        if _HAVE_RICH:
            console.print(f"\n[bold yellow]⚠️ No social media results found.[/]")
        else:
            print("No social media results found.")
        return

    if _HAVE_RICH:
        # Use MINIMAL box to prevent Unicode/URL width shattering
        table = Table(
            show_header=True, 
            header_style="bold cyan", 
            title=f"\n[bold green]{title}[/]",
            expand=True, 
            box=rich.box.MINIMAL, 
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Source", style="bold", width=10)
        table.add_column("Author", overflow="fold", ratio=1)
        table.add_column("When", width=12)
        table.add_column("Text", overflow="fold", ratio=3)
        table.add_column("URL", overflow="fold", ratio=2, style="deep_sky_blue1")

        for i, it in enumerate(items, 1):
            source = it.get("source", "Unknown")
            author = it.get("author") or "-"
            date = it.get("date") or "-"
            text = it.get("translated_text") or it.get("original_text") or "-"
            url = it.get("url") or "-"
            
            table.add_row(str(i), source, author, str(date), text, url)

        console.print(table)

        # Replaced rigid Panels with sleek horizontal rules
        for i, it in enumerate(items, 1):
            source = it.get('source') or 'Unknown'
            author = it.get('author') or '-'
            console.rule(f"[bold blue]{i}. \\[{source}] {author}[/]", style="dim")
            
            orig = it.get("original_text", "")
            trans = it.get("translated_text", "")
            url = it.get("url", "N/A")
            
            if orig and trans and orig != trans:
                console.print(f"[bold]Original:[/] {orig}")
                console.print(f"[bold]Translated:[/] {trans}")
            else:
                console.print(f"[bold]Text:[/] {trans or orig}")
                
            console.print(f"[bold]URL:[/] [deep_sky_blue1]{url}[/]\n")
    else:
        print(f"=== {title} ===")
        for i, it in enumerate(items, 1):
            print(f"{i}. [{it.get('source')}]")
            print(f"   Author: {it.get('author') or 'N/A'}")
            print(f"   Date: {it.get('date') or 'N/A'}")
            print(f"   Translated: {it.get('translated_text') or it.get('original_text') or 'N/A'}")
            print(f"   URL: {it.get('url') or 'N/A'}")
            print("")


def display_search_results(items: List[Dict], title: str = "Search Results"):
    if not items:
        if _HAVE_RICH:
            console.print(f"\n[bold yellow]⚠️ No search results found.[/]")
        else:
            print("No search results found.")
        return

    if _HAVE_RICH:
        table = Table(
            show_header=True, 
            header_style="bold cyan", 
            title=f"\n[bold green]{title}[/]", 
            expand=True, 
            box=rich.box.MINIMAL, 
        )
        
        table.add_column("#", style="dim", width=4)
        table.add_column("Lang", width=8)
        table.add_column("Title", overflow="fold", ratio=2) 
        table.add_column("Link", overflow="fold", ratio=2, style="deep_sky_blue1") 

        for i, r in enumerate(items, 1):
            lang = r.get("lang", "-")
            title_text = r.get("title", r.get("snippet", "") ) or "-"
            link_text = r.get("link") or "-"
            table.add_row(str(i), str(lang), title_text, link_text)

        console.print(table)

        # Replace rigid panels with horizontal rules
        for i, r in enumerate(items, 1):
            console.rule(f"[dim]{i}. Result[/]", style="dim")
            
            title_txt = r.get('title') or r.get('snippet') or '-'
            console.print(f"[bold]Title:[/] {title_txt}")
            
            if r.get("snippet"):
                console.print(f"[bold]Snippet:[/] {r.get('snippet')}")
                
            link = r.get('link') or '-'
            console.print(f"[bold]Link:[/] [deep_sky_blue1]{link}[/]")
            
            if r.get("lang"):
                console.print(f"[bold]Lang:[/] {r.get('lang')}\n")
    else:
        print(f"=== {title} ===")
        for i, r in enumerate(items, 1):
            print(f"{i}. [{r.get('lang','-')}] {r.get('title') or r.get('snippet','-')}")
            print(f"   Link: {r.get('link') or 'N/A'}")
            print("")


def display_nlp_analysis(analysis: Dict):
    if not analysis:
        if _HAVE_RICH:
            console.print("\n[bold yellow]⚠️ NLP Analysis data is empty.[/]")
        else:
            print("NLP Analysis data is empty.")
        return

    if _HAVE_RICH:
        # Replaced the main enclosing panel with a strong header rule
        console.rule("\n[bold cyan]=== NLP ANALYSIS (CORPUS) ===[/]\n", style="cyan")

        # 1. Summary
        summary = analysis.get("summary") or "(no summary)"
        console.print("[bold green]Summary[/]")
        console.print(f"{summary}\n")

        # 2. Keywords
        keywords = ", ".join(analysis.get("keywords", [])) or "-"
        console.print("[bold green]Top Keywords[/]")
        console.print(f"{keywords}\n")

        # 3. Sentiment & Threat (Stacked instead of side-by-side to prevent squeezing)
        sentiment = analysis.get("sentiment", {})
        threat = analysis.get("threat", {})
        
        sent_label = sentiment.get('label', 'N/A')
        sent_score = sentiment.get('score', 0)
        sent_color = "green" if sent_score > 0 else "red" if sent_score < 0 else "yellow"
        
        console.print(f"[bold green]Sentiment[/]: [{sent_color}]{sent_label} (Score: {sent_score})[/]")
        console.print(f"[dim]Positive Terms:[/] {', '.join(sentiment.get('positive_terms', [])) or 'none'}")
        console.print(f"[dim]Negative Terms:[/] {', '.join(sentiment.get('negative_terms', [])) or 'none'}\n")
        
        threat_label = threat.get('level', 'N/A')
        threat_score = threat.get('score', 0)
        threat_color = "red" if threat_label == "CRITICAL" else "yellow" if threat_label in ["HIGH", "MEDIUM"] else "green"
        
        console.print(f"[bold green]Threat / Risk[/]: [{threat_color}]{threat_label} (Score: {threat_score})[/]")
        console.print(f"[dim]Threat Terms:[/] {', '.join(threat.get('threat_terms', [])) or 'none'}")
        console.print(f"[dim]Strong Terms:[/] {', '.join(threat.get('strong_terms', [])) or 'none'}\n")

        # 4. Entities
        entities = analysis.get("entities", {})
        ent_table = Table(
            title="[bold green]Entities[/]", 
            show_header=True, 
            header_style="bold magenta", 
            expand=True, 
            box=rich.box.MINIMAL, 
        )
        
        ent_table.add_column("Type", style="cyan", ratio=1)
        ent_table.add_column("Items", style="white", overflow="fold", ratio=5)
        
        for etype, items in entities.items():
            if items:
                ent_table.add_row(etype.capitalize(), ", ".join(items))
            else:
                ent_table.add_row(etype.capitalize(), "-")
        console.print(ent_table)
        print("\n")

        # 5. Stats
        stats = analysis.get("stats", {})
        console.print("[bold green]Stats[/]")
        console.print(f"Items Analyzed: {stats.get('items_analyzed', 0)}")
        console.print(f"Total Tokens:   {stats.get('total_tokens', 0)}")
        console.print(f"Unique Terms:   {stats.get('unique_terms', 0)}\n")

    else:
        print("\n=== NLP ANALYSIS (CORPUS) ===\n")
        
        print("--- Summary ---")
        summary = analysis.get("summary") or "(no summary)"
        print("\n".join(textwrap.wrap(summary, width=80)))
        
        print("\n--- Top Keywords ---")
        keywords = ", ".join(analysis.get("keywords", [])) or "-"
        print("\n".join(textwrap.wrap(keywords, width=80)))
        
        print("\n--- Sentiment ---")
        sent = analysis.get("sentiment", {})
        print(f"  Label: {sent.get('label', 'N/A')} (Score: {sent.get('score', 0)})")
        print(f"  Positive Terms: {', '.join(sent.get('positive_terms', [])) or '-'}")
        print(f"  Negative Terms: {', '.join(sent.get('negative_terms', [])) or '-'}")

        print("\n--- Threat / Risk ---")
        threat = analysis.get("threat", {})
        print(f"  Level: {threat.get('level', 'N/A')} (Score: {threat.get('score', 0)})")
        print(f"  Threat Terms: {', '.join(threat.get('threat_terms', [])) or '-'}")
        print(f"  Strong Terms: {', '.join(threat.get('strong_terms', [])) or '-'}")

        print("\n--- Entities ---")
        ents = analysis.get("entities", {})
        for etype, items in ents.items():
            print(f"  {etype.capitalize()}:")
            if items:
                print("    " + "\n    ".join(textwrap.wrap(", ".join(items), width=70)))
            else:
                print("    -")
        
        print("\n--- Stats ---")
        stats = analysis.get("stats", {})
        print(f"  Items Analyzed: {stats.get('items_analyzed', 0)}")
        print(f"  Total Tokens: {stats.get('total_tokens', 0)}")
        print(f"  Unique Terms: {stats.get('unique_terms', 0)}")
        
        print("\n=== END OF ANALYSIS ===\n")
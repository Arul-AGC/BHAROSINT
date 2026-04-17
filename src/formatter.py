# src/formatter.py
"""
Terminal output formatter for BHAROSINT.

Design principles:
  - No giant tables (they shatter on narrow terminals and with long URLs)
  - Compact card-style blocks with proper wrapping
  - Intelligent truncation with full info preserved where it matters
  - Color-coded badges for languages and threat levels
  - Rich Panels for NLP analysis sections
"""

from typing import List, Dict
import textwrap

try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.columns import Columns
    from rich import box
    console = Console()
    _HAVE_RICH = True
except Exception:
    _HAVE_RICH = False
    console = None

# ─── Helpers ──────────────────────────────────────────────────────────────

LANG_COLORS = {
    "English": "bright_white",
    "Hindi": "bright_yellow",
    "Tamil": "bright_green",
    "Telugu": "bright_cyan",
    "Malayalam": "bright_magenta",
    "Bengali": "bright_red",
    "Twitter": "cyan",
    "Reddit": "dark_orange",
}

def _lang_badge(lang: str) -> str:
    """Return a Rich markup badge for a language/source."""
    color = LANG_COLORS.get(lang, "white")
    return f"[{color}]⟪{lang}⟫[/]"

def _trunc(text: str, max_len: int = 120) -> str:
    """Truncate text cleanly at word boundary."""
    if not text:
        return ""
    text = text.replace("\n", " ").replace("\r", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + " …"

def _trunc_url(url: str, max_len: int = 70) -> str:
    """Shorten URL for display while keeping it recognizable."""
    if not url:
        return "-"
    url = url.strip()
    if len(url) <= max_len:
        return url
    # Keep the domain + start of path, clip the rest
    return url[:max_len - 1] + "…"

def _wrap_text(text: str, width: int = 80, indent: str = "  ") -> str:
    """Wrap long text with indentation for readability."""
    if not text:
        return ""
    text = text.replace("\n", " ").replace("\r", " ").strip()
    lines = textwrap.wrap(text, width=width)
    return ("\n" + indent).join(lines)

# ─── Search Results ───────────────────────────────────────────────────────

def display_search_results(items: List[Dict], title: str = "Search Results"):
    if not items:
        if _HAVE_RICH:
            console.print(f"\n[bold yellow]⚠️  No search results found.[/]\n")
        else:
            print("\nNo search results found.\n")
        return

    count = len(items)

    if _HAVE_RICH:
        console.print()
        console.rule(f"[bold cyan]🔍 {title}[/]  [dim]({count} results)[/]", style="cyan")
        console.print()

        for i, r in enumerate(items, 1):
            lang = r.get("lang", "-")
            title_text = r.get("title") or r.get("snippet") or "-"
            snippet = r.get("snippet", "")
            link = r.get("link") or "-"

            # ── Number + Language badge ──
            header = f"[bold white]{i:>3}.[/]  {_lang_badge(lang)}"

            # ── Title (bold, wrapped) ──
            title_line = f"  [bold]{_trunc(title_text, 140)}[/]"

            # ── Snippet (dim, wrapped, only if different from title) ──
            snippet_line = ""
            if snippet and snippet != title_text:
                snippet_line = f"\n  [dim]{_trunc(snippet, 160)}[/]"

            # ── URL (cyan, truncated) ──
            url_line = f"\n  [deep_sky_blue1]{_trunc_url(link, 80)}[/]"

            console.print(f"{header}\n{title_line}{snippet_line}{url_line}")
            if i < count:
                console.print("[dim]  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─[/]")

        console.print()
    else:
        print(f"\n=== {title} ({count} results) ===\n")
        for i, r in enumerate(items, 1):
            lang = r.get("lang", "-")
            title_text = r.get("title") or r.get("snippet") or "-"
            link = r.get("link") or "-"
            print(f"  {i:>3}. [{lang}]")
            print(f"       {_trunc(title_text, 100)}")
            print(f"       {_trunc_url(link, 80)}")
            print()


# ─── Social Media Results ─────────────────────────────────────────────────

def display_social_results(items: List[Dict], title: str = "Social Media Results"):
    if not items:
        if _HAVE_RICH:
            console.print(f"\n[bold yellow]⚠️  No social media results found.[/]\n")
        else:
            print("\nNo social media results found.\n")
        return

    count = len(items)

    if _HAVE_RICH:
        console.print()
        console.rule(f"[bold cyan]📡 {title}[/]  [dim]({count} posts)[/]", style="cyan")
        console.print()

        for i, it in enumerate(items, 1):
            source = it.get("source", "Unknown")
            author = it.get("author") or "anonymous"
            orig = it.get("original_text", "")
            trans = it.get("translated_text", "")
            url = it.get("url", "")

            # ── Header: number + source badge + author ──
            header = f"[bold white]{i:>3}.[/]  {_lang_badge(source)}  [dim italic]@{author}[/]"

            # ── Content ──
            content_lines = []
            if orig and trans and orig.strip() != trans.strip():
                content_lines.append(f"  [dim]Original:[/]    {_trunc(orig, 140)}")
                content_lines.append(f"  [bold]Translated:[/]  {_trunc(trans, 140)}")
            else:
                text = trans or orig or "-"
                content_lines.append(f"  {_trunc(text, 160)}")

            # ── URL ──
            if url:
                content_lines.append(f"  [deep_sky_blue1]{_trunc_url(url, 80)}[/]")

            console.print(header)
            console.print("\n".join(content_lines))
            if i < count:
                console.print("[dim]  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─[/]")

        console.print()
    else:
        print(f"\n=== {title} ({count} posts) ===\n")
        for i, it in enumerate(items, 1):
            source = it.get("source", "Unknown")
            text = it.get("translated_text") or it.get("original_text") or "-"
            url = it.get("url") or "-"
            print(f"  {i:>3}. [{source}]")
            print(f"       {_trunc(text, 100)}")
            print(f"       {_trunc_url(url, 80)}")
            print()


# ─── NLP Analysis ─────────────────────────────────────────────────────────

def display_nlp_analysis(analysis: Dict):
    if not analysis:
        if _HAVE_RICH:
            console.print("\n[bold yellow]⚠️  NLP Analysis data is empty.[/]\n")
        else:
            print("\nNLP Analysis data is empty.\n")
        return

    if _HAVE_RICH:
        console.print()
        console.rule("[bold cyan]🧠 NLP ANALYSIS (CORPUS)[/]", style="cyan")
        console.print()

        # ── 1. Summary Panel ──
        summary = analysis.get("summary") or "(no summary)"
        summary_wrapped = _wrap_text(summary, width=90, indent="  ")
        console.print(Panel(
            f"[white]{summary_wrapped}[/]",
            title="[bold green]📋 Summary[/]",
            border_style="green",
            padding=(1, 2),
            expand=True,
        ))

        # ── 2. Keywords (as inline tags) ──
        keywords = analysis.get("keywords", [])
        if keywords:
            tags = "  ".join(f"[on grey11] [cyan]{kw}[/] [/]" for kw in keywords)
            console.print(Panel(
                tags,
                title="[bold green]🔑 Top Keywords[/]",
                border_style="green",
                padding=(1, 2),
                expand=True,
            ))

        # ── 3. Sentiment + Threat side by side ──
        sentiment = analysis.get("sentiment", {})
        threat = analysis.get("threat", {})

        # Sentiment card
        sent_label = sentiment.get("label", "N/A")
        sent_score = sentiment.get("score", 0)
        sent_color = "green" if sent_score > 0 else "red" if sent_score < 0 else "yellow"
        pos = ", ".join(sentiment.get("positive_terms", [])) or "none"
        neg = ", ".join(sentiment.get("negative_terms", [])) or "none"

        sent_text = Text()
        sent_text.append("Verdict:  ", style="bold")
        sent_text.append(f"{sent_label} ({sent_score:+d})\n", style=f"bold {sent_color}")
        sent_text.append("⊕ ", style="green")
        sent_text.append(f"{_trunc(pos, 60)}\n", style="dim green")
        sent_text.append("⊖ ", style="red")
        sent_text.append(f"{_trunc(neg, 60)}", style="dim red")

        sent_panel = Panel(
            sent_text,
            title="[bold green]💬 Sentiment[/]",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )

        # Threat card
        threat_level = threat.get("level", "NONE")
        threat_score_val = threat.get("score", 0)
        t_color = "bold red" if threat_level == "CRITICAL" else "yellow" if threat_level in ("HIGH", "MEDIUM") else "green"
        t_terms = ", ".join(threat.get("threat_terms", [])) or "none"
        s_terms = ", ".join(threat.get("strong_terms", [])) or "none"

        thr_text = Text()
        thr_text.append("Level:    ", style="bold")
        thr_text.append(f"{threat_level} (Score: {threat_score_val})\n", style=t_color)
        thr_text.append("Threats:  ", style="dim")
        thr_text.append(f"{_trunc(t_terms, 60)}\n", style="dim red")
        thr_text.append("Strong:   ", style="dim")
        thr_text.append(f"{_trunc(s_terms, 60)}", style="dim red")

        thr_panel = Panel(
            thr_text,
            title="[bold green]⚠️  Threat / Risk[/]",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )

        # Print side-by-side if terminal is wide enough, else stacked
        term_width = console.width or 80
        if term_width >= 100:
            console.print(Columns([sent_panel, thr_panel], equal=True, expand=True))
        else:
            console.print(sent_panel)
            console.print(thr_panel)

        # ── 4. Entities Table (compact) ──
        entities = analysis.get("entities", {})
        has_entities = any(bool(v) for v in entities.values())

        if has_entities:
            ent_table = Table(
                title="[bold green]🏷️  Entities[/]",
                show_header=True,
                header_style="bold magenta",
                expand=True,
                box=box.ROUNDED,
                border_style="dim",
                padding=(0, 1),
            )
            ent_table.add_column("Type", style="bold cyan", width=16)
            ent_table.add_column("Items", style="white", overflow="fold")

            for etype, eitems in entities.items():
                if eitems:
                    # Wrap long entity lists
                    items_str = _trunc(", ".join(str(e) for e in eitems), 200)
                    ent_table.add_row(etype.replace("_", " ").title(), items_str)

            console.print(ent_table)

        # ── 5. Stats (compact single line) ──
        stats = analysis.get("stats", {})
        stats_line = (
            f"[dim]Items Analyzed:[/] [bold]{stats.get('items_analyzed', 0)}[/]"
            f"  │  [dim]Tokens:[/] [bold]{stats.get('total_tokens', 0)}[/]"
            f"  │  [dim]Unique:[/] [bold]{stats.get('unique_terms', 0)}[/]"
        )
        console.print(Panel(
            stats_line,
            title="[bold green]📊 Stats[/]",
            border_style="dim green",
            padding=(0, 2),
            expand=True,
        ))
        console.print()

    else:
        # ── Plain text fallback ──
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
            print(f"  {etype.replace('_', ' ').title()}:")
            if items:
                print("    " + "\n    ".join(textwrap.wrap(", ".join(str(e) for e in items), width=70)))
            else:
                print("    -")

        print("\n--- Stats ---")
        stats = analysis.get("stats", {})
        print(f"  Items Analyzed: {stats.get('items_analyzed', 0)}")
        print(f"  Total Tokens: {stats.get('total_tokens', 0)}")
        print(f"  Unique Terms: {stats.get('unique_terms', 0)}")

        print("\n=== END OF ANALYSIS ===\n")
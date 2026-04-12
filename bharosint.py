# bharosint.py
"""
BHAROSINT v2 — Multilingual Open Source Intelligence Framework

Supports both interactive menu mode and non-interactive CLI mode.

Usage:
    Interactive:   python bharosint.py
    CLI:           python bharosint.py -q "cyber attacks india" -m search -e json
    Help:          python bharosint.py --help
"""

import argparse
import sys

from bharosint_lang import regional_search, regional_search_results
from src.social_scraper import collect_social_data
from src.nlp_engine import analyze_corpus
from src.formatter import display_search_results, display_social_results, display_nlp_analysis
from src.graph_engine_tui import display_interactive_map
from src.exporter import export_results

# --------------------------------------------------
# ASCII Banner — keep the brand identity
# --------------------------------------------------

BANNER = r"""
______ _   _   ___  ______ _____ _____ _____ _   _ _____ 
| ___ \ | | | / _ \ | ___ \  _  /  ___|_   _| \ | |_   _|
| |_/ / |_| |/ /_\ \| |_/ / | | \ `--.  | | |  \| | | |  
| ___ \  _  ||  _  ||    /| | | |`--. \ | | | . ` | | |  
| |_/ / | | || | | || |\ \ \_/ /\__/ /_| |_| |\  | | |  
\____/\_| |_/\_| |_/\_| \_|\___/\____/ \___/\_| \_/ \_/  

    🗡️  Open Source OSINT Framework (BHAROSINT v2) 🗡️
"""

# --------------------------------------------------
# Core Operations (reusable by both CLI and menu)
# --------------------------------------------------

def run_search(query: str) -> list:
    """Execute multilingual web search. Returns list of result dicts."""
    print(f"\n[+] Searching multiple languages for: {query}\n")
    results = regional_search_results(query)
    return results


def run_social(query: str) -> list:
    """Execute social media intelligence gathering. Returns list of result dicts."""
    print(f"\n[+] Gathering multilingual social media content for: {query}\n")
    data = collect_social_data(query)
    return data if data else []


def run_analysis(results: list) -> dict:
    """Run NLP analysis on a result set. Returns analysis dict."""
    print("[+] Running combined corpus-level NLP on results...\n")
    analysis = analyze_corpus(results)
    return analysis


def handle_export(results: list, analysis, query: str, fmt: str, output_dir: str):
    """Export results to file and print confirmation."""
    try:
        filepath = export_results(results, analysis, query, fmt, output_dir)
        print(f"\n[✓] Exported {fmt.upper()} report → {filepath}")
    except Exception as e:
        print(f"\n[!] Export failed: {e}")


# --------------------------------------------------
# CLI Mode (argparse)
# --------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser.

    Design note: We use optional arguments (--query) rather than positional ones.
    Why? Because OSINT queries often have spaces and special characters.
    With positional args, users would need careful quoting. With --query "...",
    the intent is always clear regardless of what the query contains.
    """
    parser = argparse.ArgumentParser(
        prog="bharosint",
        description="BHAROSINT v2 — Multilingual OSINT Framework for Indian Subcontinent Intelligence",
        epilog=(
            "Examples:\n"
            '  python bharosint.py -q "cyber attacks india" -m search\n'
            '  python bharosint.py -q "APT groups" -m social -e csv\n'
            '  python bharosint.py -q "ransomware" -m all -e html -o ./my_reports\n'
            "  python bharosint.py                (interactive menu)\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-q", "--query",
        type=str,
        default=None,
        help="Search query (required for CLI mode, omit for interactive menu)"
    )
    parser.add_argument(
        "-m", "--mode",
        type=str,
        choices=["search", "social", "analyze", "map", "all"],
        default="search",
        help="Operation mode (default: search)"
    )
    parser.add_argument(
        "-e", "--export",
        type=str,
        choices=["json", "csv", "html"],
        default=None,
        help="Export format (optional — results are always displayed in terminal)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="reports",
        help="Output directory for exports (default: reports/)"
    )

    return parser


def cli_mode(args):
    """
    Non-interactive CLI execution.

    This runs a single operation and exits — perfect for scripting,
    cron jobs, or piping output to other tools.
    """
    print(BANNER)
    query = args.query
    mode = args.mode
    results = []
    analysis = None

    try:
        # --- Determine what to run based on mode ---
        if mode in ("search", "all"):
            results = run_search(query)
            display_search_results(results, title="Web Search Results (Regional + English)")

        if mode in ("social", "all"):
            social_data = run_social(query)
            display_social_results(social_data, title="Social Media Intelligence Results")
            # Merge social results into the main result set for analysis
            if mode == "all":
                results.extend(social_data)
            else:
                results = social_data

        if mode in ("analyze", "all"):
            if not results:
                # If mode is 'analyze' standalone, we need to search first
                print("[+] No prior results — running web search first...\n")
                results = run_search(query)
                display_search_results(results, title="Web Search Results (Regional + English)")

            if results:
                analysis = run_analysis(results)
                display_nlp_analysis(analysis)
            else:
                print("[!] No results available to analyze.\n")

        if mode == "map":
            if not results:
                results = run_search(query)
            if results:
                analysis = run_analysis(results)
                display_interactive_map(analysis, query=query)
            else:
                print("[!] No results available to map.\n")

        # --- Handle export if requested ---
        if args.export and results:
            # If analysis wasn't computed but we're exporting, run it for richer exports
            if analysis is None and args.export == "html":
                analysis = run_analysis(results)
            handle_export(results, analysis, query, args.export, args.output)
        elif args.export and not results:
            print("[!] No results to export.\n")

    except KeyboardInterrupt:
        print("\n[!] Interrupted. Exiting.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        sys.exit(1)


# --------------------------------------------------
# Interactive Menu Mode (original behavior, enhanced)
# --------------------------------------------------

def main_menu():
    """Interactive menu for manual OSINT sessions."""
    print(BANNER)

    last_results = []
    last_analysis = None
    last_query = "TARGET"

    while True:
        print("""
[ MAIN MENU ]
1. Web Search (Regional + English)
2. Social Media Intelligence (Multilingual)
3. Run Combined NLP on last results (corpus-level)
4. View Threat Map (Terminal Interactive Graph)
5. Export last results (JSON / CSV / HTML)
6. Exit
""")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            query = input("Enter search query: ").strip()
            if not query:
                print("[!] Empty query. Try again.\n")
                continue
            last_query = query
            last_analysis = None  # Reset analysis when new data arrives
            try:
                last_results = run_search(query)
                display_search_results(last_results, title="Web Search Results (Regional + English)")
            except Exception as e:
                print(f"[!] Regional search failed: {e}\n")
                last_results = []

        elif choice == "2":
            query = input("Enter social media query: ").strip()
            if not query:
                print("[!] Empty query. Try again.\n")
                continue
            last_query = query
            last_analysis = None
            try:
                data = run_social(query)
                if data:
                    last_results = data
                    display_social_results(last_results, title="Social Media Intelligence Results")
                else:
                    print("[!] No social results found.")
                    last_results = []
            except Exception as e:
                print(f"[!] Social media scrape failed: {e}\n")
                last_results = []

        elif choice == "3":
            if not last_results:
                print("[!] No results available to analyze. First run a search or social scrape.\n")
                continue
            try:
                last_analysis = run_analysis(last_results)
                display_nlp_analysis(last_analysis)
            except Exception as e:
                print(f"[!] NLP Analysis failed: {e}\n")

        elif choice == "4":
            if not last_results:
                print("[!] No results available to map. First run a search or social scrape.\n")
                continue
            print("[+] Synthesizing node graph physics data...\n")
            try:
                last_analysis = run_analysis(last_results)
                display_interactive_map(last_analysis, query=last_query)
            except Exception as e:
                print(f"[!] Threat Map rendering failed: {e}\n")

        elif choice == "5":
            if not last_results:
                print("[!] No results available to export. First run a search or social scrape.\n")
                continue
            print("\nExport format:")
            print("  1. JSON")
            print("  2. CSV")
            print("  3. HTML (styled intelligence report)")
            fmt_choice = input("Choose format (1/2/3): ").strip()

            fmt_map = {"1": "json", "2": "csv", "3": "html"}
            fmt = fmt_map.get(fmt_choice)
            if not fmt:
                print("[!] Invalid format choice.\n")
                continue

            output_dir = input("Output directory (Enter for 'reports/'): ").strip() or "reports"

            # Auto-run analysis for HTML exports if not already done
            if fmt == "html" and last_analysis is None:
                print("[+] Running NLP analysis for the report...\n")
                try:
                    last_analysis = run_analysis(last_results)
                except Exception as e:
                    print(f"[!] NLP analysis failed: {e}")
                    last_analysis = None

            handle_export(last_results, last_analysis, last_query, fmt, output_dir)

        elif choice == "6":
            print("Exiting BHAROSINT. Goodbye!")
            break

        else:
            print("Invalid choice, try again!")


# --------------------------------------------------
# Entrypoint — decides between CLI and interactive
# --------------------------------------------------

def main():
    """
    The entrypoint logic:
    - If any arguments are passed → CLI mode
    - If no arguments → interactive menu
    
    This is checked by looking at sys.argv. When you run 'python bharosint.py',
    sys.argv is ['bharosint.py'] (length 1, just the script name).
    When you run 'python bharosint.py --query xyz', sys.argv has more items.
    """
    parser = build_parser()

    # If no CLI arguments supplied, launch interactive menu
    if len(sys.argv) == 1:
        main_menu()
        return

    args = parser.parse_args()

    # If --query is missing in CLI mode, it's an error
    if not args.query:
        parser.error("--query / -q is required in CLI mode. Run without arguments for interactive menu.")

    cli_mode(args)


if __name__ == "__main__":
    main()
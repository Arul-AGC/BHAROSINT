# bharosint.py

from bharosint_lang import regional_search, regional_search_results
from src.social_scraper import collect_social_data
from src.nlp_engine import analyze_corpus
from src.formatter import display_search_results, display_social_results, display_nlp_analysis
from src.graph_engine_tui import display_interactive_map

# -------------------------------
# Main Menu
# -------------------------------

def main_menu():
    print(r"""
______ _   _   ___  ______ _____ _____ _____ _   _ _____ 
| ___ \ | | | / _ \ | ___ \  _  /  ___|_   _| \ | |_   _|
| |_/ / |_| |/ /_\ \| |_/ / | | \ `--.  | | |  \| | | |  
| ___ \  _  ||  _  ||    /| | | |`--. \ | | | . ` | | |  
| |_/ / | | || | | || |\ \ \_/ /\__/ /_| |_| |\  | | |  
\____/\_| |_/\_| |_/\_| \_|\___/\____/ \___/\_| \_/ \_/  

    🗡️  Open Source OSINT Framework (BHAROSINT v2) 🗡️
    """)


    last_results = []
    last_query = "TARGET"
    while True:
        print("""
[ MAIN MENU ]
1. Web Search (Regional + English)
2. Social Media Intelligence (Multilingual)
3. Run Combined NLP on last results (corpus-level)
4. View Threat Map (Terminal Interactive Graph)
5. Exit
""")
        choice = input("Enter your choice: ")

        if choice == "1":
            query = input("Enter search query: ")
            last_query = query
            print(f"\n[+] Searching multiple languages for: {query}\n")
            try:
                last_results = regional_search_results(query)
                display_search_results(last_results, title="Web Search Results (Regional + English)")
            except Exception as e:
                print(f"[!] Regional search failed: {e}\n")
                last_results = []
        
        elif choice == "2":
            query = input("Enter social media query: ")
            last_query = query
            print(f"\n[+] Gathering multilingual social media content for: {query}\n")
            try:
                data = collect_social_data(query)
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
            print("[+] Running combined corpus-level NLP on last results...\n")
            try:
                analysis = analyze_corpus(last_results)
                display_nlp_analysis(analysis)
            except Exception as e:
                print(f"[!] NLP Analysis failed: {e}\n")
        elif choice == "4":
            if not last_results:
                print("[!] No results available to map. First run a search or social scrape.\n")
                continue
            
            print("[+] Synthesizing node graph physics data...\n")
            try:
                analysis = analyze_corpus(last_results)
                display_interactive_map(analysis, query=last_query)
            except Exception as e:
                print(f"[!] Threat Map rendering failed: {e}\n")
        elif choice == "5":
            print("Exiting BHAROSINT. Goodbye!")
            break
        else:
            print("Invalid choice, try again!")

if __name__ == "__main__":
    main_menu()
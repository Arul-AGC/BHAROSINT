# bharosint.py
import sys
from colorama import Fore, Style, init
from src.search import duckduckgo_search

# Initialize colorama
init(autoreset=True)

def banner():
    print(Fore.CYAN + Style.BRIGHT + """
______ _   _   ___  ______ _____ _____ _____ _   _ _____ 
| ___ \ | | | / _ \ | ___ \  _  /  ___|_   _| \ | |_   _|
| |_/ / |_| |/ /_\ \| |_/ / | | \ `--.  | | |  \| | | |  
| ___ \  _  ||  _  ||    /| | | |`--. \ | | | . ` | | |  
| |_/ / | | || | | || |\ \\ \_/ /\__/ /_| |_| |\  | | |  
\____/\_| |_/\_| |_/\_| \_|\___/\____/ \___/\_| \_/ \_/  
                                                         
                                                          
    🗡️  Open Source OSINT Framework (BHAROSINT v1) 🗡️
    """)

def main_menu():
    while True:
        print(Fore.YELLOW + "\n[ MAIN MENU ]")
        print(Fore.GREEN + "1. Web Search (DuckDuckGo)")
        print(Fore.GREEN + "2. Exit")

        choice = input(Fore.CYAN + "\nEnter your choice: ")

        if choice == "1":
            query = input(Fore.MAGENTA + "Enter search query: ")
            print(Fore.WHITE + "\n[+] Searching DuckDuckGo for:", query)
            results = duckduckgo_search(query)
            if results:
                print(Fore.GREEN + f"\n[+] Found {len(results)} results:\n")
                for idx, result in enumerate(results, 1):
                    print(Fore.YELLOW + f"{idx}. {result['title']}")
                    print(Fore.CYAN + f"   {result['link']}\n")

            else:
                print(Fore.RED + "\n[!] No results found.")
        
        elif choice == "2":
            print(Fore.RED + "\nExiting BHAROSINT... Stay safe! 🕵️")
            sys.exit()
        else:
            print(Fore.RED + "Invalid choice, try again!")

if __name__ == "__main__":
    banner()
    main_menu()


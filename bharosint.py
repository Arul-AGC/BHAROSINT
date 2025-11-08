from colorama import Fore, Style, init
from bharosint_lang import regional_search

init(autoreset=True)

def banner():
    print(Fore.CYAN + Style.BRIGHT + r"""
______ _   _   ___  ______ _____ _____ _____ _   _ _____ 
| ___ \ | | | / _ \ | ___ \  _  /  ___|_   _| \ | |_   _|
| |_/ / |_| |/ /_\ \| |_/ / | | \ `--.  | | |  \| | | |  
| ___ \  _  ||  _  ||    /| | | |`--. \ | | | . ` | | |  
| |_/ / | | || | | || |\ \ \_/ /\__/ /_| |_| |\  | | |  
\____/\_| |_/\_| |_/\_| \_|\___/\____/ \___/\_| \_/ \_/  

    🗡️  Open Source OSINT Framework (BHAROSINT v1) 🗡️
""")

def main_menu():
    while True:
        print(Fore.MAGENTA + "\n[ MAIN MENU ]")
        print(Fore.YELLOW + "1. Web Search (Regional + English)")
        print(Fore.YELLOW + "2. Exit")

        choice = input(Fore.CYAN + "\nEnter your choice: ")

        if choice == "1":
            query = input(Fore.GREEN + "Enter search query: ")
            print(Fore.CYAN + f"\n[+] Searching multiple languages for: {query}\n")
            results = regional_search(query, max_results=5)

            if results:
                print(Fore.GREEN + f"[+] Found {len(results)} unique results:\n")
                for i, r in enumerate(results, 1):
                    print(Fore.YELLOW + f"{i}. {r['title']}")
                    print(Fore.CYAN + f"   {r['link']}\n")
            else:
                print(Fore.RED + "[!] No results found.")
        elif choice == "2":
            print(Fore.CYAN + "Exiting BHAROSINT. Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid choice, try again!")

if __name__ == "__main__":
    banner()
    main_menu()

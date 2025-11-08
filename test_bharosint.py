from bharosint_lang import regional_search

print("BHAROSINT Test Search\n")
query = input("Enter query: ")

results = regional_search(query, max_results=5)
if results:
    for r in results:
        print(f"- {r['title']}\n  {r['link']}\n")
else:
    print("No results found.")

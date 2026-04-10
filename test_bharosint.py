from bharosint_lang import regional_search_results

print("BHAROSINT Test Search\n")
query = input("Enter query: ")

results = regional_search_results(query)
if results:
    for r in results:
        print(f"- {r['title']}\n  {r['link']}\n")
else:
    print("No results found.")

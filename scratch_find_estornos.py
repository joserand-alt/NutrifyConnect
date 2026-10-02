import re

with open("transactions_debug.txt", "r", encoding="utf-8") as f:
    text = f.read()

# find all occurrences of "estorno" (case insensitive)
estorno_matches = re.findall(r'.*estorno.*', text, re.IGNORECASE)
print(f"Total lines matching 'estorno': {len(estorno_matches)}")
for m in estorno_matches:
    print(" ", m)

# Let's also check if there are other reversal keywords like "devolução", "cancelamento", "reembolso"
for kw in ["devolu", "cancel", "reembolso", "estorn"]:
    matches = re.findall(rf'.*{kw}.*', text, re.IGNORECASE)
    print(f"\nKeyword '{kw}': {len(matches)} matches")
    for m in matches:
        print(" ", m)

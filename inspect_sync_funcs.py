with open('template.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("--- Pos 326500 to 327500 (getSync24hData) ---")
print(content[326500:327500].encode('ascii', 'replace').decode('ascii'))

print("\n--- Pos 534700 to 537500 (Modal JS handlers) ---")
print(content[534700:537500].encode('ascii', 'replace').decode('ascii'))

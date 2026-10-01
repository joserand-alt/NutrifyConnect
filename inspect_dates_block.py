with open('gerador.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("--- Lines around 102500 - 105000 ---")
print(content[102500:105200].encode('ascii', 'replace').decode('ascii'))

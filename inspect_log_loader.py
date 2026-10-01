with open('gerador.py', 'r', encoding='utf-8') as f:
    content = f.read()

print(content[9500:15000].encode('ascii', 'replace').decode('ascii'))

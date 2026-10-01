with open('gerador.py', 'r', encoding='utf-8') as f:
    content = f.read()

pos = content.find('fetch_logs_from_api')
print("--- fetch_logs_from_api call context in gerador.py ---")
print(content[pos-1000:pos+3000].encode('ascii', 'replace').decode('ascii'))

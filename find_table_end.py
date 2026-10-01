with open('template.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("--- Content around 542000 to 545000 ---")
print(content[542000:545000].encode('ascii', 'replace').decode('ascii'))

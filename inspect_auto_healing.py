with open('gerador.py', 'r', encoding='utf-8') as f:
    content = f.read()

pos = content.find('# AUTO-HEALING DE CURSOS:')
print(content[pos:pos+3000].encode('ascii', 'replace').decode('ascii'))

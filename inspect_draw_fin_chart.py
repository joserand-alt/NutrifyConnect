with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_dfc = tmpl.find('function _drawFinChart')
print("=== _drawFinChart snippet ===")
print(tmpl[pos_dfc:pos_dfc+2500].encode('ascii', 'replace').decode('ascii'))

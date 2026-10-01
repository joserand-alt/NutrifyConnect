with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

g1_start = tmpl.find('<!-- G1')
g2_start = tmpl.find('<!-- G2')

print(tmpl[g1_start:g2_start].encode('ascii', 'replace').decode('ascii'))

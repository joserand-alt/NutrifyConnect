with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_glob = tmpl.find('const globalHistorico = [];')
if pos_glob == -1:
    pos_glob = tmpl.find('const globalProjecao = [];')
if pos_glob == -1:
    pos_glob = tmpl.find('global:')

print("=== computeUnifiedFinancialDataset global assembly ===")
print(tmpl[pos_glob-200:pos_glob+3000].encode('ascii', 'replace').decode('ascii'))

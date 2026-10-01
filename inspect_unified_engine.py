with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_u = tmpl.find('function computeUnifiedFinancialDataset')
print("computeUnifiedFinancialDataset at:", pos_u)
if pos_u != -1:
    print(tmpl[pos_u:pos_u+3500].encode('ascii', 'replace').decode('ascii'))

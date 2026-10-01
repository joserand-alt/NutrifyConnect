with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_u = tmpl.find('function computeUnifiedFinancialDataset')
print("=== computeUnifiedFinancialDataset core calculation ===")
print(tmpl[pos_u+1500:pos_u+6500].encode('ascii', 'replace').decode('ascii'))

with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_u = tmpl.find('function computeUnifiedFinancialDataset')
pos_vsubs = tmpl.find('vSubs.forEach', pos_u)

print("=== vSubs loop in computeUnifiedFinancialDataset ===")
print(tmpl[pos_vsubs-200:pos_vsubs+2500].encode('ascii', 'replace').decode('ascii'))

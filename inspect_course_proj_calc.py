with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_u = tmpl.find('function computeUnifiedFinancialDataset')
pos_g = tmpl.find('globalObj.projecao_mensal =', pos_u)

print("=== computeUnifiedFinancialDataset course projections loop ===")
print(tmpl[pos_g-3500:pos_g].encode('ascii', 'replace').decode('ascii'))

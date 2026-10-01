with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_u = tmpl.find('function computeUnifiedFinancialDataset')
pos_c = tmpl.find('cm.proj_1m = cm.projecao_mensal', pos_u)

print("=== computeUnifiedFinancialDataset cm.projecao_mensal building ===")
print(tmpl[pos_c-3000:pos_c].encode('ascii', 'replace').decode('ascii'))

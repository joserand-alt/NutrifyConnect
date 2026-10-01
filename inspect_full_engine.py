with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_u = tmpl.find('function computeUnifiedFinancialDataset')
pos_u_end = tmpl.find('function drawFinanceiro', pos_u)

print("=== computeUnifiedFinancialDataset complete code ===")
print(tmpl[pos_u:pos_u_end].encode('ascii', 'replace').decode('ascii'))

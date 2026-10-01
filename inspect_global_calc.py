with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

pos_u = tmpl.find('function computeUnifiedFinancialDataset')
pos_ret = tmpl.find('return { courses: coursesMap, global: globalObj };', pos_u)

print("=== computeUnifiedFinancialDataset before return ===")
print(tmpl[pos_ret-3000:pos_ret+100].encode('ascii', 'replace').decode('ascii'))

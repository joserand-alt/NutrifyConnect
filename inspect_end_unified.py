template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('computeUnifiedFinancialDataset')
idx_next = text.find('function drawFinanceiro', idx)
print('End of computeUnifiedFinancialDataset (lines before drawFinanceiro):')
print(text[idx_next-600:idx_next].encode('ascii', 'replace').decode('ascii'))

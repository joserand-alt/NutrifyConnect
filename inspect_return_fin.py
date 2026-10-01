template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function computeUnifiedFinancialDataset')
if idx != -1:
    idx_end = text.find('function', idx + 50)
    print('End of computeUnifiedFinancialDataset:')
    print(text[idx_end-400:idx_end])

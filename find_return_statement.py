template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('computeUnifiedFinancialDataset')
idx_ret = text.find('return ', idx + 100)
while idx_ret != -1 and idx_ret < idx + 15000:
    print('Found return at:', text[idx_ret-50:idx_ret+150].replace('\n', ' '))
    idx_ret = text.find('return ', idx_ret + 10)

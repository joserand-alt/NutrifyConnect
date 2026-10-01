template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'function\s+([a-zA-Z0-9_]*Money[a-zA-Z0-9_]*)', text)
print('Money functions in template.html:', matches)

idx_fM = text.find('const fM =')
while idx_fM != -1:
    print('fM definition:', text[idx_fM:idx_fM+120])
    idx_fM = text.find('const fM =', idx_fM + 10)

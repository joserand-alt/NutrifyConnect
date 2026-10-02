with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'function _renderCaixaKpiCards\(resumo\)\s*\{.*?\}', text, re.DOTALL)
if m:
    print("Found _renderCaixaKpiCards:\n", m.group(0))

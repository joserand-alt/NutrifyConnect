with open('vindi_service.py', 'r', encoding='utf-8') as f:
    vindi_code = f.read()

import re
matches = [m.start() for m in re.finditer(r'projecao_mensal_map', vindi_code)]
print("projecao_mensal_map occurrences:", len(matches))
for p in matches:
    print(vindi_code[p-100:p+200])

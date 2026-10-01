template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'G2\s*[-–—]', text, re.IGNORECASE)
for m in matches:
    idx = m.start()
    print('Found G2 at char:', idx)
    print(text[idx-50:idx+1500].encode('ascii', 'replace').decode('ascii'))

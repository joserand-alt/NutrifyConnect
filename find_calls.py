template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'(\w+\(\);)', text)
print('Top level calls found in script:')
for line_no, line in enumerate(text.splitlines(), 1):
    if line.strip().endswith('();') or 'addEventListener' in line:
        print(f"{line_no}: {line.strip().encode('ascii', 'replace').decode('ascii')}")

with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
scripts = re.findall(r'<script>([\s\S]*?)</script>', html)
for i, s in enumerate(scripts):
    print(f'Script block {i}: length {len(s)}')
    for line in s.split('\n'):
        if 'selectTab' in line or 'switchTab' in line or 'tab' in line:
            print('  ', line.strip()[:100])

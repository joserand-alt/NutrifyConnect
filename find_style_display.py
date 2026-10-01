with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
for m in re.finditer(r'style\.display\s*=', html):
    start = max(0, m.start() - 60)
    end = min(len(html), m.end() + 60)
    print(html[start:end].replace('\n', ' '))
    print('---')

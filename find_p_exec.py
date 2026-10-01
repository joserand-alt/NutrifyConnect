with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = [m.start() for m in re.finditer(r'#p-exec|\.panel', html)]
for idx in matches:
    print(html[idx-30:idx+80].replace('\n', ' '))
    print('---')

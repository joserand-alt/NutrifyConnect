with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'MONITORAMENTO AO VIVO', text, re.I)]
for i, m in enumerate(matches):
    with open(f'match_{i+1}.txt', 'w', encoding='utf-8') as out:
        out.write(text[m-200:m+800])
    print(f"Wrote match_{i+1}.txt")

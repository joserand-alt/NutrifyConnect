with open('gerador.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'data_insc', content)]
print("data_insc positions:", matches)

for p in matches:
    print("--- AT POS", p, "---")
    print(content[max(0, p-100):min(len(content), p+200)].encode('ascii', 'replace').decode('ascii'))

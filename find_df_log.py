with open('gerador.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'df_log', content)]
print("df_log positions:", len(matches))

for p in matches[:10]:
    print("--- AT POS", p, "---")
    print(content[max(0, p-100):min(len(content), p+200)].encode('ascii', 'replace').decode('ascii'))

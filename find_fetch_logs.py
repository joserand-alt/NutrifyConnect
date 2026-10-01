with open('gerador.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'fetch_logs_from_api', content)]
print("fetch_logs_from_api positions:", matches)

for p in matches:
    print("--- AT POS", p, "---")
    print(content[max(0, p-200):min(len(content), p+500)].encode('ascii', 'replace').decode('ascii'))

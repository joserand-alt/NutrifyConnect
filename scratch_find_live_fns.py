with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'function drawHomeView|function renderLive|renderAuditoria|matriculas24h|matriculas30d', text, re.I)]
for i, m in enumerate(matches):
    print(f"Match {i+1} at {m}: {text[m:m+120]}")

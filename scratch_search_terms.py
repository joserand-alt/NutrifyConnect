import re

with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

for term in ['p-exec', 'p-home', 'p-fin', 'p-curso', 'class="panel', 'class=\'panel', 'id="p-', 'id=\'p-']:
    matches = [m.start() for m in re.finditer(re.escape(term), text)]
    print(f"Term '{term}': {len(matches)} occurrences")
    for pos in matches[:3]:
        print(f"  snippet: {text[max(0, pos-50):pos+100]}")

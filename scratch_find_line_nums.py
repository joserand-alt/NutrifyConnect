with open('template.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if 'id="p-fin"' in l:
        print(f"p-fin starts at line {i}: {l.strip()}")
    if '</section>' in l and i > 2500 and i < 3500:
        print(f"section end around line {i}: {l.strip()}")

for i, l in enumerate(lines, 1):
    if '<nav class="tabs"' in l or 'id="btn-tab-fin"' in l:
        print(f"nav at line {i}: {l.strip()}")

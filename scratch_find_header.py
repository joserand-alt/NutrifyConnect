import re

with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'<header|<nav|class=[\"\'](?:top|nav|header|brand|title)', text, re.I)]
for m in matches[:6]:
    print('--- MATCH AT', m, '---')
    print(text[m:m+250])

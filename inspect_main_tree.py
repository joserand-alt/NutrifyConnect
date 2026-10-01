import re

with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

main_idx = html.find('<main class="hud-main-content">')
main_end = html.find('</main>')
main_content = html[main_idx:main_end]

# Find all section tags and direct divs
lines = main_content.split('\n')
for i, line in enumerate(lines):
    if '<section' in line or '</section>' in line or 'id="p-' in line:
        print(f'{i+1}: {line.strip()[:100]}')

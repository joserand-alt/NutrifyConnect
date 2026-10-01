with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
styles = re.findall(r'<style>([\s\S]*?)</style>', html)
for i, s in enumerate(styles):
    print(f'=== Style {i} ===')
    for line in s.split('\n'):
        line_s = line.strip()
        if any(w in line_s for w in ['height', 'margin', 'padding', 'position', 'min-height', 'top', 'transform']) and '{' in line_s:
            print(line_s[:120])

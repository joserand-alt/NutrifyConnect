with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
styles = re.findall(r'<style>([\s\S]*?)</style>', html)
for i, s in enumerate(styles):
    for m in re.finditer(r'([^{}]*?\.panel[^{}]*?)\{([^}]*?)\}', s):
        print(f'Style {i} Selector:', m.group(1).strip())
        print('  Rules:', m.group(2).strip()[:100])

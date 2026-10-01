with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's find all occurrences of .panel in CSS
import re
css_blocks = re.findall(r'<style>([\s\S]*?)</style>', html)
all_css = '\n'.join(css_blocks)

for m in re.finditer(r'([^{}]*panel[^{}]*)\{([^}]*)\}', all_css, re.IGNORECASE):
    print('Selector:', m.group(1).strip())
    print('Rules:', m.group(2).strip())
    print('---')

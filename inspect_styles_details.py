with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's inspect where .panel is defined in CSS and all overrides
import re
styles = re.findall(r'<style>([\s\S]*?)</style>', html)
for i, s in enumerate(styles):
    print(f'Style block {i}: length {len(s)}')
    # check for any height, min-height, margin, position on panel or hud-main-content
    for line in s.split('\n'):
        if any(k in line for k in ['hud-main-content', 'panel', 'exec-hero', 'global-filter-bar']):
            print('  ', line.strip()[:100])

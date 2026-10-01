import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8-sig') as f:
    text = f.read()

pos_style_end = text.find('</style>')
pos_script = text.find('<script>', pos_style_end)
html = text[pos_style_end+8:pos_script]

# Find header, panels, and major divs
for m in re.finditer(r'<(header|nav|div\s+class="[^"]*"|div\s+id="[^"]*")[^>]*>', html):
    line = m.group(0)
    if any(k in line for k in ['panel', 'header', 'filter', 'kpis', 'live', 'wrap', 'nav', 'tab']):
        print(line[:100])

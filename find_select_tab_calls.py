import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8-sig') as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'selectTab\s*\(', text)]
for m in matches:
    print(repr(text[m:m+50]))

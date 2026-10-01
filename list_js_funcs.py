import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8-sig') as f:
    text = f.read()

funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', text)
print("JavaScript functions found:")
for fn in sorted(set(funcs)):
    if any(k in fn.lower() for k in ['chart', 'draw', 'render', 'kpi', 'live', 'curso', 'fin', 'tab']):
        print(" ", fn)

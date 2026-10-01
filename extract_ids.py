import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8-sig') as f:
    text = f.read()

ids = set(re.findall(r'id=["\']([^"\']+)["\']', text))
js_ids = set(re.findall(r'getElementById\(["\']([^"\']+)["\']\)', text))

print(f"Total HTML IDs: {len(ids)}")
print(f"Total JS referenced IDs: {len(js_ids)}")
print("Key containers:")
for i in sorted(js_ids):
    if any(k in i.lower() for k in ['tab', 'home', 'exec', 'curso', 'fin', 'live', 'filter', 'kpi', 'origem']):
        print(" ", i)

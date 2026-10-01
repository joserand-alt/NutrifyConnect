import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's search for "1014.0" in the HTML string and print the surrounding 200 chars
for m in re.finditer(r'1014\.0', html):
    start = max(0, m.start() - 100)
    end = min(len(html), m.end() + 100)
    print("MATCH at", m.start(), ":")
    print(repr(html[start:end]))
    print("-" * 50)

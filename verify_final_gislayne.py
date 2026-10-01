import json
from datetime import datetime, timedelta

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])

students = data.get('students', [])

for s in students:
    if 'gislayne' in (s.get('email') or '').lower():
        print(f"Gislayne: {s.get('nome')} | Email: {s.get('email')} | data_insc: {s.get('data_insc')} | Curso: {s.get('curso')}")

now = datetime(2026, 9, 18, 17, 30)
t24h = now - timedelta(hours=24)
t30d = now - timedelta(days=30)

def parse_d(d_str):
    if not d_str:
        return None
    try:
        parts = d_str.split('/')
        return datetime(int(parts[2]), int(parts[1]), int(parts[0]))
    except:
        return None

list_24h = [s for s in students if parse_d(s.get('data_insc') or '') and parse_d(s.get('data_insc') or '') >= t24h]
list_30d = [s for s in students if parse_d(s.get('data_insc') or '') and parse_d(s.get('data_insc') or '') >= t30d]

print(f"\nTotal Students in DATA with data_insc in 24h: {len(list_24h)}")
print(f"Total Students in DATA with data_insc in 30d: {len(list_30d)}")

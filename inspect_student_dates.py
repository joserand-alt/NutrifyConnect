import json
import re

with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const DATA\s*=\s*(\{.*?\});', html, re.DOTALL)
data = json.loads(m.group(1))

students = data.get('students', [])
print(f'Total students: {len(students)}')

sample_dates = []
date_fields_count = {}
for s in students[:50]:
    row = {k: v for k, v in s.items() if any(d in k.lower() for d in ['data', 'date', 'insc', 'criac', 'created', 'matric', 'primeiro', 'first'])}
    sample_dates.append(row)

for s in students:
    for k in s.keys():
        if any(d in k.lower() for d in ['data', 'date', 'insc', 'criac', 'created', 'matric', 'primeiro', 'first']):
            date_fields_count[k] = date_fields_count.get(k, 0) + 1

print('Date fields found across all students:', date_fields_count)
print('Sample student date records (first 5):')
for r in sample_dates[:5]:
    print(r)

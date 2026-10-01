import json
import re

with open('dashboard_gerado.html', 'r', encoding='utf-8') as f:
    content = f.read()

# find rawEstudantes or rawData
m1 = content.find('const DATA = {')
m2 = content.find('};\n', m1)
if m1 != -1 and m2 != -1:
    data = json.loads(content[m1+13:m2+1])
    students = data.get('students', [])
else:
    # try find last closing brace before script end
    idx = content.find('const DATA = ') + len('const DATA = ')
    idx_end = content.find('</script>', idx)
    raw = content[idx:idx_end].strip()
    if raw.endswith(';'):
        raw = raw[:-1]
    data = json.loads(raw)
    students = data.get('students', [])

print(f"Total students parsed: {len(students)}")

luizas = [s for s in students if 'luizafrigini' in (s.get('email') or '').lower()]
print(f"\n--- LUIZA ({len(luizas)} entries) ---")
for l in luizas:
    print(f"Name: {l.get('nome')}, Email: {l.get('email')}, Curso: {l.get('curso')}, Data: {l.get('data_insc')}, Status: {l.get('status')}, Aulas: {l.get('total_aulas')}")

anas = [s for s in students if 'analuizaccavalari' in (s.get('email') or '').lower()]
print(f"\n--- ANA LUIZA ({len(anas)} entries) ---")
for a in anas:
    print(f"Name: {a.get('nome')}, Email: {a.get('email')}, Curso: {a.get('curso')}, Data: {a.get('data_insc')}, Status: {a.get('status')}, Aulas: {a.get('total_aulas')}")

future_students = [s for s in students if any(yr in str(s.get('data_insc', '')) for yr in ['2027', '2028', '2029'])]
print(f"\nStudents with future date (data_insc): {len(future_students)}")

# Check duplicate (email, curso)
dups = {}
for s in students:
    key = ((s.get('email') or '').strip().lower(), (s.get('curso') or '').strip().lower())
    dups[key] = dups.get(key, 0) + 1

duplicate_entries = {k: v for k, v in dups.items() if v > 1 and k[0]}
print(f"\nDuplicate (email, curso) pairs: {len(duplicate_entries)}")
if duplicate_entries:
    print("Duplicates:", duplicate_entries)

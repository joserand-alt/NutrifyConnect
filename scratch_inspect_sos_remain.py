import json
from scratch_test_correction import corrected_students

with open('cativa_cache.json', 'r', encoding='utf-8') as f:
    c_data = json.load(f)
c_students = c_data.get('students', []) if isinstance(c_data, dict) else c_data

cativa_by_email = {}
for s in c_students:
    em = (s.get('email') or '').lower().strip()
    courses = [c.get('courseName') for c in s.get('courses', [])]
    cativa_by_email[em] = courses

sos_remain = [s for s in corrected_students if s.get('curso_novo') == 'S.O.S ANTIBIOTICO']
print(f'Total de SOS restantes: {len(sos_remain)}')
for s in sos_remain[:30]:
    em = (s.get('email') or '').lower().strip()
    c_courses = cativa_by_email.get(em, [])
    events = [e.get('item') or e.get('acao') for e in s.get('events', []) if isinstance(e, dict)][:5]
    print(f"- {s.get('nome')} | email: {em} | Cativa: {c_courses} | Events: {events}")

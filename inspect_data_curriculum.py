import json
import re

with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const DATA\s*=\s*(\{.*?\});', html, re.DOTALL)
if not m:
    m = re.search(r'window\.RAW_DATA\s*=\s*(\{.*?\});', html, re.DOTALL)

data = json.loads(m.group(1))

print('DATA keys:', list(data.keys()))
curric = data.get('curriculum', {})
print('Curriculum keys / length:', len(curric), list(curric.keys()))

students = data.get('students', [])
print('Students count:', len(students))
st_courses = {}
for s in students:
    c = s.get('curso')
    st_courses[c] = st_courses.get(c, 0) + 1
print('Student courses in DATA:', st_courses)

modules = data.get('modules', {})
print('Modules keys / length:', len(modules), list(modules.keys()) if isinstance(modules, dict) else len(modules))

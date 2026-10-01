import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print("Vindi KPIs:", json.dumps(data.get('financeiro', {}).get('kpis'), indent=2))
    print("Asaas KPIs:", json.dumps(data.get('financeiro_asaas', {}).get('kpis'), indent=2))
    print("Funil KPIs:", json.dumps(data.get('funil', {}).get('kpis'), indent=2))
    
    # Students summary:
    students = data.get('students', [])
    statuses = {}
    vindi_statuses = {}
    for s in students:
        st = s.get('status', 'Unknown')
        statuses[st] = statuses.get(st, 0) + 1
        vs = s.get('vindi_status', 'Unknown')
        vindi_statuses[vs] = vindi_statuses.get(vs, 0) + 1
    print("Statuses:", statuses)
    print("Vindi Statuses:", vindi_statuses)
    
    # Courses
    courses = data.get('courses', [])
    print(f"Total courses: {len(courses)}")
    for c in courses[:5]:
        print("Course sample:", c.get('name') or c.get('curso') or c)

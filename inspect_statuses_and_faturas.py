import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    
    # Check student statuses
    students = data.get('students', [])
    print(f"Total students in DATA: {len(students)}")
    statuses = {}
    for s in students:
        st = s.get('status')
        statuses[str(st)] = statuses.get(str(st), 0) + 1
    print("Raw students statuses in DATA:", statuses)
    
    # Check Vindi faturas
    v_fat = data.get('financeiro', {}).get('faturas_tabela', [])
    print(f"\nVindi faturas count: {len(v_fat)}")
    v_st = {}
    v_cursos = {}
    for f in v_fat:
        st = f.get('status')
        c = f.get('curso')
        v_st[str(st)] = v_st.get(str(st), 0) + 1
        v_cursos[str(c)] = v_cursos.get(str(c), 0) + 1
    print("Vindi faturas statuses:", v_st)
    print("Vindi faturas top cursos:", list(v_cursos.items())[:6])
    
    # Check Asaas faturas
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])
    print(f"\nAsaas faturas count: {len(a_fat)}")
    a_st = {}
    a_cursos = {}
    for f in a_fat:
        st = f.get('status')
        c = f.get('curso')
        a_st[str(st)] = a_st.get(str(st), 0) + 1
        a_cursos[str(c)] = a_cursos.get(str(c), 0) + 1
    print("Asaas faturas statuses:", a_st)
    print("Asaas faturas top cursos:", list(a_cursos.items())[:6])

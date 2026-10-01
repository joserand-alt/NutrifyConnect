import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi_cache = json.load(f)

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas_cache = json.load(f)

# Load students from dashboard
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

import re
m = re.search(r'const DATA = (.*?);\s*const CURRENT_DATA', html_text, re.DOTALL)
data = json.loads(m.group(1))

st_list = data.get('students', [])
print(f"Total students in dataset: {len(st_list)}")

sos_students = []
for s in st_list:
    c = str(s.get('curso', '')).upper()
    if 'ANTIBIOT' in c or 'SOS' in c or 'S.O.S' in c:
        sos_students.append(s)

print(f"\nStudents with course matching SOS Antibiótico: {len(sos_students)}")
for s in sos_students:
    print(f"\nNome: {s.get('nome')} | Email: {s.get('email')} | Curso: {s.get('curso')} | Status: {s.get('status')} | Acessou: {s.get('acessou')}")
    em = (s.get('email') or '').lower().strip()
    
    # Check in Vindi
    v_st = s.get('vindi')
    if v_st:
        print(f"  Vindi Status: {v_st.get('status_financeiro')} | Plano: {v_st.get('plano')}")
        for ft in v_st.get('faturas', []):
            print(f"    Vindi Fat: {ft.get('id')} | Status: {ft.get('status')} | Valor: R$ {ft.get('valor')} | Venc: {ft.get('vencimento')}")

    # Check in Asaas
    a_st = s.get('asaas')
    if a_st:
        print(f"  Asaas Status: {a_st.get('status_financeiro')} | TotalPago: R$ {a_st.get('total_pago')}")
        for ft in a_st.get('faturas', []):
            print(f"    Asaas Fat: {ft.get('id')} | Status: {ft.get('status')} ({ft.get('status_raw')}) | Valor: R$ {ft.get('valor')} | Venc: {ft.get('vencimento')}")

    # Check all faturas in Asaas matching this email directly
    a_fts = [f for f in asaas_cache.get('financeiro', {}).get('faturas_tabela', []) if (f.get('email') or '').lower().strip() == em]
    if a_fts and not a_st:
        print(f"  Direct Asaas Faturas found ({len(a_fts)}):")
        for ft in a_fts:
            print(f"    -> {ft.get('id')} | Status: {ft.get('status')} ({ft.get('status_raw')}) | Valor: R$ {ft.get('valor')} | Venc: {ft.get('vencimento')} | Desc: {ft.get('description')}")

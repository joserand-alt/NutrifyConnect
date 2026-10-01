import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_start = text.find('const DATA = ') + len('const DATA = ')
pos_end = text.find(';\nconst CURRENT_DATA', pos_start)
if pos_end == -1: pos_end = text.find(';\nlet CURRENT_DATA', pos_start)
if pos_end == -1: pos_end = text.find(';const CURRENT_DATA', pos_start)

data = json.loads(text[pos_start:pos_end])

st_list = data.get('students', [])
print(f"Total students in dataset: {len(st_list)}")

sos_students = []
for s in st_list:
    c = str(s.get('curso', '')).upper()
    if 'ANTIBIOT' in c or 'SOS' in c or 'S.O.S' in c:
        sos_students.append(s)

print(f"\nStudents enrolled in SOS Antibiótico: {len(sos_students)}")
for s in sos_students:
    print(f"\nNome: {s.get('nome')} | Email: {s.get('email')} | Curso: {s.get('curso')} | Status: {s.get('status')} | Acessou: {s.get('acessou')}")
    if s.get('vindi'):
        v = s['vindi']
        print(f"  Vindi: StatusFin={v.get('status_financeiro')} | Plano={v.get('plano')} | ValorParcela={v.get('valor_parcela')} | Faturas={len(v.get('faturas', []))}")
        for ft in v.get('faturas', []):
            print(f"    Vindi Fat: ID {ft.get('id')} | Status: {ft.get('status')} | Valor: R$ {ft.get('valor')} | Venc: {ft.get('vencimento')}")
    if s.get('asaas'):
        a = s['asaas']
        print(f"  Asaas: StatusFin={a.get('status_financeiro')} | TotalPago=R$ {a.get('total_pago')} | Faturas={len(a.get('faturas', []))}")
        for ft in a.get('faturas', []):
            print(f"    Asaas Fat: ID {ft.get('id')} | Status: {ft.get('status')} ({ft.get('status_raw')}) | Valor: R$ {ft.get('valor')} | Venc: {ft.get('vencimento')} | Desc: {ft.get('description')}")

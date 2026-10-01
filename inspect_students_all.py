import json
from collections import Counter

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos_s = html.find('"students":')
pos_m = html.find('"mensagens_recentes":', pos_s)
raw = html[pos_s + 11 : pos_m].strip().rstrip(',')
students = json.loads(raw)
print('Total students:', len(students))

cursos = Counter(s.get('curso') for s in students)
print('\n--- ALL STUDENT COURSES ---')
for c, cnt in cursos.most_common():
    print(f'  {c}: {cnt}')

turmas = Counter(s.get('turma') for s in students if s.get('turma'))
print('\n--- ALL STUDENT TURMAS ---')
for t, cnt in turmas.most_common():
    print(f'  {t}: {cnt}')

# Check students with no access and no payment
no_acc_no_pay = []
for s in students:
    acessou = s.get('acessou', False)
    has_vindi_pay = False
    if s.get('vindi'):
        v = s['vindi']
        if (v.get('total_pago') or 0) > 0 or len(v.get('faturas', [])) > 0:
            has_vindi_pay = True
    has_asaas_pay = False
    if s.get('asaas'):
        a = s['asaas']
        if (a.get('total_pago') or 0) > 0 or len(a.get('faturas', [])) > 0:
            has_asaas_pay = True
    
    if not acessou and not has_vindi_pay and not has_asaas_pay:
        no_acc_no_pay.append(s)

print(f'\nStudents with NO ACCESS and NO PAYMENT: {len(no_acc_no_pay)}')
for s in no_acc_no_pay[:10]:
    print(f"  {s.get('nome')} | {s.get('email')} | {s.get('curso')} | plat: {s.get('plataforma')}")

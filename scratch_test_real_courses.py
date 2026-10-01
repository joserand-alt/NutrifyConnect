import json, re

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    v = json.load(f)
v_subs = v.get('subscriptions', [])

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    a = json.load(f)
a_subs = a.get('subscriptions', [])

with open('dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('DATA = {')
end_idx = html.find('};\n\nlet CURRENT_DATA', idx)
data_str = html[idx+7:end_idx+1]
DATA = json.loads(data_str)

students = DATA.get('students', [])

vindi_by_email = {}
for sub in v_subs:
    em = (sub.get('customer_email') or '').lower().strip()
    if em and sub.get('status_assinatura') in ['active', 'em_dia', 'ativo']:
        vindi_by_email[em] = sub.get('plano')

asaas_by_email = {}
for sub in a_subs:
    em = (sub.get('customer_email') or '').lower().strip()
    if em:
        asaas_by_email[em] = sub.get('description') or sub.get('plano')

print('--- ANÁLISE DE CURSOS REAIS DOS ALUNOS ATUALMENTE EM S.O.S ANTIBIOTICO ---')
sos_students = [s for s in students if 'S.O.S' in s.get('curso', '') or 'ANTIBIOTICO' in s.get('curso', '')]
print(f'Total atual de SOS: {len(sos_students)}')

real_courses_count = {}
for s in sos_students:
    em = (s.get('email') or '').lower().strip()
    v_plano = vindi_by_email.get(em)
    a_desc = asaas_by_email.get(em)
    
    if v_plano:
        real_c = f"Vindi: {v_plano}"
    elif a_desc:
        real_c = f"Asaas: {a_desc}"
    else:
        real_c = "Sem financeiro direto (Logs apenas)"
    real_courses_count[real_c] = real_courses_count.get(real_c, 0) + 1

for c, count in sorted(real_courses_count.items(), key=lambda x: x[1], reverse=True):
    print(f"  {count} alunos -> {c}")

import json

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

prefix = 'const DATA = '
start = html.find(prefix) + len(prefix)
decoder = json.JSONDecoder()
data, _ = decoder.raw_decode(html[start:])

students = data.get('students', [])
print(f'Total students in DATA: {len(students)}')

# Breakdown by status in students list
by_status = {}
by_acesso = {'acessou': 0, 'nunca_acessou': 0}
by_fin = {'vindi_active': 0, 'vindi_expired_paid': 0, 'vindi_canceled': 0, 'asaas': 0, 'sem_fin': 0}

for s in students:
    ac = s.get('acessou', False) or len(s.get('events', [])) > 0
    if ac: by_acesso['acessou'] += 1
    else: by_acesso['nunca_acessou'] += 1
    
    v = s.get('vindi') or {}
    a = s.get('asaas') or {}
    v_st = v.get('status_assinatura')
    
    if v_st == 'active': by_fin['vindi_active'] += 1
    elif v_st in ['expired', 'inactive']: by_fin['vindi_expired_paid'] += 1
    elif v_st == 'canceled': by_fin['vindi_canceled'] += 1
    elif a: by_fin['asaas'] += 1
    else: by_fin['sem_fin'] += 1

print('\nAcesso:')
for k, v in by_acesso.items():
    print(f'  {k}: {v}')

print('\nFinanceiro:')
for k, v in by_fin.items():
    print(f'  {k}: {v}')

# Check where 661 comes from in template.html or dashboard JS
print('\nSearching for 661 or active matricula calculation in HTML...')
import re
for m in re.finditer(r'661|matricula|matrículas|active_students', html, re.IGNORECASE):
    idx = m.start()
    print(repr(html[max(0, idx-50):min(len(html), idx+80)]))
    print('-'*50)

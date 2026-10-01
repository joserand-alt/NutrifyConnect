import json

with open('dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('DATA = {')
end_idx = html.find('};\n\nlet CURRENT_DATA', idx)
data_str = html[idx+7:end_idx+1]
DATA = json.loads(data_str)

students = DATA.get('students', [])
sos_students = [s for s in students if 'S.O.S' in s.get('curso', '') or 'ANTIBIOTICO' in s.get('curso', '')]
print(f'Total de alunos classificados como S.O.S ANTIBIOTICO: {len(sos_students)}')

origens = {}
for s in sos_students:
    orig = s.get('curso_origem') or ('Inferido' if s.get('curso_inferido') else 'Log de Acesso')
    origens[orig] = origens.get(orig, 0) + 1

print('Origens dos alunos SOS:', origens)

print('\nAmostra de 25 alunos classificados como SOS:')
for s in sos_students[:25]:
    v = s.get('vindi') or {}
    a = s.get('asaas') or {}
    v_plano = v.get('plano') if isinstance(v, dict) else ''
    print(f"- {s.get('nome')} | email: {s.get('email')} | origem: {s.get('curso_origem')} | Vindi: {v_plano}")

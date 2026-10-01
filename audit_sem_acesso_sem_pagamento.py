import sys, json

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = content.find('const DATA = ')
end_m = content.find(';\n', m)
data = json.loads(content[m+len('const DATA = '):end_m])

students = data.get('students', [])
v_faturas = data.get('financeiro', {}).get('faturas_tabela', [])
a_faturas = data.get('financeiro_asaas', {}).get('faturas_tabela', [])

financial_emails = set()
financial_names = set()

for f in v_faturas:
    em = (f.get('email') or '').lower().strip()
    nm = (f.get('aluno') or '').lower().strip()
    if em: financial_emails.add(em)
    if nm: financial_names.add(nm)

for f in a_faturas:
    em = (f.get('email') or '').lower().strip()
    nm = (f.get('aluno') or '').lower().strip()
    if em: financial_emails.add(em)
    if nm: financial_names.add(nm)

sem_acesso_sem_pagamento = []
matriculas_validas = []

for s in students:
    em = (s.get('email') or '').lower().strip()
    nm = (s.get('nome') or '').lower().strip()
    acessou = s.get('acessou', False)
    logins = s.get('logins', 0)
    has_access = (acessou and logins > 0)
    
    v = s.get('vindi') or {}
    a = s.get('asaas') or {}
    has_finance = bool(v or a or em in financial_emails or nm in financial_names)
    
    if not has_access and not has_finance:
        sem_acesso_sem_pagamento.append(s)
    else:
        matriculas_validas.append(s)

print(f"Total inicial em DATA.students: {len(students)}")
print(f"Registros SEM ACESSO E SEM PAGAMENTO (a expurgar): {len(sem_acesso_sem_pagamento)}")
print(f"Total de MATRÍCULAS REAIS VÁLIDAS: {len(matriculas_validas)}")

print("\n--- Lista dos registros expurgados ---")
for idx, x in enumerate(sem_acesso_sem_pagamento, 1):
    print(f"{idx}. {x.get('nome')} | {x.get('email')} | Curso: {x.get('curso')} | Origem: {x.get('origem', 'N/A')}")

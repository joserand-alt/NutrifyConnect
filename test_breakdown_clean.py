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

# Map of paid emails and names
paid_emails = set()
paid_names = set()
for f in v_faturas:
    if f.get('status') in ['pago', 'paid']:
        em = (f.get('email') or '').lower().strip()
        nm = (f.get('aluno') or '').lower().strip()
        if em: paid_emails.add(em)
        if nm: paid_names.add(nm)
for f in a_faturas:
    if f.get('status') in ['pago', 'paid']:
        em = (f.get('email') or '').lower().strip()
        nm = (f.get('aluno') or '').lower().strip()
        if em: paid_emails.add(em)
        if nm: paid_names.add(nm)

matriculas_canceladas = []
matriculas_concluidas = []
matriculas_vigentes = []
alunos_pagantes = []

for s in students:
    em = (s.get('email') or '').lower().strip()
    nm = (s.get('nome') or '').lower().strip()
    
    # Has paid invoice?
    has_paid = (em in paid_emails or nm in paid_names)
    if has_paid:
        alunos_pagantes.append(s)
        
    v = s.get('vindi') or {}
    a = s.get('asaas') or {}
    v_st = (v.get('status_financeiro') or v.get('status_assinatura') or '').lower()
    a_st = (a.get('status_financeiro') or a.get('status_assinatura') or '').lower()
    
    is_cancel = (v_st in ['cancelado', 'canceled'] or a_st in ['cancelado', 'canceled'] or s.get('status') == 'Cancelado')
    is_concluido = ((v_st in ['quitado'] or a_st in ['quitado'] or s.get('status') in ['Concluído', 'Encerrado'] or s.get('turma_encerrada') is True) and not is_cancel)
    
    if is_cancel:
        matriculas_canceladas.append(s)
    elif is_concluido:
        matriculas_concluidas.append(s)
    else:
        matriculas_vigentes.append(s)

print(f'Total Matriculas: {len(students)}')
print(f'Matriculas Vigentes (Ativas Recorrentes): {len(matriculas_vigentes)}')
print(f'Matriculas Concluidas / Quitadas: {len(matriculas_concluidas)}')
print(f'Matriculas Canceladas: {len(matriculas_canceladas)}')
print(f'Alunos Pagantes Confirmados: {len(alunos_pagantes)} ({len(alunos_pagantes)/len(students)*100:.1f}%)')

eng_vigentes = {'ativos': 0, 'em_risco': 0, 'abandono': 0, 'nunca': 0}
for s in matriculas_vigentes:
    acessou = s.get('acessou', False)
    logins = s.get('logins', 0)
    dias_inativo = s.get('dias_inativo', 0)
    cadencia = s.get('cadencia', 0)
    dias_ativo = s.get('dias_ativo', 0)
    
    if not acessou or logins == 0:
        eng_vigentes['nunca'] += 1
    elif logins > 1 and dias_ativo > 0:
        if dias_inativo > 30 or (dias_inativo > 14 and cadencia > 0 and dias_inativo > (cadencia * 2.5)):
            eng_vigentes['abandono'] += 1
        elif cadencia > 0 and dias_inativo > (cadencia * 1.5 + 2):
            eng_vigentes['em_risco'] += 1
        else:
            eng_vigentes['ativos'] += 1
    else:
        if dias_inativo > 14:
            eng_vigentes['abandono'] += 1
        elif dias_inativo > 7:
            eng_vigentes['em_risco'] += 1
        else:
            eng_vigentes['ativos'] += 1

total_v = len(matriculas_vigentes)
print('--- Engajamento na Base Vigente ---')
print(f"Alunos Engajados (Ativos): {eng_vigentes['ativos']} ({eng_vigentes['ativos']/total_v*100:.1f}%)")
print(f"Alunos em Risco: {eng_vigentes['em_risco']} ({eng_vigentes['em_risco']/total_v*100:.1f}%)")
print(f"Abandono / Inativos: {eng_vigentes['abandono']} ({eng_vigentes['abandono']/total_v*100:.1f}%)")
print(f"Nunca Acessaram: {eng_vigentes['nunca']} ({eng_vigentes['nunca']/total_v*100:.1f}%)")

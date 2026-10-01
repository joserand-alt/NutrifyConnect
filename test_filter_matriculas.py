import sys, json

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = content.find('const DATA = ')
end_m = content.find(';\n', m)
data = json.loads(content[m+len('const DATA = '):end_m])

raw_students = data.get('students', [])
v_faturas = data.get('financeiro', {}).get('faturas_tabela', [])
a_faturas = data.get('financeiro_asaas', {}).get('faturas_tabela', [])

paid_emails = set()
paid_names = set()
fin_emails = set()
fin_names = set()

for f in v_faturas:
    em = (f.get('email') or '').lower().strip()
    nm = (f.get('aluno') or '').lower().strip()
    st = (f.get('status') or '').lower()
    if em: fin_emails.add(em)
    if nm: fin_names.add(nm)
    if st in ['pago', 'paid']:
        if em: paid_emails.add(em)
        if nm: paid_names.add(nm)

for f in a_faturas:
    em = (f.get('email') or '').lower().strip()
    nm = (f.get('aluno') or '').lower().strip()
    st = (f.get('status') or '').lower()
    if em: fin_emails.add(em)
    if nm: fin_names.add(nm)
    if st in ['pago', 'paid']:
        if em: paid_emails.add(em)
        if nm: paid_names.add(nm)

# Filter ONLY legitimate matriculas: (has access) OR (has financial record / subscription / payment)
matriculas = []
expurgados = []

for s in raw_students:
    em = (s.get('email') or '').lower().strip()
    nm = (s.get('nome') or '').lower().strip()
    acessou = s.get('acessou', False)
    logins = s.get('logins', 0)
    has_access = (acessou and logins > 0)
    
    v = s.get('vindi') or {}
    a = s.get('asaas') or {}
    has_finance = bool(v or a or em in fin_emails or nm in fin_names)
    
    if has_access or has_finance:
        matriculas.append(s)
    else:
        expurgados.append(s)

print(f"Total bruto anterior: {len(raw_students)}")
print(f"Registros expurgados (Sem Acesso e Sem Pagamento): {len(expurgados)}")
print(f"Total de MATRÍCULAS REAIS VÁLIDAS: {len(matriculas)}")

# Breakdown de matriculas
vigentes = []
concluidas = []
canceladas = []
pagantes = []

for s in matriculas:
    em = (s.get('email') or '').lower().strip()
    nm = (s.get('nome') or '').lower().strip()
    if em in paid_emails or nm in paid_names:
        pagantes.append(s)
        
    v = s.get('vindi') or {}
    a = s.get('asaas') or {}
    v_st = (v.get('status_financeiro') or v.get('status_assinatura') or '').lower()
    a_st = (a.get('status_financeiro') or a.get('status_assinatura') or '').lower()
    
    is_cancel = (v_st in ['cancelado', 'canceled'] or a_st in ['cancelado', 'canceled'] or s.get('status') == 'Cancelado')
    is_concluido = ((v_st in ['quitado'] or a_st in ['quitado'] or s.get('status') in ['Concluído', 'Encerrado'] or s.get('turma_encerrada') is True) and not is_cancel)
    
    if is_cancel:
        canceladas.append(s)
    elif is_concluido:
        concluidas.append(s)
    else:
        vigentes.append(s)

print(f"\n--- Estrutura de Matrículas Reais ---")
print(f"1. Matrículas Vigentes (Ativas Recorrentes): {len(vigentes)}")
print(f"2. Matrículas Concluídas / Quitadas: {len(concluidas)}")
print(f"3. Matrículas Canceladas: {len(canceladas)}")
print(f"-> Soma total de matrículas: {len(vigentes) + len(concluidas) + len(canceladas)}")
print(f"-> Alunos Pagantes Confirmados: {len(pagantes)} ({len(pagantes)/len(matriculas)*100:.1f}% das matrículas)")

# Engajamento da Base Vigente
eng = {'engajados': 0, 'em_risco': 0, 'abandono': 0, 'nunca': 0}
for s in vigentes:
    acessou = s.get('acessou', False)
    logins = s.get('logins', 0)
    dias_inativo = s.get('dias_inativo', 0)
    cadencia = s.get('cadencia', 0)
    dias_ativo = s.get('dias_ativo', 0)
    
    if not acessou or logins == 0:
        eng['nunca'] += 1
    elif logins > 1 and dias_ativo > 0:
        if dias_inativo > 30 or (dias_inativo > 14 and cadencia > 0 and dias_inativo > (cadencia * 2.5)):
            eng['abandono'] += 1
        elif cadencia > 0 and dias_inativo > (cadencia * 1.5 + 2):
            eng['em_risco'] += 1
        else:
            eng['engajados'] += 1
    else:
        if dias_inativo > 14:
            eng['abandono'] += 1
        elif dias_inativo > 7:
            eng['em_risco'] += 1
        else:
            eng['engajados'] += 1

total_vig = len(vigentes)
print(f"\n--- Engajamento na Base Vigente ({total_vig} alunos) ---")
print(f"- Alunos Engajados: {eng['engajados']} ({eng['engajados']/total_vig*100:.1f}%)")
print(f"- Alunos em Risco: {eng['em_risco']} ({eng['em_risco']/total_vig*100:.1f}%)")
print(f"- Abandono / Inativos: {eng['abandono']} ({eng['abandono']/total_vig*100:.1f}%)")
print(f"- Nunca Acessaram (PAGANTES SEM ACESSO): {eng['nunca']} ({eng['nunca']/total_vig*100:.1f}%)")

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

def should_exclude(s):
    email = str(s.get('email', '')).lower().strip()
    nome = str(s.get('nome', '')).lower().strip()
    curso = str(s.get('curso', '')).upper().strip()
    
    if 'NUTRIFY' in curso:
        return True
    if any(dom in email for dom in ['@infectocast', '@integralmedica', '@nutrify']):
        return True
    if 'teste' in email or 'teste' in nome:
        return True
    return False

# Filtro final rigoroso
matriculas = [s for s in raw_students if not should_exclude(s)]

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

print(f"Total de Matrículas Oficiais Reais: {len(matriculas)}")
print(f"1. Matrículas Vigentes (Ativas Recorrentes): {len(vigentes)}")
print(f"2. Matrículas Concluídas / Quitadas: {len(concluidas)}")
print(f"3. Matrículas Canceladas: {len(canceladas)}")
print(f"-> Alunos Pagantes Confirmados: {len(pagantes)} ({len(pagantes)/len(matriculas)*100:.1f}%)")

# Engajamento da Base Vigente Oficial
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
print(f"- Nunca Acessaram: {eng['nunca']} ({eng['nunca']/total_vig*100:.1f}%)")

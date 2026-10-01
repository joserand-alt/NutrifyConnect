import sys, json

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = content.find('const DATA = ')
end_m = content.find(';\n', m)
data = json.loads(content[m+len('const DATA = '):end_m])

students = data.get('students', [])
vindi = data.get('financeiro', {})
asaas = data.get('financeiro_asaas', {})

v_faturas = vindi.get('faturas_tabela', [])
a_faturas = asaas.get('faturas_tabela', [])

# Map of emails and names to students
email_to_student = {}
name_to_student = {}
for s in students:
    em = (s.get('email') or '').lower().strip()
    nm = (s.get('nome') or '').lower().strip()
    if em: email_to_student[em] = s
    if nm: name_to_student[nm] = s

# Courses map with complete metrics
courses_map = {}

def get_or_create_course(c):
    if c not in courses_map:
        courses_map[c] = {
            'curso': c,
            'vigentes': 0,
            'engajados': 0,
            'em_risco': 0,
            'abandono': 0,
            'nunca': 0,
            'concluidos': 0,
            'cancelados': 0,
            'pago_total': 0.0,
            'pago_mes_atual': 0.0,
            'proj_mes_atual': 0.0,
            'pago_mes_ant': 0.0,
            'mrr': 0.0,
            'atraso': 0.0,
            'proj_1m': 0.0,
            'proj_3m': 0.0,
            'proj_6m': 0.0,
            'proj_12m': 0.0
        }
    return courses_map[c]

# 1. Distribute students
for s in students:
    c = s.get('curso') or 'OUTROS / PLATAFORMA GERAL'
    cm = get_or_create_course(c)
    
    v = s.get('vindi') or {}
    a = s.get('asaas') or {}
    v_st = (v.get('status_financeiro') or v.get('status_assinatura') or '').lower()
    a_st = (a.get('status_financeiro') or a.get('status_assinatura') or '').lower()
    
    is_cancel = (v_st in ['cancelado', 'canceled'] or a_st in ['cancelado', 'canceled'] or s.get('status') == 'Cancelado')
    is_concluido = ((v_st in ['quitado'] or a_st in ['quitado'] or s.get('status') in ['Concluído', 'Encerrado'] or s.get('turma_encerrada') is True) and not is_cancel)
    
    if is_cancel:
        cm['cancelados'] += 1
    elif is_concluido:
        cm['concluidos'] += 1
    else:
        cm['vigentes'] += 1
        acessou = s.get('acessou', False)
        logins = s.get('logins', 0)
        dias_inativo = s.get('dias_inativo', 0)
        cadencia = s.get('cadencia', 0)
        dias_ativo = s.get('dias_ativo', 0)
        
        if not acessou or logins == 0:
            cm['nunca'] += 1
        elif logins > 1 and dias_ativo > 0:
            if dias_inativo > 30 or (dias_inativo > 14 and cadencia > 0 and dias_inativo > (cadencia * 2.5)):
                cm['abandono'] += 1
            elif cadencia > 0 and dias_inativo > (cadencia * 1.5 + 2):
                cm['em_risco'] += 1
            else:
                cm['engajados'] += 1
        else:
            if dias_inativo > 14:
                cm['abandono'] += 1
            elif dias_inativo > 7:
                cm['em_risco'] += 1
            else:
                cm['engajados'] += 1
                
        # MRR from active students
        v_parcela = float(v.get('valor_parcela') or 0)
        a_parcela = float(a.get('valor_parcela') or a.get('mrr') or 0)
        cm['mrr'] += (v_parcela + a_parcela)

# 2. Distribute invoices (Vindi & Asaas)
for f in v_faturas + a_faturas:
    em = (f.get('email') or '').lower().strip()
    nm = (f.get('aluno') or '').lower().strip()
    st_obj = email_to_student.get(em) or name_to_student.get(nm)
    c = (st_obj.get('curso') if st_obj else None) or f.get('curso') or 'OUTROS / PLATAFORMA GERAL'
    cm = get_or_create_course(c)
    
    val = float(f.get('valor') or 0)
    st = (f.get('status') or '').lower()
    dt = str(f.get('data') or f.get('vencimento') or '')
    
    # Pago total
    if st in ['pago', 'paid']:
        cm['pago_total'] += val
        if '09/2026' in dt or '2026-09' in dt or '/09/26' in dt:
            cm['pago_mes_atual'] += val
        elif '08/2026' in dt or '2026-08' in dt or '/08/26' in dt:
            cm['pago_mes_ant'] += val
    elif st in ['em_atraso', 'overdue']:
        cm['atraso'] += val
    elif st in ['futuro', 'a_vencer', 'pending']:
        if '09/2026' in dt or '2026-09' in dt or '/09/26' in dt:
            cm['proj_mes_atual'] += val

# Calculate 1m, 3m, 6m, 12m for each course
for c, cm in courses_map.items():
    cm['proj_1m'] = cm['proj_mes_atual'] if cm['proj_mes_atual'] > 0 else (cm['mrr'] * 0.9)
    cm['proj_3m'] = cm['mrr'] * 3
    cm['proj_6m'] = cm['mrr'] * 6
    cm['proj_12m'] = cm['mrr'] * 12
    cm['previsto_mes_vigente'] = cm['pago_mes_atual'] + cm['proj_mes_atual']
    diff = cm['previsto_mes_vigente'] - cm['pago_mes_ant']
    cm['crescimento_mom'] = (diff / cm['pago_mes_ant'] * 100) if cm['pago_mes_ant'] > 0 else 0

print("=== TABELA COMPLETA POR CURSO ===")
print(f"{'Curso':<35} | {'Vig.':<5} | {'Pago Total':<12} | {'Pago Mês':<10} | {'Proj Mês':<10} | {'Prev Mês':<10} | {'MoM%':<7} | {'Pago Ant':<10} | {'MRR':<10} | {'Proj 3m':<10} | {'Proj 6m':<10} | {'Proj 12m':<10}")
print("-" * 155)
for c, cm in sorted(courses_map.items(), key=lambda x: x[1]['vigentes'], reverse=True):
    print(f"{c[:35]:<35} | {cm['vigentes']:<5} | R$ {cm['pago_total']:>9,.0f} | R$ {cm['pago_mes_atual']:>7,.0f} | R$ {cm['proj_mes_atual']:>7,.0f} | R$ {cm['previsto_mes_vigente']:>7,.0f} | {cm['crescimento_mom']:>+6.1f}% | R$ {cm['pago_mes_ant']:>7,.0f} | R$ {cm['mrr']:>7,.0f} | R$ {cm['proj_3m']:>7,.0f} | R$ {cm['proj_6m']:>7,.0f} | R$ {cm['proj_12m']:>8,.0f}")

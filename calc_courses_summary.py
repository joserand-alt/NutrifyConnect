import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    students = data.get('students', [])
    v_kpis = data.get('financeiro', {}).get('kpis', {})
    a_kpis = data.get('financeiro_asaas', {}).get('kpis', {})
    v_fat = data.get('financeiro', {}).get('faturas_tabela', [])
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])
    
    # 1. Enrich students status exactly as template.html does
    email_to_student = {}
    name_to_student = {}
    
    courses_summary = {}
    
    for s in students:
        em = str(s.get('email', '')).lower().strip()
        nm = str(s.get('nome', '')).lower().strip()
        c = s.get('curso') or 'OUTROS / NÃO ESPECIFICADO'
        
        acessou = s.get('acessou', False)
        logins = s.get('logins', 0)
        dias_inativo = s.get('dias_inativo', 0)
        cadencia = s.get('cadencia', 0)
        dias_ativo = s.get('dias_ativo', 0)
        
        vindi = s.get('vindi')
        asaas = s.get('asaas')
        v_st = vindi.get('status_financeiro') or vindi.get('status_assinatura') if vindi else None
        a_st = asaas.get('status_financeiro') or asaas.get('status_assinatura') if asaas else None
        
        if v_st in ('cancelado', 'canceled') or a_st in ('cancelado', 'canceled'):
            st = 'Cancelado'
        elif not acessou:
            st = 'Nunca acessou'
        else:
            if logins > 1 and dias_ativo > 0:
                if dias_inativo > 30 or (dias_inativo > 14 and cadencia and dias_inativo > (cadencia * 2.5)):
                    st = 'Abandonou'
                elif cadencia and dias_inativo > (cadencia * 1.5 + 2):
                    st = 'Em Risco'
                else:
                    st = 'Ativo'
            else:
                if dias_inativo > 14:
                    st = 'Abandonou'
                elif dias_inativo > 7:
                    st = 'Em Risco'
                else:
                    st = 'Ativo'
        
        s['computed_status'] = st
        if em: email_to_student[em] = s
        if nm: name_to_student[nm] = s
        
        if c not in courses_summary:
            courses_summary[c] = {
                'curso': c,
                'total': 0,
                'ativos': 0,
                'em_risco': 0,
                'abandono': 0,
                'nunca': 0,
                'cancelados': 0,
                'pago': 0,
                'atraso': 0,
                'proj': 0,
                'mrr': 0
            }
        
        cs = courses_summary[c]
        cs['total'] += 1
        if st == 'Cancelado':
            cs['cancelados'] += 1
        elif st == 'Ativo':
            cs['ativos'] += 1
        elif st == 'Em Risco':
            cs['em_risco'] += 1
        elif st == 'Abandonou':
            cs['abandono'] += 1
        elif st == 'Nunca acessou':
            cs['nunca'] += 1
        
        # Add MRR from active subscriptions
        if st != 'Cancelado':
            v_mrr = float(vindi.get('valor_recorrente') or 0) if vindi else 0
            a_mrr = float(asaas.get('valor_recorrente') or asaas.get('mrr') or 0) if asaas else 0
            cs['mrr'] += (v_mrr + a_mrr)

    # Invoices linkage
    all_fat = [('vindi', f) for f in v_fat] + [('asaas', f) for f in a_fat]
    for gw, f in all_fat:
        em = str(f.get('email', '')).lower().strip()
        nm = str(f.get('aluno', '')).lower().strip()
        st_obj = email_to_student.get(em) or name_to_student.get(nm)
        c = st_obj['curso'] if st_obj and st_obj.get('curso') else 'OUTROS / NÃO ESPECIFICADO'
        
        if c not in courses_summary:
            courses_summary[c] = {
                'curso': c, 'total': 0, 'ativos': 0, 'em_risco': 0, 'abandono': 0, 'nunca': 0, 'cancelados': 0,
                'pago': 0, 'atraso': 0, 'proj': 0, 'mrr': 0
            }
        
        val = float(f.get('valor') or 0)
        st = f.get('status')
        if st in ('pago', 'paid'):
            courses_summary[c]['pago'] += val
        elif st == 'em_atraso':
            courses_summary[c]['atraso'] += val
        elif st in ('a_vencer', 'futuro', 'pending', 'open'):
            courses_summary[c]['proj'] += val

    # Projeção adicional para Vindi onde faturas futuras não são pré-geradas
    # Distribui a projecao_30d da Vindi proporcionalmente ao MRR de cada curso
    tot_mrr = sum(cs['mrr'] for cs in courses_summary.values())
    v_proj_30d = float(v_kpis.get('projecao_30d') or 0)
    for c, cs in courses_summary.items():
        if tot_mrr > 0 and cs['mrr'] > 0:
            cs['proj'] += v_proj_30d * (cs['mrr'] / tot_mrr)
            
    print(f"{'CURSO':<45} | {'ATIV':<4} | {'RISC':<4} | {'ABAN':<4} | {'CANC':<4} | {'MRR':<10} | {'PROJ':<10} | {'ATRASO':<10}")
    print("-" * 105)
    for c, cs in sorted(courses_summary.items(), key=lambda x: -x[1]['total']):
        print(f"{cs['curso'][:44]:<45} | {cs['ativos']:<4} | {cs['em_risco']:<4} | {cs['abandono']:<4} | {cs['cancelados']:<4} | R${cs['mrr']:>8.0f} | R${cs['proj']:>8.0f} | R${cs['atraso']:>8.0f}")

import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    students = data.get('students', [])
    v_fat = data.get('financeiro', {}).get('faturas_tabela', [])
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])
    
    # 1. Map emails and names to course
    email_to_student = {}
    name_to_student = {}
    courses_map = {}
    
    for s in students:
        em = str(s.get('email', '')).lower().strip()
        nm = str(s.get('nome', '')).lower().strip()
        c = s.get('curso') or 'OUTROS / PLATAFORMA GERAL'
        
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
        
        if c not in courses_map:
            courses_map[c] = {
                'curso': c, 'total': 0, 'ativos': 0, 'em_risco': 0, 'abandono': 0, 'cancelados': 0,
                'pago': 0, 'atraso': 0, 'proj': 0, 'mrr': 0
            }
        
        cm = courses_map[c]
        cm['total'] += 1
        if st == 'Cancelado':
            cm['cancelados'] += 1
        elif st == 'Ativo':
            cm['ativos'] += 1
        elif st == 'Em Risco':
            cm['em_risco'] += 1
        elif st in ('Abandonou', 'Nunca acessou'):
            cm['abandono'] += 1
            
        # MRR
        if st != 'Cancelado':
            val_p = float(vindi.get('valor_parcela') or 0) if vindi else 0
            cm['mrr'] += val_p
            
            # Future scheduled invoices from student's own faturas
            if vindi and vindi.get('faturas'):
                for f in vindi['faturas']:
                    if f.get('status') == 'futuro':
                        cm['proj'] += float(f.get('valor') or 0)

    # Invoices from global tables (Asaas + Vindi)
    all_fat = [('vindi', f) for f in v_fat] + [('asaas', f) for f in a_fat]
    for gw, f in all_fat:
        em = str(f.get('email', '')).lower().strip()
        nm = str(f.get('aluno', '')).lower().strip()
        st_obj = email_to_student.get(em) or name_to_student.get(nm)
        c = st_obj['curso'] if st_obj and st_obj.get('curso') else 'OUTROS / PLATAFORMA GERAL'
        
        if c not in courses_map:
            courses_map[c] = {
                'curso': c, 'total': 0, 'ativos': 0, 'em_risco': 0, 'abandono': 0, 'cancelados': 0,
                'pago': 0, 'atraso': 0, 'proj': 0, 'mrr': 0
            }
            
        val = float(f.get('valor') or 0)
        st = f.get('status')
        if st in ('pago', 'paid'):
            courses_map[c]['pago'] += val
        elif st == 'em_atraso':
            courses_map[c]['atraso'] += val
        elif gw == 'asaas' and st in ('a_vencer', 'pending', 'open'):
            # Asaas pending invoices
            courses_map[c]['proj'] += val

    print(f"{'CURSO':<40} | {'ATIV':<4} | {'RISC':<4} | {'ABAN':<4} | {'CANC':<4} | {'MRR':<10} | {'PROJ':<10} | {'ATRASO':<10}")
    print("-" * 105)
    for c, cm in sorted(courses_map.items(), key=lambda x: -x[1]['total']):
        print(f"{cm['curso'][:39]:<40} | {cm['ativos']:<4} | {cm['em_risco']:<4} | {cm['abandono']:<4} | {cm['cancelados']:<4} | R${cm['mrr']:>8.0f} | R${cm['proj']:>8.0f} | R${cm['atraso']:>8.0f}")

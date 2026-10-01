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
paid_by_student = {}
faturas_by_student = {}

for f in v_faturas:
    em = (f.get('email') or '').lower().strip()
    nm = (f.get('aluno') or '').lower().strip()
    st = (f.get('status') or '').lower()
    val = float(f.get('valor') or 0)
    
    for k in [em, nm]:
        if k:
            if k not in faturas_by_student:
                faturas_by_student[k] = []
            faturas_by_student[k].append(f)
            if st in ['pago', 'paid']:
                if k == em: paid_emails.add(em)
                if k == nm: paid_names.add(nm)
                paid_by_student[k] = paid_by_student.get(k, 0) + val

for f in a_faturas:
    em = (f.get('email') or '').lower().strip()
    nm = (f.get('aluno') or '').lower().strip()
    st = (f.get('status') or '').lower()
    val = float(f.get('valor') or 0)
    
    for k in [em, nm]:
        if k:
            if k not in faturas_by_student:
                faturas_by_student[k] = []
            faturas_by_student[k].append(f)
            if st in ['pago', 'paid']:
                if k == em: paid_emails.add(em)
                if k == nm: paid_names.add(nm)
                paid_by_student[k] = paid_by_student.get(k, 0) + val

# Find the 58 students in matriculas_vigentes who never accessed
nunca_acessaram = []

for s in students:
    em = (s.get('email') or '').lower().strip()
    nm = (s.get('nome') or '').lower().strip()
    
    v = s.get('vindi') or {}
    a = s.get('asaas') or {}
    v_st = (v.get('status_financeiro') or v.get('status_assinatura') or '').lower()
    a_st = (a.get('status_financeiro') or a.get('status_assinatura') or '').lower()
    
    is_cancel = (v_st in ['cancelado', 'canceled'] or a_st in ['cancelado', 'canceled'] or s.get('status') == 'Cancelado')
    is_concluido = ((v_st in ['quitado'] or a_st in ['quitado'] or s.get('status') in ['Concluído', 'Encerrado'] or s.get('turma_encerrada') is True) and not is_cancel)
    
    # Check if in matriculas_vigentes
    if not is_cancel and not is_concluido:
        acessou = s.get('acessou', False)
        logins = s.get('logins', 0)
        if not acessou or logins == 0:
            has_paid = (em in paid_emails or nm in paid_names)
            total_pago = paid_by_student.get(em, 0) or paid_by_student.get(nm, 0)
            v_status = v.get('status_financeiro') or v.get('status_assinatura') or 'Sem Vindi'
            a_status = a.get('status_financeiro') or a.get('status_assinatura') or 'Sem Asaas'
            
            # Count invoices status
            all_fats = faturas_by_student.get(em, []) + faturas_by_student.get(nm, [])
            fat_statuses = {}
            for ft in all_fats:
                fst = ft.get('status', 'desconhecido')
                fat_statuses[fst] = fat_statuses.get(fst, 0) + 1
                
            nunca_acessaram.append({
                'nome': s.get('nome'),
                'email': s.get('email'),
                'curso': s.get('curso'),
                'tem_pagamento': has_paid,
                'total_pago': total_pago,
                'vindi_status': v_status,
                'asaas_status': a_status,
                'fat_statuses': fat_statuses,
                'total_faturas': len(all_fats)
            })

print(f"Total de alunos que Nunca Acessaram na Base Vigente: {len(nunca_acessaram)}")
com_pagamento = [x for x in nunca_acessaram if x['tem_pagamento']]
sem_pagamento = [x for x in nunca_acessaram if not x['tem_pagamento']]

print(f"-> COM pagamento confirmado (faturas pagas): {len(com_pagamento)} ({len(com_pagamento)/len(nunca_acessaram)*100:.1f}%)")
print(f"-> SEM pagamento confirmado: {len(sem_pagamento)} ({len(sem_pagamento)/len(nunca_acessaram)*100:.1f}%)")

print("\n================ DETALHAMENTO DOS QUE NÃO TÊM PAGAMENTO ================")
for idx, x in enumerate(sem_pagamento, 1):
    print(f"{idx}. {x['nome']} | {x['email']} | {x['curso']} | Vindi: {x['vindi_status']} | Asaas: {x['asaas_status']} | Faturas: {x['fat_statuses']}")

print("\n================ RESUMO POR STATUS FINANCEIRO DOS 58 ALUNOS ================")
fin_summary = {}
for x in nunca_acessaram:
    key = f"Vindi: {x['vindi_status']} / Asaas: {x['asaas_status']}"
    fin_summary[key] = fin_summary.get(key, 0) + 1

for k, v in fin_summary.items():
    print(f"- {k}: {v} alunos")

total_valor_pago_pelos_58 = sum(x['total_pago'] for x in nunca_acessaram)
print(f"\nValor total já pago por estes 58 alunos: R$ {total_valor_pago_pelos_58:,.2f}")

import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's extract the student data and simulate the exact logic of lines 1475-1555
m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    students = data.get('students', [])
    
    st_counts = {}
    for s in students:
        acessou = s.get('acessou', False)
        logins = s.get('logins', 0)
        dias_inativo = s.get('dias_inativo', 0)
        cadencia = s.get('cadencia', 0)
        dias_ativo = s.get('dias_ativo', 0)
        aulas_feitas = s.get('aulas_concluidas', 0) # or events
        
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
        st_counts[st] = st_counts.get(st, 0) + 1
    
    print("Simulated student status counts:")
    for k, v in sorted(st_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

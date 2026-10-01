import json, re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const DATA = (\{.*?\});\s*\n', content, re.DOTALL)
if not match:
    print("DATA block not found")
    exit()

data = json.loads(match.group(1))
students = data.get('students', [])

email_target = 'welisoncatarino13@hotmail.com'

print(f"=== Buscando {email_target} ===\n")

for s in students:
    email = (s.get('email') or '').lower().strip()
    if email == email_target:
        print(f"Nome: {s.get('nome')}")
        print(f"Email: {email}")
        print(f"Curso: {s.get('curso')}")
        print(f"Plataforma: {s.get('plataforma')}")
        print(f"Status: {s.get('status_manual', 'N/A')}")
        
        # Vindi data
        vindi = s.get('vindi')
        if vindi:
            print(f"\n--- VINDI ---")
            print(f"  has_vindi: {vindi.get('has_vindi')}")
            print(f"  plano: {vindi.get('plano', 'N/A')}")
            print(f"  status_assinatura: {vindi.get('status_assinatura')}")
            print(f"  status_financeiro: {vindi.get('status_financeiro')}")
            faturas = vindi.get('faturas', [])
            print(f"  faturas: {len(faturas)}")
            for ft in faturas[:5]:
                print(f"    - valor={ft.get('valor')} status={ft.get('status')} venc={ft.get('vencimento')} curso={ft.get('curso', 'N/A')}")
        
        # Asaas data
        asaas = s.get('asaas')
        if asaas:
            print(f"\n--- ASAAS ---")
            print(f"  has_asaas: {asaas.get('has_asaas')}")
            print(f"  plano: {asaas.get('plano', 'N/A')}")
            print(f"  status_assinatura: {asaas.get('status_assinatura')}")
            print(f"  status_financeiro: {asaas.get('status_financeiro')}")
            faturas = asaas.get('faturas', [])
            print(f"  faturas: {len(faturas)}")
            for ft in faturas[:5]:
                print(f"    - valor={ft.get('valor')} status={ft.get('status')} venc={ft.get('vencimento')} desc={ft.get('descricao', 'N/A')[:80]} curso={ft.get('curso', 'N/A')}")
        
        if not vindi and not asaas:
            print("\n  SEM DADOS FINANCEIROS (Vindi/Asaas)")
        
        print("\n" + "="*60)

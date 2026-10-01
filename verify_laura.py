import json, re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the DATA JSON block
match = re.search(r'const DATA = (\{.*?\});\s*\n', content, re.DOTALL)
if match:
    data_str = match.group(1)
    data = json.loads(data_str)
    students = data.get('students', [])
    
    # Find Laura
    for s in students:
        email = (s.get('email') or '').lower()
        nome = s.get('nome', '?')
        if 'laurawarlitzer' in email or ('laura' in nome.lower() and 'warlitzer' in nome.lower()):
            curso = s.get('curso', '?')
            vindi = s.get('vindi')
            asaas = s.get('asaas')
            print(f"Nome: {nome}")
            print(f"Email: {email}")
            print(f"Curso: {curso}")
            if vindi:
                print(f"  Vindi status_financeiro: {vindi.get('status_financeiro', 'N/A')}")
                print(f"  Vindi status_assinatura: {vindi.get('status_assinatura', 'N/A')}")
                print(f"  Vindi has_vindi: {vindi.get('has_vindi', 'N/A')}")
            else:
                print("  Vindi: SEM DADOS")
            if asaas:
                print(f"  Asaas status_financeiro: {asaas.get('status_financeiro', 'N/A')}")
                print(f"  Asaas status_assinatura: {asaas.get('status_assinatura', 'N/A')}")
                print(f"  Asaas has_asaas: {asaas.get('has_asaas', 'N/A')}")
            else:
                print("  Asaas: SEM DADOS")
            print("---")
else:
    print("DATA block not found")

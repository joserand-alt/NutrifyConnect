import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi_cache = json.load(f)

v_subs = vindi_cache.get('subscriptions', [])

print("=== VINDI SUBSCRIPTIONS WITH SOS ANTIBIOTICO ===")
for s in v_subs:
    plano = str(s.get('plano', ''))
    if 'sos' in plano.lower() or 'antibiot' in plano.lower():
        print(f"Sub ID: {s.get('id')} | Status: {s.get('status')} | StatusFin: {s.get('status_financeiro')} | ValorParcela: R$ {s.get('valor_parcela')} | ProxVenc: {s.get('proximo_vencimento')} | Email: {s.get('customer_email')} | Plano: {s.get('plano')}")
        print("  Faturas associadas:", len(s.get('faturas', [])))
        for ft in s.get('faturas', []):
            print(f"    Fat: ID {ft.get('id')} | Status: {ft.get('status')} | Valor: {ft.get('valor')} | Venc: {ft.get('vencimento')} | Pag: {ft.get('data_pagamento')}")

# Now let's check students enrolled in SOS Antibiótico in the platform
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas_cache = json.load(f)

print("\n=== ASAAS STUDENTS & ORDERS ===")
# Let's inspect the order descriptions or amounts in Asaas
# E.g. which Asaas payments match SOS Antibiótico price? (What is the price of SOS Antibiótico?)
a_faturas = asaas_cache.get('financeiro', {}).get('faturas_tabela', [])
for f in a_faturas:
    val = float(f.get('valor') or 0)
    desc = str(f.get('description', ''))
    # Print distinct payments with their amounts and order number
    if val in [249, 24.9, 487, 819, 719, 540, 196.83, 218.7, 519]:
        pass

print("\n=== STUDENTS IN DASHBOARD GENERATED ===")
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

import re
m = re.search(r'const DATA = (.*?);\s*const CURRENT_DATA', html_text, re.DOTALL)
if m:
    data_json = json.loads(m.group(1))
    st_list = data_json.get('students', [])
    sos_students = [s for s in st_list if 'antibiot' in (s.get('curso') or '').lower() or 'sos' in (s.get('curso') or '').lower()]
    print(f"Total students in SOS Antibiótico: {len(sos_students)}")
    for s in sos_students:
        print(f"  Aluno: {s.get('nome')} | Email: {s.get('email')} | Curso: {s.get('curso')} | Status: {s.get('status')} | Vindi: {bool(s.get('vindi'))} | Asaas: {bool(s.get('asaas'))}")
        if s.get('vindi'):
            print("    Vindi data:", s.get('vindi'))
        if s.get('asaas'):
            print("    Asaas data:", s.get('asaas'))

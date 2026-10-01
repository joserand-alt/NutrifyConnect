import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# 1. Inspect Asaas Cache
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas_cache = json.load(f)

print("=== ASAAS CACHE INSPECTION FOR SOS ANTIBIOTICO ===")
a_faturas = asaas_cache.get('financeiro', {}).get('faturas_tabela', [])
print(f"Total Asaas faturas: {len(a_faturas)}")

sos_a_faturas = []
for f in a_faturas:
    desc = str(f.get('description', '')).lower()
    plano = str(f.get('plano', '')).lower()
    aluno = str(f.get('aluno', ''))
    em = str(f.get('email', ''))
    if any(k in desc or k in plano for k in ['sos', 's.o.s', 'antibiotico', 'antibiótico', 'atb', 'mdr']):
        sos_a_faturas.append(f)

print(f"Found {len(sos_a_faturas)} Asaas faturas matching SOS/Antibiotico by description/plano:")
for f in sos_a_faturas:
    print(f"  ID: {f.get('id')} | Status: {f.get('status')} ({f.get('status_raw')}) | Forma: {f.get('forma_pagamento')} | Valor: R$ {f.get('valor')} | Venc: {f.get('vencimento')} | Pag: {f.get('data_pagamento')} | Aluno: {f.get('aluno')} ({f.get('email')}) | Desc: {f.get('description')}")

# 2. Inspect Asaas students in cache
a_data = asaas_cache.get('data', {})
sos_a_students = []
for k, st in a_data.items():
    name = str(st.get('customer_name', ''))
    em = str(st.get('customer_email', ''))
    fts = st.get('faturas', [])
    fts_desc = ' '.join(str(x.get('description', '')) for x in fts).lower()
    if any(k in fts_desc for k in ['sos', 's.o.s', 'antibiotico', 'antibiótico', 'atb']):
        sos_a_students.append((k, name, em, len(fts), st.get('status_financeiro'), st.get('total_pago')))

print(f"\nFound {len(sos_a_students)} Asaas students linked to SOS/Antibiotico:")
for s in sos_a_students:
    print(f"  Ref: {s[0]} | Name: {s[1]} | Email: {s[2]} | Faturas: {s[3]} | StatusFin: {s[4]} | TotalPago: R$ {s[5]}")

# 3. Inspect Vindi Cache
with open(r'c:\Users\DELL\Desktop\Acompanhamento de acessos\vindi_cache.json', 'r', encoding='utf-8', errors='ignore') as f:
    vindi_cache = json.load(f)

print("\n=== VINDI CACHE INSPECTION FOR SOS ANTIBIOTICO ===")
v_subs = vindi_cache.get('subscriptions', [])
print(f"Total Vindi subscriptions: {len(v_subs)}")

sos_v_subs = []
for s in v_subs:
    plano = str(s.get('plano', '')).lower()
    desc = str(s.get('description', '')).lower()
    em = str(s.get('customer_email', ''))
    if any(k in plano or k in desc for k in ['sos', 's.o.s', 'antibiotico', 'antibiótico', 'atb', 'mdr']):
        sos_v_subs.append(s)

print(f"Found {len(sos_v_subs)} Vindi subscriptions matching SOS/Antibiotico:")
for s in sos_v_subs:
    print(f"  ID: {s.get('id')} | Status: {s.get('status')} | StatusFin: {s.get('status_financeiro')} | ValorParcela: R$ {s.get('valor_parcela')} | ProxVenc: {s.get('proximo_vencimento')} | Plano: {s.get('plano')} | Email: {s.get('customer_email')}")

import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# 1. Search in Vindi Cache
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi_cache = json.load(f)

print("=== 1. VINDI CACHE SEARCH ===")
v_subs = vindi_cache.get('subscriptions', [])
v_faturas = vindi_cache.get('faturas_tabela', [])

print(f"Total Vindi subscriptions: {len(v_subs)}")
print(f"Total Vindi faturas: {len(v_faturas)}")

v_matches_sub = []
for s in v_subs:
    text = json.dumps(s, ensure_ascii=False).lower()
    if 'antibiot' in text or 's.o.s' in text or 'sos' in text or 'atb' in text or 'mdr' in text:
        v_matches_sub.append(s)

print(f"Vindi subscriptions matching keywords: {len(v_matches_sub)}")
for s in v_matches_sub[:10]:
    print("  Sub:", s.get('id'), s.get('plano'), s.get('status'), s.get('status_financeiro'), s.get('valor_parcela'), s.get('customer_email'))

v_matches_fat = []
for f in v_faturas:
    text = json.dumps(f, ensure_ascii=False).lower()
    if 'antibiot' in text or 's.o.s' in text or 'sos' in text:
        v_matches_fat.append(f)

print(f"Vindi faturas matching keywords: {len(v_matches_fat)}")
for f in v_matches_fat[:10]:
    print("  Fat:", f.get('id'), f.get('plano'), f.get('status'), f.get('valor'), f.get('vencimento'), f.get('data_pagamento'), f.get('email'))

# 2. Search in Asaas Cache
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas_cache = json.load(f)

print("\n=== 2. ASAAS CACHE SEARCH ===")
a_faturas = asaas_cache.get('financeiro', {}).get('faturas_tabela', [])
a_data = asaas_cache.get('data', {})

print(f"Total Asaas faturas: {len(a_faturas)}")
print(f"Total Asaas customer accounts: {len(a_data)}")

# Let's inspect all unique plans / descriptions in Asaas
a_descriptions = set()
for f in a_faturas:
    a_descriptions.add((f.get('description') or ''))

print(f"Unique Asaas payment descriptions ({len(a_descriptions)}):")
for d in sorted(a_descriptions):
    print("  ->", repr(d))

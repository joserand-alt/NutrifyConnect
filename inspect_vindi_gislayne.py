import json

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi = json.load(f)

# Find Gislayne in vindi
students = vindi.get('students', {})
subs = vindi.get('subscriptions', [])
faturas = vindi.get('faturas_tabela', [])

print("Subscriptions for gislayne:")
for s in subs:
    if 'gislayne' in str(s).lower():
        print("Sub keys:", list(s.keys()))
        print("Sub created_at / start_at:", s.get('created_at'), s.get('start_at'), s.get('plano'))
        print("Sub faturas:", len(s.get('faturas', [])))
        for f in s.get('faturas', []):
            print("  Fatura:", f.get('id'), f.get('status'), f.get('vencimento'), f.get('data_pagamento'))

print("\nStudents in vindi_cache for gislayne:")
for k, v in students.items():
    if 'gislayne' in str(k).lower() or 'gislayne' in str(v).lower():
        print(k, v)

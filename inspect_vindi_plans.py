import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi_cache = json.load(f)

v_subs = vindi_cache.get('subscriptions', [])
v_faturas = vindi_cache.get('faturas_tabela', [])

v_planos_sub = set()
for s in v_subs:
    v_planos_sub.add(s.get('plano'))

print(f"Distinct Vindi subscription plans ({len(v_planos_sub)}):")
for p in sorted(v_planos_sub):
    print("  ->", p)

v_planos_fat = set()
for f in v_faturas:
    v_planos_fat.add(f.get('plano') or f.get('description'))

print(f"\nDistinct Vindi fatura descriptions/plans ({len(v_planos_fat)}):")
for p in sorted(v_planos_fat):
    if p:
        print("  ->", p)

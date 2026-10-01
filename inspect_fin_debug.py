import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])

vindi = data.get('financeiro', {})
asaas = data.get('financeiro_asaas', {})

print("=== VINDI KPIS ===")
print(json.dumps(vindi.get('kpis', {}), indent=2, ensure_ascii=False))

print("\n=== ASAAS KPIS ===")
print(json.dumps(asaas.get('kpis', {}), indent=2, ensure_ascii=False))

print("\n=== VINDI PROJECAO MENSAL MAP ===")
print(json.dumps(vindi.get('projecao_mensal_map', {}), indent=2, ensure_ascii=False))

print("\n=== ASAAS PROJECAO MENSAL MAP ===")
print(json.dumps(asaas.get('projecao_mensal_map', {}), indent=2, ensure_ascii=False))

print("\n=== VINDI SUBSCRIPTIONS COUNT & SAMPLE ===")
subs = vindi.get('subscriptions', [])
print(f"Total subscriptions in vindi: {len(subs)}")
if subs:
    print("Sample sub:", {
        'id': subs[0].get('id'),
        'plano': subs[0].get('plano'),
        'valor_parcela': subs[0].get('valor_parcela'),
        'status_financeiro': subs[0].get('status_financeiro'),
        'proximo_vencimento': subs[0].get('proximo_vencimento'),
        'faturas_count': len(subs[0].get('faturas', []))
    })

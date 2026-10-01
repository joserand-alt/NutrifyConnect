import json

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vc = json.load(f)

v_data = vc.get('data', {})
print(f"Total students in v_data: {len(v_data)}")

# Convert v_data to subscriptions list
v_subs = []
for em, s in v_data.items():
    if isinstance(s, dict) and s.get('has_vindi'):
        v_subs.append({
            'id': s.get('subscription_id') or s.get('customer_id'),
            'customer_name': s.get('customer_name'),
            'customer_email': s.get('customer_email') or em,
            'plano': s.get('plano'),
            'status_assinatura': s.get('status_assinatura'),
            'status_financeiro': s.get('status_financeiro'),
            'valor_parcela': s.get('valor_parcela'),
            'proximo_vencimento': s.get('proximo_vencimento'),
            'faturas': s.get('faturas', [])
        })

print(f"Total converted v_subs: {len(v_subs)}")
adimplentes = [s for s in v_subs if s.get('status_financeiro') == 'adimplente']
print(f"Adimplentes v_subs: {len(adimplentes)}")
print(f"Total MRR from adimplentes: R$ {sum(s['valor_parcela'] for s in adimplentes):,.2f}")

import json

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vc = json.load(f)

print("Top keys in vindi_cache:", list(vc.keys()))
print("Does vindi_cache have 'subscriptions'?", 'subscriptions' in vc)
print("Does vindi_cache['financeiro'] have 'subscriptions'?", 'subscriptions' in vc.get('financeiro', {}))

# Let's count how many students in vc['data'] have active subscriptions / faturas
data = vc.get('data', {})
print(f"Total students in vc['data']: {len(data)}")

subs_count = 0
total_mrr = 0
for em, s in data.items():
    if isinstance(s, dict) and s.get('has_vindi'):
        if s.get('status_financeiro') == 'adimplente' or s.get('status_assinatura') == 'active':
            subs_count += 1
            total_mrr += float(s.get('valor_parcela') or 0)

print(f"Active adimplente subscribers in vc['data']: {subs_count}")
print(f"Total MRR in vc['data']: R$ {total_mrr:,.2f}")

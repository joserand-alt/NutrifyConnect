import json

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = 'const DATA = '
i1 = html.find(m)
i2 = html.find(';\n\nlet CURRENT_DATA', i1)
if i2 == -1: i2 = html.find(';\nlet CURRENT_DATA', i1)
data = json.loads(html[i1+len(m):i2].strip().rstrip(';'))

vSubs = data.get('financeiro', {}).get('subscriptions', [])
print('Total Vindi subscriptions:', len(vSubs))

ped_subs = []
for s in vSubs:
    c = str(s.get('curso', '')).upper()
    pl = str(s.get('plano', '')).upper()
    if 'PED' in c or 'INFECTOPED' in c or 'PEDIATR' in pl:
        ped_subs.append(s)

print(f'Total PED subscriptions: {len(ped_subs)}')

active_ped_subs = [s for s in ped_subs if s.get('status_financeiro') == 'adimplente']
print(f'Active (adimplente) PED subs: {len(active_ped_subs)}')

total_mrr = sum(float(s.get('valor_parcela') or 0) for s in active_ped_subs)
print(f'Total PED MRR from valor_parcela: R$ {total_mrr:.2f}')

print('\nBreakdown of active PED subs:')
for s in active_ped_subs:
    pl = s.get('plano', '')
    vp = float(s.get('valor_parcela') or 0)
    fats = s.get('faturas', [])
    paid = len([f for f in fats if f.get('status') in ['paid', 'pago']])
    print(f"  {s.get('customer_name', 'Unknown')}: R$ {vp:.2f}/mês | Plano: '{pl}' | Faturas pagas: {paid}")

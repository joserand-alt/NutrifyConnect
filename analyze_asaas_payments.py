import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

fin = cache.get('financeiro', {})
faturas = fin.get('faturas_tabela', [])

print(f"Total Asaas faturas in cache: {len(faturas)}")

# Group by status and forma_pagamento
summary = {}
for f in faturas:
    key = (f.get('forma_pagamento'), f.get('status'), f.get('status_raw'))
    if key not in summary:
        summary[key] = {'count': 0, 'total': 0.0, 'samples': []}
    summary[key]['count'] += 1
    summary[key]['total'] += float(f.get('valor') or 0)
    if len(summary[key]['samples']) < 2:
        summary[key]['samples'].append({
            'id': f.get('id'),
            'aluno': f.get('aluno'),
            'valor': f.get('valor'),
            'vencimento': f.get('vencimento'),
            'data_pagamento': f.get('data_pagamento'),
            'description': f.get('description')
        })

for (forma, st, st_raw), info in sorted(summary.items()):
    print(f"\nForma: {forma} | Status: {st} (Raw: {st_raw}) | Qtd: {info['count']} | Total: R$ {info['total']:,.2f}")
    for s in info['samples']:
        print(f"   Sample: {s}")

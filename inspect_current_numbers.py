import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])

vindi = data.get('financeiro', {})
asaas = data.get('financeiro_asaas', {})

v_kpis = vindi.get('kpis', {})
a_kpis = asaas.get('kpis', {})

v_rec = v_kpis.get('total_recebido', 0)
a_rec = a_kpis.get('total_recebido', 0)
v_mrr = v_kpis.get('mrr_ativo', 0)
a_mrr = a_kpis.get('mrr_ativo', 0)
v_p30 = v_kpis.get('projecao_30d', 0)
a_p30 = a_kpis.get('projecao_30d', 0)
v_p60 = v_kpis.get('projecao_60d', 0)
v_p12 = v_kpis.get('projecao_12m', 0)

print(f"Receita Realizada Total: R$ {(v_rec + a_rec):,.2f} (Vindi: {v_rec:,.2f} + Asaas: {a_rec:,.2f})")
print(f"MRR Total: R$ {(v_mrr + a_mrr):,.2f} (Vindi: {v_mrr:,.2f} + Asaas: {a_mrr:,.2f})")
print(f"Projeção 30d (M+1): R$ {(v_p30 + a_p30):,.2f} (Vindi: {v_p30:,.2f} + Asaas: {a_p30:,.2f})")
print(f"Projeção 60d / 3M: R$ {v_p60:,.2f}")
print(f"Projeção 12M: R$ {v_p12:,.2f}")

# Check monthly projections in vindi and asaas
print("\nVindi projecao_mensal:")
for p in vindi.get('projecao_mensal', []):
    print(f"  {p.get('mes')} ({p.get('label')}): Previsto = R$ {p.get('previsto', 0):,.2f} | Realizado = R$ {p.get('realizado', 0):,.2f}")

print("\nAsaas projecao_mensal:")
for p in asaas.get('projecao_mensal', []):
    print(f"  {p.get('mes')} ({p.get('label')}): Previsto = R$ {p.get('previsto', 0):,.2f} | Realizado = R$ {p.get('realizado', 0):,.2f}")

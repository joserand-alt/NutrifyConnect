import json

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vc = json.load(f)

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    ac = json.load(f)

v_proj_list = vc.get('financeiro', {}).get('projecao_mensal', [])
a_proj_list = ac.get('financeiro', {}).get('projecao_mensal', [])

# Map by month
v_by_m = {p['mes']: p for p in v_proj_list}
a_by_m = {p['mes']: p for p in a_proj_list}

all_months = sorted(list(set(list(v_by_m.keys()) + list(a_by_m.keys()))))
print("=== CONSOLIDATED MONTHLY PROJECTIONS ===")

consolidated_proj = []
for ym in all_months:
    v_prev = v_by_m.get(ym, {}).get('previsto', 0)
    a_prev = a_by_m.get(ym, {}).get('previsto', 0)
    v_real = v_by_m.get(ym, {}).get('realizado', 0)
    a_real = a_by_m.get(ym, {}).get('realizado', 0)
    
    tot_prev = v_prev + a_prev
    tot_real = v_real + a_real
    
    y, m = ym.split('-')
    meses_pt = {'01':'Jan', '02':'Fev', '03':'Mar', '04':'Abr', '05':'Mai', '06':'Jun', '07':'Jul', '08':'Ago', '09':'Set', '10':'Out', '11':'Nov', '12':'Dez'}
    lbl = f"{meses_pt.get(m, m)}/{y[2:]}"
    
    consolidated_proj.append({
        'mes': ym,
        'label': lbl,
        'vindi_previsto': v_prev,
        'asaas_previsto': a_prev,
        'total_previsto': tot_prev,
        'vindi_realizado': v_real,
        'asaas_realizado': a_real,
        'total_realizado': tot_real
    })
    print(f"[{ym} - {lbl}] Total Previsto: R$ {tot_prev:,.2f} (Vindi: {v_prev:,.2f} + Asaas: {a_prev:,.2f}) | Realizado: R$ {tot_real:,.2f}")

# Future months (excluding current month 2026-09)
future_months = [p for p in consolidated_proj if p['mes'] > '2026-09']

proj_1m_out = future_months[0]['total_previsto'] if len(future_months) > 0 else 0
proj_3m_trim = sum(p['total_previsto'] for p in future_months[:3])
proj_6m_sem = sum(p['total_previsto'] for p in future_months[:6])
proj_12m_ano = sum(p['total_previsto'] for p in future_months[:12])

print("\n=== EXECUTIVE G1 PROJECTIONS (FUTURE MONTHS FROM OUT/26) ===")
print(f"Card 1 - Mês Vigente (Set/26) Realizado: R$ {consolidated_proj[0]['total_realizado']:,.2f}")
print(f"Card 1 - Mês Vigente (Set/26) A Vencer: R$ {consolidated_proj[0]['total_previsto']:,.2f}")
print(f"Card 1 - Mês Vigente (Set/26) Total Previsto: R$ {(consolidated_proj[0]['total_realizado'] + consolidated_proj[0]['total_previsto']):,.2f}")
print(f"Card 5 - Projeção Próximo Mês (Out/26 / M+1): R$ {proj_1m_out:,.2f}")
print(f"Card 6 - Projeção 3 Meses (Trimestre / Out-Dez): R$ {proj_3m_trim:,.2f}")
print(f"Card 7 - Projeção 6 Meses (Semestre / Out-Mar): R$ {proj_6m_sem:,.2f}")
print(f"Card 8 - Projeção 12 Meses (Anual / Out-Set): R$ {proj_12m_ano:,.2f}")

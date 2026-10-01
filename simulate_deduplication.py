import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    a_kpis = data.get('financeiro_asaas', {}).get('kpis', {})
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])
    
    print("CURRENT Asaas KPIs:")
    print("  total_em_atraso:", a_kpis.get('total_em_atraso'))
    print("  qtd_em_atraso:", a_kpis.get('qtd_em_atraso'))
    
    # Apply the rule
    # 1. Group by customer and order
    by_cust = {}
    for f in a_fat:
        cid = f.get('email') or f.get('aluno')
        desc = f.get('description', '')
        m_num = re.search(r'#(\d+)', desc)
        order = m_num.group(1) if m_num else f.get('id')
        by_cust.setdefault(cid, {}).setdefault(order, []).append(f)
        
    filtered_faturas = []
    excluded_orders = []
    
    for cid, orders in by_cust.items():
        # Check if customer has any order with confirmed payment
        paid_orders = [ord_id for ord_id, fats in orders.items() if any(x.get('status') in ('pago', 'paid') for x in fats)]
        
        for ord_id, fats in orders.items():
            # If this order has 0 payments AND customer has another order with confirmed payments
            has_payment = any(x.get('status') in ('pago', 'paid') for x in fats)
            if not has_payment and len(paid_orders) > 0:
                # It's an abandoned checkout!
                excluded_orders.append((cid, ord_id, fats[0].get('forma_pagamento'), sum(float(x.get('valor') or 0) for x in fats), len(fats)))
            else:
                filtered_faturas.extend(fats)
                
    print(f"\nExcluded {len(excluded_orders)} abandoned orders:")
    for cid, ord_id, forma, val, cnt in excluded_orders:
        print(f"  {cid} -> Order #{ord_id} ({forma}): {cnt} faturas somando R$ {val:,.2f}")
        
    new_atraso = sum(float(f.get('valor') or 0) for f in filtered_faturas if f.get('status') == 'em_atraso')
    new_qtd_atraso = sum(1 for f in filtered_faturas if f.get('status') == 'em_atraso')
    print(f"\nNEW Asaas Inadimplência:")
    print(f"  total_em_atraso: R$ {new_atraso:,.2f} (era R$ {a_kpis.get('total_em_atraso'):,.2f})")
    print(f"  qtd_em_atraso: {new_qtd_atraso} (era {a_kpis.get('qtd_em_atraso')})")

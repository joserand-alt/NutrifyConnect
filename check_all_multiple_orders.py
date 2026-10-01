import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])
    
    # Group payments by customer and order
    by_cust = {}
    for f in a_fat:
        cid = f.get('email') or f.get('aluno')
        desc = f.get('description', '')
        m_num = re.search(r'#(\d+)', desc)
        order = m_num.group(1) if m_num else 'single'
        
        by_cust.setdefault(cid, {}).setdefault(order, []).append(f)
        
    print("Asaas customers with multiple orders/checkouts:")
    for cid, orders in by_cust.items():
        if len(orders) > 1:
            print(f"\nCustomer: {cid}")
            for ord_id, fats in orders.items():
                pago_cnt = sum(1 for x in fats if x.get('status') in ('pago', 'paid'))
                atraso_cnt = sum(1 for x in fats if x.get('status') == 'em_atraso')
                avencer_cnt = sum(1 for x in fats if x.get('status') in ('a_vencer', 'futuro', 'pending'))
                tot_val = sum(float(x.get('valor') or 0) for x in fats)
                formas = set(x.get('forma_pagamento') for x in fats)
                print(f"  Order #{ord_id} ({','.join(formas)}): {len(fats)} faturas (R$ {tot_val:,.2f}) | {pago_cnt} pagas, {atraso_cnt} atraso, {avencer_cnt} a vencer")

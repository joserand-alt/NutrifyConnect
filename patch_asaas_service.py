import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

ASAAS_SERVICE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py'

with open(ASAAS_SERVICE_PATH, 'r', encoding='utf-8') as f:
    code = f.read()

# Locate insertion point after paid_customer_ids calculation
target_snippet = '''    paid_customer_ids = set()
    for p in payments:
        if p.get("status") in ("RECEIVED", "CONFIRMED"):
            paid_customer_ids.add(p.get("customer"))'''

assert target_snippet in code, "target_snippet not found in asaas_service.py"

dedup_rule = '''
    # Regra inteligente de Deduplicação de Checkouts / Tentativas Abandonadas:
    # Agrupa pagamentos por cliente e número do pedido (#XXXXXX ou installment).
    # Se o cliente possui um pedido com pagamento confirmado (RECEIVED / CONFIRMED),
    # pedidos com ZERO pagamentos (ex: PIX abandonado ou carnê duplicado que não foi pago)
    # são desconsiderados para evitar cobranças fantasmas em atraso ou projeções duplicadas.
    orders_by_cust = {}
    for p in payments:
        cid = p.get("customer", "")
        if cid not in paid_customer_ids:
            continue
        desc = p.get("description") or ""
        m_num = re.search(r'#(\d+)', desc)
        order_key = m_num.group(1) if m_num else (p.get("installment") or p.get("id") or "single")
        orders_by_cust.setdefault(cid, {}).setdefault(order_key, []).append(p)

    valid_payment_ids = set()
    for cid, orders in orders_by_cust.items():
        paid_orders = [ord_k for ord_k, p_list in orders.items() if any(x.get("status") in ("RECEIVED", "CONFIRMED") for x in p_list)]
        for ord_k, p_list in orders.items():
            has_paid = any(x.get("status") in ("RECEIVED", "CONFIRMED") for x in p_list)
            if not has_paid and len(paid_orders) > 0:
                continue
            for x in p_list:
                valid_payment_ids.add(x.get("id"))'''

new_target_snippet = target_snippet + dedup_rule
code = code.replace(target_snippet, new_target_snippet, 1)

# Now update the payment iteration checks
old_loop_check = '''    for p in payments:
        cid = p.get("customer", "")
        # Regra: se o cliente nunca pagou nenhuma fatura, desconsidera do financeiro
        if cid not in paid_customer_ids:
            continue'''

new_loop_check = '''    for p in payments:
        cid = p.get("customer", "")
        # Regra: se o cliente nunca pagou nenhuma fatura, desconsidera do financeiro
        if cid not in paid_customer_ids:
            continue
        if p.get("id") not in valid_payment_ids:
            continue'''

assert old_loop_check in code, "old_loop_check not found in asaas_service.py"
code = code.replace(old_loop_check, new_loop_check, 1)

# Now update projecao_map loop check
old_proj_check = '''    projecao_map = {}
    for p in payments:
        if p.get("customer") not in paid_customer_ids:
            continue
        if p.get("status") == "PENDING":'''

new_proj_check = '''    projecao_map = {}
    for p in payments:
        if p.get("customer") not in paid_customer_ids:
            continue
        if p.get("id") not in valid_payment_ids:
            continue
        if p.get("status") == "PENDING":'''

assert old_proj_check in code, "old_proj_check not found in asaas_service.py"
code = code.replace(old_proj_check, new_proj_check, 1)

with open(ASAAS_SERVICE_PATH, 'w', encoding='utf-8') as f:
    f.write(code)

print("SUCCESS: asaas_service.py updated with abandoned checkout deduplication rule!")

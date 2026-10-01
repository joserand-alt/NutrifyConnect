import os
import re

# ==============================================================================
# 1. Update asaas_service.py
# ==============================================================================
asaas_paths = [
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py',
    r'C:\Users\DELL\Desktop\Acompanhamento de acessos\asaas_service.py'
]

asaas_payment_patch = """        is_received = status_raw in ("RECEIVED", "RECEIVED_IN_CASH")
        is_confirmed = status_raw == "CONFIRMED"

        # Pagamento só é considerado realizado/pago se já foi recebido OU se está confirmado com vencimento até hoje
        is_realized = is_received or (is_confirmed and ((paid_dt and paid_dt.date() <= now.date()) or (due_dt and due_dt.date() <= now.date())))
        is_future = is_confirmed and not is_realized

        if is_realized:
            total_recebido += valor
            total_pagas += 1
            ref_dt = paid_dt or due_dt
            if ref_dt:
                ym = ref_dt.strftime("%Y-%m")
                if ym not in historico_map: historico_map[ym] = {"pago": 0.0, "qtd": 0}
                historico_map[ym]["pago"] += valor
                historico_map[ym]["qtd"] += 1
                if ym == current_ym: recebido_mes += valor
        elif is_future:
            # Parcelas futuras de cartão de crédito vão para projeção no mês do vencimento
            st_fin = "futuro"
            st_label = "Futuro (Cartão)"
            st_color = "#3b82f6"
            st_bg = "rgba(59,130,246,0.1)"
            if due_dt:
                ym = due_dt.strftime("%Y-%m")
                projecao_map[ym] = projecao_map.get(ym, 0.0) + valor
        elif status_raw == "OVERDUE":
            total_em_atraso += valor
            qtd_em_atraso += 1
        elif status_raw == "PENDING":
            if due_dt and due_dt.date() >= now.date():
                ym = due_dt.strftime("%Y-%m")
                projecao_map[ym] = projecao_map.get(ym, 0.0) + valor"""

for ap in asaas_paths:
    if os.path.exists(ap):
        with open(ap, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the status_raw block
        pattern = r'(\s+if status_raw in \("RECEIVED", "CONFIRMED"\):.*?elif status_raw == "OVERDUE":.*?total_em_atraso \+= valor; qtd_em_atraso \+= 1)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + '\n' + asaas_payment_patch + content[match.end():]
            with open(ap, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched {ap}")
        else:
            print(f"Could not match regex in {ap}")

# Also update vindi_service.py to ensure future due dates are not counted as paid cash
vindi_paths = [
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_service.py',
    r'C:\Users\DELL\Desktop\Acompanhamento de acessos\vindi_service.py'
]

vindi_paid_patch = """        if status == 'paid':
            # Se for vencimento futuro sem data de pagamento efetiva, vai para projeção
            is_future_paid = (paid_dt is None) and (due_dt and due_dt.date() > now.date())
            if is_future_paid:
                ym = due_dt.strftime("%Y-%m")
                projecao_mensal_map[ym] = projecao_mensal_map.get(ym, 0.0) + amount_val
            else:
                total_recebido += amount_val
                total_faturas_pagas += 1
                ref_dt = paid_dt or due_dt or _parse_iso(b.get('created_at'))
                if ref_dt:
                    ym = ref_dt.strftime('%Y-%m')
                    if ym not in historico_mensal_map:
                        historico_mensal_map[ym] = {'pago': 0.0, 'qtd': 0}
                    historico_mensal_map[ym]['pago'] += amount_val
                    historico_mensal_map[ym]['qtd'] += 1
                    if ym == current_ym:
                        recebido_mes_atual += amount_val"""

for vp in vindi_paths:
    if os.path.exists(vp):
        with open(vp, 'r', encoding='utf-8') as f:
            content = f.read()
        pattern_v = r'(\s+if status == [\'"]paid[\'"]:.*?if ym == current_ym:.*?recebido_mes_atual \+= amount_val)'
        match_v = re.search(pattern_v, content, re.DOTALL)
        if match_v:
            content = content[:match_v.start()] + '\n' + vindi_paid_patch + content[match_v.end():]
            with open(vp, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched {vp}")
        else:
            print(f"Could not match regex in {vp}")

# Remove caches to force fresh calculation
for cp in [
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json',
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json'
]:
    if os.path.exists(cp):
        os.remove(cp)
        print(f"Removed cache {cp}")

print("Future installments patch applied successfully.")

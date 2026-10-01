import os
import re

# 1. Patch asaas_service.py
asaas_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py'

with open(asaas_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace payment parsing and aggregation in asaas_service.py
old_payment_logic = """        is_received = status_raw in ("RECEIVED", "RECEIVED_IN_CASH")
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

new_payment_logic = """        is_past_or_today = due_dt and (due_dt.date() <= now.date())
        is_received = status_raw in ("RECEIVED", "RECEIVED_IN_CASH")
        
        # Pagamento só é REALIZADO se já foi recebido ou se é CONFIRMED com vencimento até hoje
        if is_received or (status_raw == "CONFIRMED" and is_past_or_today):
            total_recebido += valor
            total_pagas += 1
            ref_dt = (paid_dt if (paid_dt and paid_dt.date() <= now.date()) else None) or due_dt
            if ref_dt:
                ym = ref_dt.strftime("%Y-%m")
                if ym not in historico_map: historico_map[ym] = {"pago": 0.0, "qtd": 0}
                historico_map[ym]["pago"] += valor
                historico_map[ym]["qtd"] += 1
                if ym == current_ym: recebido_mes += valor
            st_fin = "pago"
            st_label = "Pago"
            st_color = "#059669"
            st_bg = "rgba(5,150,105,0.1)"
        elif status_raw == "CONFIRMED" and not is_past_or_today:
            # Parcelas futuras em cartão de crédito -> PROJEÇÃO no mês de vencimento
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
            st_fin = "em_atraso"
            st_label = "Em Atraso"
            st_color = "#e11d48"
            st_bg = "rgba(225,29,72,0.1)"
        elif status_raw == "PENDING":
            if due_dt and due_dt.date() >= now.date():
                ym = due_dt.strftime("%Y-%m")
                projecao_map[ym] = projecao_map.get(ym, 0.0) + valor
            st_fin = "a_vencer"
            st_label = "A Vencer"
            st_color = "#d97706"
            st_bg = "rgba(217,119,6,0.1)" """

if old_payment_logic in code:
    code = code.replace(old_payment_logic, new_payment_logic)
    print("Replaced asaas_service.py payment logic!")
else:
    # try regex replacement
    pattern = r'(\s+is_received = status_raw in \("RECEIVED", "RECEIVED_IN_CASH"\).*?projecao_map\[ym\] = projecao_map\.get\(ym, 0\.0\) \+ valor)'
    match = re.search(pattern, code, re.DOTALL)
    if match:
        code = code[:match.start()] + '\n' + new_payment_logic + code[match.end():]
        print("Replaced asaas_service.py payment logic via regex!")
    else:
        print("Could not find old pattern in asaas_service.py.")

with open(asaas_path, 'w', encoding='utf-8') as f:
    f.write(code)

# Remove caches
for cp in [
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json',
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json'
]:
    if os.path.exists(cp):
        os.remove(cp)
        print(f"Removed cache {cp}")

print("asaas_service.py updated successfully.")

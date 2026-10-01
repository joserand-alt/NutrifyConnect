import os
import re
import json
import calendar
from datetime import datetime, date, timedelta

dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"

# 1. Update asaas_service.py
asaas_path = os.path.join(dash_dir, "asaas_service.py")
with open(asaas_path, "r", encoding="utf-8") as f:
    a_code = f.read()

# Make sure imports are present
if "from datetime import datetime, date, timedelta" not in a_code:
    a_code = "from datetime import datetime, date, timedelta\n" + a_code
if "import calendar" not in a_code:
    a_code = "import calendar\n" + a_code

# Replace calculation
pattern = r"projecao_mensal\.append\(\{\"mes\":ym,\"label\":f\"\{meses_pt\.get\(m,m\)\}/\{y\[2:\]\}\",\"previsto\":round\(projecao_map\[ym\],2\),\"realizado\":round\(realizado,2\)\}\).*?def _fmt\(v\): return f\"R\$ \{v:,\.2f\}\"\.replace\(\",\",\"X\"\)\.replace\(\"\.\",\",\"\)\.replace\(\"X\",\"\.\"\)"

replacement = """projecao_mensal.append({"mes":ym,"label":f"{meses_pt.get(m,m)}/{y[2:]}","previsto":round(projecao_map[ym],2),"realizado":round(realizado,2)})

    mrr = sum(p.get("previsto", 0) for p in projecao_mensal[:2])

    # Calculo preciso Asaas: a vencer no mes vs projecao 30 dias (D+30)
    today = now.date()
    end_of_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    d30_date = today + timedelta(days=30)

    a_vencer_mes_atual = 0.0
    proj_30d = 0.0

    for p in payments:
        if p.get("customer") not in paid_customer_ids or p.get("id") not in valid_payment_ids:
            continue
        if p.get("status") == "PENDING":
            due_dt = _parse_date(p.get("dueDate") or "")
            if due_dt:
                val = float(p.get("value") or 0)
                if today <= due_dt.date() <= end_of_month:
                    a_vencer_mes_atual += val
                if today <= due_dt.date() <= d30_date:
                    proj_30d += val

    if a_vencer_mes_atual == 0.0 and len(projecao_mensal) > 0:
        a_vencer_mes_atual = projecao_mensal[0]['previsto']
    if proj_30d == 0.0:
        proj_30d = mrr

    total_fat = total_recebido + total_em_atraso
    taxa_adimp = round(total_recebido/total_fat*100) if total_fat>0 else 100

    def _fmt(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")"""

a_code_new = re.sub(pattern, replacement, a_code, flags=re.DOTALL)
with open(asaas_path, "w", encoding="utf-8") as f:
    f.write(a_code_new)
print("[Asaas] asaas_service.py patched cleanly!")

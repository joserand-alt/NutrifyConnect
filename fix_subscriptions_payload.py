import os
import json
import re

dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"

# 1. Patch gerador.py to pass subscriptions and data inside financeiro and asaas_financeiro
gerador_path = os.path.join(dash_dir, "gerador.py")
with open(gerador_path, "r", encoding="utf-8") as f:
    g_code = f.read()

# Make sure financeiro_data and asaas_financeiro include subscriptions and data
target = "financeiro_data = vindi_res.get('financeiro', {}) if isinstance(vindi_res, dict) else {}"
replacement = """financeiro_data = vindi_res.get('financeiro', {}) if isinstance(vindi_res, dict) else {}
        if isinstance(vindi_res, dict):
            financeiro_data['subscriptions'] = vindi_res.get('subscriptions', [])
            financeiro_data['data'] = vindi_res.get('data', {})"""

g_code = g_code.replace(target, replacement)

target_asaas = "asaas_financeiro = asaas_res.get('financeiro', {}) if isinstance(asaas_res, dict) else {}"
replacement_asaas = """asaas_financeiro = asaas_res.get('financeiro', {}) if isinstance(asaas_res, dict) else {}
        if isinstance(asaas_res, dict):
            asaas_financeiro['data'] = asaas_res.get('data', {})"""

g_code = g_code.replace(target_asaas, replacement_asaas)

with open(gerador_path, "w", encoding="utf-8") as f:
    f.write(g_code)
print("[1] gerador.py updated to attach subscriptions and data!")

# 2. Patch vindi_service.py to include subscriptions in financeiro_global
vindi_path = os.path.join(dash_dir, "vindi_service.py")
with open(vindi_path, "r", encoding="utf-8") as f:
    v_code = f.read()

if '"subscriptions": subscriptions_list,' not in v_code:
    v_code = v_code.replace(
        '"faturas_tabela": faturas_para_tabela_geral,',
        '"subscriptions": subscriptions_list,\n        "faturas_tabela": faturas_para_tabela_geral,'
    )
    with open(vindi_path, "w", encoding="utf-8") as f:
        f.write(v_code)
    print("[2] vindi_service.py updated with subscriptions in financeiro_global!")

# 3. Update vindi_cache.json
v_cache_path = os.path.join(dash_dir, "vindi_cache.json")
if os.path.exists(v_cache_path):
    with open(v_cache_path, "r", encoding="utf-8") as f:
        vc = json.load(f)
    vc["financeiro"]["subscriptions"] = vc.get("subscriptions", [])
    with open(v_cache_path, "w", encoding="utf-8") as f:
        json.dump(vc, f, ensure_ascii=False, indent=2)
    print("[3] vindi_cache.json updated with subscriptions inside financeiro!")

# 4. Patch template.html to have robust fallbacks for MRR and projections by course
template_path = os.path.join(dash_dir, "template.html")
with open(template_path, "r", encoding="utf-8") as f:
    t_code = f.read()

# Ensure vSubsList falls back to (vindi.subscriptions || DATA.subscriptions || [])
t_code = t_code.replace(
    "const vSubsList = (vindi.subscriptions || []);",
    "const vSubsList = (vindi.subscriptions || (DATA && DATA.financeiro && DATA.financeiro.subscriptions) || []);"
)

with open(template_path, "w", encoding="utf-8") as f:
    f.write(t_code)
print("[4] template.html updated!")

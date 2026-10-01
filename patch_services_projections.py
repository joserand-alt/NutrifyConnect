import json
import re
import os

# =========================================================================
# 1. PATCH vindi_service.py
# =========================================================================
with open('vindi_service.py', 'r', encoding='utf-8') as f:
    v_code = f.read()

# Fix proj_30d, proj_60d, proj_12m and subscriptions return in vindi_service.py
v_target_old = '''    proj_30d = projecao_mensal[0]['previsto'] if len(projecao_mensal) > 0 else mrr_ativo_total
    proj_60d = sum(p['previsto'] for p in projecao_mensal[:2]) if len(projecao_mensal) >= 2 else (mrr_ativo_total * 2)
    proj_12m = mrr_ativo_total * 12'''

v_target_new = '''    # Projeções a partir dos meses futuros (M+1: Out/26 em diante)
    future_proj_months = [p for p in projecao_mensal if p['mes'] > current_ym]
    proj_30d = future_proj_months[0]['previsto'] if len(future_proj_months) > 0 else (projecao_mensal[0]['previsto'] if projecao_mensal else mrr_ativo_total)
    proj_60d = sum(p['previsto'] for p in future_proj_months[:2]) if len(future_proj_months) >= 2 else (mrr_ativo_total * 2)
    proj_3m = sum(p['previsto'] for p in future_proj_months[:3]) if len(future_proj_months) >= 3 else (mrr_ativo_total * 3)
    proj_6m = sum(p['previsto'] for p in future_proj_months[:6]) if len(future_proj_months) >= 6 else (mrr_ativo_total * 6)
    proj_12m = sum(p['previsto'] for p in future_proj_months[:12]) if len(future_proj_months) >= 12 else (mrr_ativo_total * 12)'''

if v_target_old in v_code:
    v_code = v_code.replace(v_target_old, v_target_new)
    print("vindi_service.py KPIs calculation updated.")
else:
    print("WARNING: v_target_old not found in vindi_service.py")

# Also ensure subscriptions list is exported in result
v_fin_old = '''    financeiro_global = {
        "kpis": {
            "total_recebido": round(total_recebido, 2),
            "total_recebido_fmt": f"R$ {total_recebido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "total_faturas_pagas": total_faturas_pagas,
            "recebido_mes_atual": round(recebido_mes_atual, 2),
            "recebido_mes_atual_fmt": f"R$ {recebido_mes_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "total_em_atraso": round(total_em_atraso, 2),
            "total_em_atraso_fmt": f"R$ {total_em_atraso:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "qtd_em_atraso": qtd_em_atraso,
            "mrr_ativo": round(mrr_ativo_total, 2),
            "mrr_ativo_fmt": f"R$ {mrr_ativo_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "projecao_30d": round(proj_30d, 2),
            "projecao_30d_fmt": f"R$ {proj_30d:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "projecao_60d": round(proj_60d, 2),
            "projecao_60d_fmt": f"R$ {proj_60d:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "projecao_12m": round(proj_12m, 2),
            "projecao_12m_fmt": f"R$ {proj_12m:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "taxa_adimplencia": taxa_adimp
        },
        "historico_mensal": historico_mensal,
        "projecao_mensal": projecao_mensal,
        "faturas_tabela": faturas_para_tabela_geral[:300]
    }'''

v_fin_new = '''    subs_list_exported = list(students_vindi.values())

    financeiro_global = {
        "kpis": {
            "total_recebido": round(total_recebido, 2),
            "total_recebido_fmt": f"R$ {total_recebido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "total_faturas_pagas": total_faturas_pagas,
            "recebido_mes_atual": round(recebido_mes_atual, 2),
            "recebido_mes_atual_fmt": f"R$ {recebido_mes_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "a_vencer_mes_atual": round(projecao_mensal[0]['previsto'] if projecao_mensal and projecao_mensal[0]['mes'] == current_ym else 0.0, 2),
            "total_em_atraso": round(total_em_atraso, 2),
            "total_em_atraso_fmt": f"R$ {total_em_atraso:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "qtd_em_atraso": qtd_em_atraso,
            "mrr_ativo": round(mrr_ativo_total, 2),
            "mrr_ativo_fmt": f"R$ {mrr_ativo_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "projecao_30d": round(proj_30d, 2),
            "projecao_30d_fmt": f"R$ {proj_30d:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "projecao_60d": round(proj_60d, 2),
            "projecao_60d_fmt": f"R$ {proj_60d:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "proj_3m": round(proj_3m, 2),
            "proj_6m": round(proj_6m, 2),
            "projecao_12m": round(proj_12m, 2),
            "projecao_12m_fmt": f"R$ {proj_12m:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "taxa_adimplencia": taxa_adimp
        },
        "historico_mensal": historico_mensal,
        "projecao_mensal": projecao_mensal,
        "projecao_mensal_map": projecao_mensal_map,
        "subscriptions": subs_list_exported,
        "faturas_tabela": faturas_para_tabela_geral
    }'''

if v_fin_old in v_code:
    v_code = v_code.replace(v_fin_old, v_fin_new)
    print("vindi_service.py financeiro_global updated.")
else:
    print("WARNING: v_fin_old not found in vindi_service.py")

# Update return result
v_res_old = '''    result = {
        "cached_at": now.isoformat(),
        "total_matched": len(students_vindi),
        "data": students_vindi,
        "financeiro": financeiro_global
    }'''

v_res_new = '''    result = {
        "cached_at": now.isoformat(),
        "total_matched": len(students_vindi),
        "data": students_vindi,
        "subscriptions": subs_list_exported,
        "financeiro": financeiro_global
    }'''

if v_res_old in v_code:
    v_code = v_code.replace(v_res_old, v_res_new)
    print("vindi_service.py return result updated.")

with open('vindi_service.py', 'w', encoding='utf-8') as f:
    f.write(v_code)

# =========================================================================
# 2. PATCH asaas_service.py
# =========================================================================
with open('asaas_service.py', 'r', encoding='utf-8') as f:
    a_code = f.read()

# Update asaas_service.py financeiro_global to include subscriptions & projecao_mensal_map
a_fin_old = '''    financeiro_global = {
        "fonte": "Asaas",
        "kpis": {
            "total_recebido": round(total_recebido, 2),
            "total_recebido_fmt": f"R$ {total_recebido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "total_faturas_pagas": total_pagas,
            "recebido_mes_atual": round(recebido_mes, 2),
            "recebido_mes_fmt": f"R$ {recebido_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "a_vencer_mes_atual": round(a_vencer_mes_atual, 2),
            "a_vencer_mes_atual_fmt": f"R$ {a_vencer_mes_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "total_em_atraso": round(total_em_atraso, 2),
            "total_em_atraso_fmt": f"R$ {total_em_atraso:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "qtd_em_atraso": qtd_em_atraso,
            "mrr_ativo": round(mrr_ativo, 2),
            "mrr_ativo_fmt": f"R$ {mrr_ativo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "projecao_30d": round(projecao_30d, 2),
            "projecao_30d_fmt": f"R$ {projecao_30d:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "taxa_adimplencia": taxa_adimp,
        },
        "historico_mensal": historico_mensal,
        "projecao_mensal": projecao_mensal,
        "faturas_tabela": faturas_tabela,
        "faturas_recentes": faturas_tabela[:200],
    }'''

a_fin_new = '''    subs_list_asaas = list(students_asaas.values())

    future_proj_months_a = [p for p in projecao_mensal if p['mes'] > current_ym]
    proj_30d_a = future_proj_months_a[0]['previsto'] if len(future_proj_months_a) > 0 else (projecao_mensal[0]['previsto'] if projecao_mensal else mrr_ativo)
    proj_3m_a = sum(p['previsto'] for p in future_proj_months_a[:3]) if len(future_proj_months_a) >= 3 else (mrr_ativo * 3)
    proj_6m_a = sum(p['previsto'] for p in future_proj_months_a[:6]) if len(future_proj_months_a) >= 6 else (mrr_ativo * 6)
    proj_12m_a = sum(p['previsto'] for p in future_proj_months_a[:12]) if len(future_proj_months_a) >= 12 else (mrr_ativo * 12)

    financeiro_global = {
        "fonte": "Asaas",
        "kpis": {
            "total_recebido": round(total_recebido, 2),
            "total_recebido_fmt": f"R$ {total_recebido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "total_faturas_pagas": total_pagas,
            "recebido_mes_atual": round(recebido_mes, 2),
            "recebido_mes_fmt": f"R$ {recebido_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "a_vencer_mes_atual": round(a_vencer_mes_atual, 2),
            "a_vencer_mes_atual_fmt": f"R$ {a_vencer_mes_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "total_em_atraso": round(total_em_atraso, 2),
            "total_em_atraso_fmt": f"R$ {total_em_atraso:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "qtd_em_atraso": qtd_em_atraso,
            "mrr_ativo": round(mrr_ativo, 2),
            "mrr_ativo_fmt": f"R$ {mrr_ativo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "projecao_30d": round(proj_30d_a, 2),
            "projecao_30d_fmt": f"R$ {proj_30d_a:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "proj_3m": round(proj_3m_a, 2),
            "proj_6m": round(proj_6m_a, 2),
            "projecao_12m": round(proj_12m_a, 2),
            "taxa_adimplencia": taxa_adimp,
        },
        "historico_mensal": historico_mensal,
        "projecao_mensal": projecao_mensal,
        "projecao_mensal_map": projecao_map,
        "subscriptions": subs_list_asaas,
        "faturas_tabela": faturas_tabela,
        "faturas_recentes": faturas_tabela[:200],
    }'''

if a_fin_old in a_code:
    a_code = a_code.replace(a_fin_old, a_fin_new)
    print("asaas_service.py financeiro_global updated.")
else:
    print("WARNING: a_fin_old not found in asaas_service.py")

a_res_old = '''result = {"_cached_at": datetime.now().isoformat(), "data": students_asaas, "financeiro": financeiro_global}'''
a_res_new = '''result = {"_cached_at": datetime.now().isoformat(), "data": students_asaas, "subscriptions": subs_list_asaas, "financeiro": financeiro_global}'''
if a_res_old in a_code:
    a_code = a_code.replace(a_res_old, a_res_new)
    print("asaas_service.py return result updated.")

with open('asaas_service.py', 'w', encoding='utf-8') as f:
    f.write(a_code)

print("vindi_service.py and asaas_service.py patched successfully!")

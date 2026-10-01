import os
import re
import json
import calendar
from datetime import datetime, date, timedelta

def main():
    dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"
    
    # 1. Patch vindi_service.py
    vindi_path = os.path.join(dash_dir, "vindi_service.py")
    if os.path.exists(vindi_path):
        with open(vindi_path, "r", encoding="utf-8") as f:
            v_code = f.read()

        if "import calendar" not in v_code:
            v_code = "import calendar\n" + v_code

        # Replace calculation block
        pattern = r"proj_30d\s*=\s*projecao_mensal\[0\]\['previsto'\].*?financeiro_global\s*=\s*\{\s*\"kpis\":\s*\{.*?(?=\"historico_mensal\":)"
        
        replacement = """# Calculo preciso: a vencer no mes vigente vs projecao 30 dias corridos (D+30)
    today = now.date()
    end_of_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    d30_date = today + timedelta(days=30)

    a_vencer_mes_atual = 0.0
    proj_30d = 0.0

    for sub_item in subscriptions_list:
        if sub_item.get('status_financeiro') == 'adimplente':
            price_val = float(sub_item.get('valor_parcela') or 0.0)
            prox_fmt = sub_item.get('proximo_vencimento')
            if prox_fmt:
                try:
                    p_dt = datetime.strptime(prox_fmt, '%d/%m/%Y').date()
                    if today <= p_dt <= end_of_month:
                        a_vencer_mes_atual += price_val
                    if today <= p_dt <= d30_date:
                        proj_30d += price_val
                except:
                    a_vencer_mes_atual += price_val
                    proj_30d += price_val
            else:
                a_vencer_mes_atual += price_val
                proj_30d += price_val

    if a_vencer_mes_atual == 0.0 and len(projecao_mensal) > 0:
        a_vencer_mes_atual = projecao_mensal[0]['previsto']
    if proj_30d == 0.0:
        proj_30d = mrr_ativo_total

    proj_60d = sum(p['previsto'] for p in projecao_mensal[:2]) if len(projecao_mensal) >= 2 else (mrr_ativo_total * 2)
    proj_12m = mrr_ativo_total * 12
    total_faturado = total_recebido + total_em_atraso
    taxa_adimp = round((total_recebido / total_faturado * 100)) if total_faturado > 0 else 100

    financeiro_global = {
        "kpis": {
            "total_recebido": round(total_recebido, 2),
            "total_recebido_fmt": f"R$ {total_recebido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "total_faturas_pagas": total_faturas_pagas,
            "recebido_mes_atual": round(recebido_mes_atual, 2),
            "recebido_mes_atual_fmt": f"R$ {recebido_mes_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "a_vencer_mes_atual": round(a_vencer_mes_atual, 2),
            "a_vencer_mes_atual_fmt": f"R$ {a_vencer_mes_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
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
        """
        v_code_new = re.sub(pattern, replacement, v_code, flags=re.DOTALL)
        with open(vindi_path, "w", encoding="utf-8") as f:
            f.write(v_code_new)
        print("[1] vindi_service.py updated successfully!")

    # 2. Patch asaas_service.py
    asaas_path = os.path.join(dash_dir, "asaas_service.py")
    if os.path.exists(asaas_path):
        with open(asaas_path, "r", encoding="utf-8") as f:
            a_code = f.read()

        if "import calendar" not in a_code:
            a_code = "import calendar\n" + a_code

        # Update asaas calc
        asaas_pattern = r"proj_30d\s*=\s*projecao_mensal\[0\]\[\"previsto\"\].*?financeiro_global\s*=\s*\{\s*\"fonte\":\s*\"Asaas\",\s*\"kpis\":\s*\{.*?(?=\"historico_mensal\":)"
        
        asaas_replacement = """# Calculo preciso Asaas: a vencer no mes vs projecao 30 dias (D+30)
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

    def _fmt(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

    financeiro_global = {
        "fonte": "Asaas",
        "kpis": {
            "total_recebido": round(total_recebido,2), "total_recebido_fmt": _fmt(total_recebido),
            "total_faturas_pagas": total_pagas,
            "recebido_mes_atual": round(recebido_mes,2), "recebido_mes_fmt": _fmt(recebido_mes),
            "a_vencer_mes_atual": round(a_vencer_mes_atual,2), "a_vencer_mes_atual_fmt": _fmt(a_vencer_mes_atual),
            "total_em_atraso": round(total_em_atraso,2), "total_em_atraso_fmt": _fmt(total_em_atraso),
            "qtd_em_atraso": qtd_em_atraso,
            "mrr_ativo": round(mrr,2), "mrr_ativo_fmt": _fmt(mrr),
            "projecao_30d": round(proj_30d,2), "projecao_30d_fmt": _fmt(proj_30d),
            "taxa_adimplencia": taxa_adimp,
        },
        """
        a_code_new = re.sub(asaas_pattern, asaas_replacement, a_code, flags=re.DOTALL)
        with open(asaas_path, "w", encoding="utf-8") as f:
            f.write(a_code_new)
        print("[2] asaas_service.py updated successfully!")

    # 3. Update vindi_cache.json and asaas_cache.json
    v_cache_path = os.path.join(dash_dir, "vindi_cache.json")
    if os.path.exists(v_cache_path):
        with open(v_cache_path, "r", encoding="utf-8") as f:
            vc = json.load(f)

        today = date.today()
        end_of_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        d30_date = today + timedelta(days=30)
        v_a_vencer = 0.0
        v_proj_30d = 0.0
        v_mrr = 0.0

        for sub in vc.get("subscriptions", []):
            if sub.get("status_financeiro") == "adimplente":
                price = float(sub.get("valor_parcela") or 0.0)
                v_mrr += price
                prox_fmt = sub.get("proximo_vencimento")
                if prox_fmt:
                    try:
                        p_dt = datetime.strptime(prox_fmt, "%d/%m/%Y").date()
                        if today <= p_dt <= end_of_month:
                            v_a_vencer += price
                        if today <= p_dt <= d30_date:
                            v_proj_30d += price
                    except:
                        v_a_vencer += price
                        v_proj_30d += price
                else:
                    v_a_vencer += price
                    v_proj_30d += price

        vc["financeiro"]["kpis"]["a_vencer_mes_atual"] = round(v_a_vencer, 2)
        vc["financeiro"]["kpis"]["a_vencer_mes_atual_fmt"] = f"R$ {v_a_vencer:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        vc["financeiro"]["kpis"]["projecao_30d"] = round(v_proj_30d, 2)
        vc["financeiro"]["kpis"]["projecao_30d_fmt"] = f"R$ {v_proj_30d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        vc["financeiro"]["kpis"]["mrr_ativo"] = round(v_mrr, 2)
        vc["financeiro"]["kpis"]["mrr_ativo_fmt"] = f"R$ {v_mrr:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        with open(v_cache_path, "w", encoding="utf-8") as f:
            json.dump(vc, f, ensure_ascii=False, indent=2)
        print("[3] vindi_cache.json updated successfully!")

    a_cache_path = os.path.join(dash_dir, "asaas_cache.json")
    if os.path.exists(a_cache_path):
        with open(a_cache_path, "r", encoding="utf-8") as f:
            ac = json.load(f)

        today = date.today()
        end_of_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        d30_date = today + timedelta(days=30)
        a_a_vencer = 0.0
        a_proj_30d = 0.0

        for fat in ac.get("financeiro", {}).get("faturas_tabela", []):
            st = fat.get("status")
            due_iso = fat.get("vencimento_iso")
            val = float(fat.get("valor") or 0.0)
            if st in ["pendente", "PENDING", "a_vencer"]:
                if due_iso:
                    try:
                        d_dt = datetime.strptime(due_iso[:10], "%Y-%m-%d").date()
                        if today <= d_dt <= end_of_month:
                            a_a_vencer += val
                        if today <= d_dt <= d30_date:
                            a_proj_30d += val
                    except:
                        pass

        ac["financeiro"]["kpis"]["a_vencer_mes_atual"] = round(a_a_vencer, 2)
        ac["financeiro"]["kpis"]["a_vencer_mes_atual_fmt"] = f"R$ {a_a_vencer:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        ac["financeiro"]["kpis"]["projecao_30d"] = round(a_proj_30d, 2)
        ac["financeiro"]["kpis"]["projecao_30d_fmt"] = f"R$ {a_proj_30d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        with open(a_cache_path, "w", encoding="utf-8") as f:
            json.dump(ac, f, ensure_ascii=False, indent=2)
        print("[4] asaas_cache.json updated successfully!")

    # 4. Update template.html
    template_path = os.path.join(dash_dir, "template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        t_code = f.read()

    # 4.1 Update financial totalizers in drawExecView
    old_tot = """    const recRealizadaTotal = (Number(vKpis.total_recebido) || 0) + (Number(aKpis.total_recebido) || 0);
    const recMesAtual = (Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || 0);
    const mrrConsolidado = (Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0);
    const proj30d = (Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0);
    const proj12m = (Number(vKpis.projecao_12m) || 2663789.16);"""

    new_tot = """    const recRealizadaTotal = (Number(vKpis.total_recebido) || 0) + (Number(aKpis.total_recebido) || 0);
    const recMesAtual = (Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || Number(aKpis.recebido_mes) || 0);
    const aVencerMesVigente = (Number(vKpis.a_vencer_mes_atual) || Number(vKpis.projecao_mensal?.[0]?.previsto) || 0) + (Number(aKpis.a_vencer_mes_atual) || Number(aKpis.projecao_mensal?.[0]?.previsto) || 0);
    const totalPrevistoMesVigente = recMesAtual + aVencerMesVigente;
    const mrrConsolidado = (Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0);
    const proj30d = (Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0);
    const proj12m = (Number(vKpis.projecao_12m) || 2663789.16);"""

    t_code = t_code.replace(old_tot, new_tot)

    # 4.2 Update Card 1 subtitle to use aVencerMesVigente
    t_code = re.sub(
        r'(\<\!-- CARD 1: RECEITA MÊS VIGENTE --\>.*?\<div class="exec-card-sub"\>)\s*<b>\$\{fM\(recMesAtual\)\}<\/b> realizado \(\$\{pctRealizadoMes\}%\) \+ <b>\$\{fM\(proj30d\)\}<\/b> a vencer em \$\{labelMesVigente\}',
        r'\1\n              <b>${fM(recMesAtual)}</b> realizado (${pctRealizadoMes}%) + <b>${fM(aVencerMesVigente)}</b> a vencer em ${labelMesVigente}',
        t_code,
        flags=re.DOTALL
    )

    # 4.3 Update Card 5 to use proj30d ($D+30$) and clear label/pill/sub
    old_card5 = """          <!-- CARD 5: PROJEÇÃO 1 MÊS (30 DIAS) -->
          <div class="exec-card" style="background:rgba(2,132,199,0.02); border-left:3px solid #0284c7">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 1 Mês (30 dias)</span>
              <span class="exec-pill pill-blue">Ciclo Mensal</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(mrrConsolidado)}</div>
            <div class="exec-card-sub">Faturamento projetado de 1 ciclo mensal completo da carteira ativa (MRR)</div>
          </div>"""

    new_card5 = """          <!-- CARD 5: PROJEÇÃO 1 MÊS (30 DIAS) -->
          <div class="exec-card" style="background:rgba(2,132,199,0.02); border-left:3px solid #0284c7">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 1 Mês (30 dias)</span>
              <span class="exec-pill pill-blue">Próximos 30d (D+30)</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(proj30d)}</div>
            <div class="exec-card-sub">Faturas e parcelas agendadas para os próximos 30 dias corridos (D+30)</div>
          </div>"""

    if old_card5 in t_code:
        t_code = t_code.replace(old_card5, new_card5)
    else:
        # regex replacement for Card 5
        card5_pat = r"(\<\!-- CARD 5: PROJEÇÃO 1 MÊS \(30 DIAS\) --\>.*?\<div class=\"exec-card-val\" style=\"color:#0284c7\"\>)\$\{fM\([a-zA-Z0-9_]+\)\}(\<\/div\>\s*\<div class=\"exec-card-sub\"\>).*?(\<\/div\>)"
        t_code = re.sub(
            card5_pat,
            r'\1${fM(proj30d)}\2Faturas e parcelas agendadas para os próximos 30 dias corridos (D+30)\3',
            t_code,
            flags=re.DOTALL
        )

    with open(template_path, "w", encoding="utf-8") as f:
        f.write(t_code)
    print("[5] template.html updated successfully!")

if __name__ == "__main__":
    main()

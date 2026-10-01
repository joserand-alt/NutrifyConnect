import os
import re
import json
import calendar
from datetime import datetime, date, timedelta

dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"

# 1. Update vindi_service.py to project full 18 future months using remaining contract cycles
vindi_path = os.path.join(dash_dir, "vindi_service.py")
with open(vindi_path, "r", encoding="utf-8") as f:
    v_code = f.read()

# Make sure imports are present
if "from datetime import datetime, date, timedelta" not in v_code:
    v_code = "from datetime import datetime, date, timedelta\nimport calendar\n" + v_code

# Replace projecao_mensal calculation in vindi_service.py
old_vindi_proj_block = r"sorted_proj_ym\s*=\s*sorted\(\[ym for ym in projecao_mensal_map\.keys\(\) if ym >= current_ym\]\).*?financeiro_global\s*=\s*\{"

new_vindi_proj_block = """# Gerar horizonte de 18 meses futuros para projecao contratual real
    today = now.date()
    current_ym = today.strftime('%Y-%m')
    end_of_current_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    d30_date = today + timedelta(days=30)

    future_months = []
    cur_y = today.year
    cur_m = today.month
    for _ in range(18):
        future_months.append(f"{cur_y}-{cur_m:02d}")
        cur_m += 1
        if cur_m > 12:
            cur_m = 1
            cur_y += 1

    projecao_vindi_map = {ym: 0.0 for ym in future_months}
    a_vencer_mes_atual = 0.0
    proj_30d = 0.0

    for sub_data in subscriptions_list:
        if sub_data.get('status_financeiro') == 'adimplente':
            price = float(sub_data.get('valor_parcela') or 0.0)
            plano = (sub_data.get('plano') or '').upper()
            total_cycles = 18
            if '24' in plano: total_cycles = 24
            elif '12' in plano or 'ANUAL' in plano: total_cycles = 12
            elif '6' in plano or 'SEMESTRAL' in plano: total_cycles = 6

            faturas_aluno = sub_data.get('faturas', [])
            paid_count = sum(1 for f in faturas_aluno if f.get('status') in ['paid', 'pago'])
            remaining = max(0, total_cycles - paid_count)

            prox = sub_data.get('proximo_vencimento')
            due_in_current_month = False
            if prox:
                try:
                    p_dt = datetime.strptime(prox, '%d/%m/%Y').date()
                    if today <= p_dt <= end_of_current_month:
                        due_in_current_month = True
                        a_vencer_mes_atual += price
                    if today <= p_dt <= d30_date:
                        proj_30d += price
                except:
                    due_in_current_month = True
                    a_vencer_mes_atual += price
                    proj_30d += price
            else:
                due_in_current_month = True
                a_vencer_mes_atual += price
                proj_30d += price

            if due_in_current_month:
                projecao_vindi_map[current_ym] += price
                for m_idx in range(1, min(remaining, len(future_months))):
                    projecao_vindi_map[future_months[m_idx]] += price
            else:
                for m_idx in range(1, min(remaining + 1, len(future_months))):
                    projecao_vindi_map[future_months[m_idx]] += price

    projecao_mensal = []
    for ym in future_months:
        y, m = ym.split('-')
        lbl = f"{meses_pt.get(m, m)}/{y[2:]}"
        projecao_mensal.append({
            "mes": ym,
            "label": lbl,
            "previsto": round(projecao_vindi_map[ym], 2)
        })

    proj_3m_vindi = sum(p['previsto'] for p in projecao_mensal[:3])
    proj_6m_vindi = sum(p['previsto'] for p in projecao_mensal[:6])
    proj_12m_vindi = sum(p['previsto'] for p in projecao_mensal[:12])
    total_faturado = total_recebido + total_em_atraso
    taxa_adimp = round((total_recebido / total_faturado * 100)) if total_faturado > 0 else 100

    financeiro_global = {"""

v_code_new = re.sub(old_vindi_proj_block, new_vindi_proj_block, v_code, flags=re.DOTALL)
with open(vindi_path, "w", encoding="utf-8") as f:
    f.write(v_code_new)
print("[1] vindi_service.py updated with 18-month contract projection!")

# 2. Update vindi_cache.json with full 18-month projections
raw_bills_path = os.path.join(dash_dir, "all_vindi_bills_raw.json")
with open(raw_bills_path, "r", encoding="utf-8") as f:
    bills = json.load(f)

paid_bills_by_sub = {}
for b in bills:
    sub_id = b.get("subscription_id")
    st = b.get("status")
    if sub_id and st in ["paid", "pago"]:
        paid_bills_by_sub[sub_id] = paid_bills_by_sub.get(sub_id, 0) + 1

v_cache_path = os.path.join(dash_dir, "vindi_cache.json")
with open(v_cache_path, "r", encoding="utf-8") as f:
    vc = json.load(f)

today = date.today()
current_ym = today.strftime('%Y-%m')
end_of_current_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
d30_date = today + timedelta(days=30)
meses_pt = {'01':'Jan','02':'Fev','03':'Mar','04':'Abr','05':'Mai','06':'Jun','07':'Jul','08':'Ago','09':'Set','10':'Out','11':'Nov','12':'Dez'}

future_months = []
cur_y = today.year
cur_m = today.month
for _ in range(18):
    future_months.append(f"{cur_y}-{cur_m:02d}")
    cur_m += 1
    if cur_m > 12:
        cur_m = 1
        cur_y += 1

projecao_vindi_map = {ym: 0.0 for ym in future_months}
a_vencer_mes_atual = 0.0
proj_30d = 0.0
mrr_vindi = 0.0

for sub in vc.get("subscriptions", []):
    if sub.get("status_financeiro") == "adimplente":
        sub_id = sub.get("subscription_id")
        price = float(sub.get("valor_parcela") or 0.0)
        mrr_vindi += price
        plano = (sub.get("plano") or "").upper()
        total_cycles = 18
        if "24" in plano: total_cycles = 24
        elif "12" in plano or "ANUAL" in plano: total_cycles = 12
        elif "6" in plano or "SEMESTRAL" in plano: total_cycles = 6

        faturas = sub.get("faturas", [])
        paid_count = sum(1 for f in faturas if f.get("status") in ["paid", "pago"])
        if paid_count == 0 and sub_id in paid_bills_by_sub:
            paid_count = paid_bills_by_sub[sub_id]
        remaining = max(0, total_cycles - paid_count)

        prox = sub.get("proximo_vencimento")
        due_in_current_month = False
        if prox:
            try:
                p_dt = datetime.strptime(prox, "%d/%m/%Y").date()
                if today <= p_dt <= end_of_current_month:
                    due_in_current_month = True
                    a_vencer_mes_atual += price
                if today <= p_dt <= d30_date:
                    proj_30d += price
            except:
                due_in_current_month = True
                a_vencer_mes_atual += price
                proj_30d += price
        else:
            due_in_current_month = True
            a_vencer_mes_atual += price
            proj_30d += price

        if due_in_current_month:
            projecao_vindi_map[current_ym] += price
            for m_idx in range(1, min(remaining, len(future_months))):
                projecao_vindi_map[future_months[m_idx]] += price
        else:
            for m_idx in range(1, min(remaining + 1, len(future_months))):
                projecao_vindi_map[future_months[m_idx]] += price

projecao_mensal_v = []
for ym in future_months:
    y, m = ym.split("-")
    lbl = f"{meses_pt.get(m, m)}/{y[2:]}"
    projecao_mensal_v.append({
        "mes": ym,
        "label": lbl,
        "previsto": round(projecao_vindi_map[ym], 2)
    })

vc["financeiro"]["projecao_mensal"] = projecao_mensal_v
vc["financeiro"]["kpis"]["a_vencer_mes_atual"] = round(a_vencer_mes_atual, 2)
vc["financeiro"]["kpis"]["a_vencer_mes_atual_fmt"] = f"R$ {a_vencer_mes_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
vc["financeiro"]["kpis"]["projecao_30d"] = round(proj_30d, 2)
vc["financeiro"]["kpis"]["projecao_30d_fmt"] = f"R$ {proj_30d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
vc["financeiro"]["kpis"]["mrr_ativo"] = round(mrr_vindi, 2)
vc["financeiro"]["kpis"]["mrr_ativo_fmt"] = f"R$ {mrr_vindi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

with open(v_cache_path, "w", encoding="utf-8") as f:
    json.dump(vc, f, ensure_ascii=False, indent=2)
print("[2] vindi_cache.json updated with 18-month monthly projections!")

# 3. Update asaas_cache.json
a_cache_path = os.path.join(dash_dir, "asaas_cache.json")
with open(a_cache_path, "r", encoding="utf-8") as f:
    ac = json.load(f)

projecao_asaas_map = {ym: 0.0 for ym in future_months}
for f in ac.get("financeiro", {}).get("faturas_tabela", []):
    st = f.get("status")
    val = float(f.get("valor") or 0.0)
    venc = f.get("vencimento_iso") or f.get("vencimento") or ""
    if st in ["pendente", "pending", "a_vencer", "PENDING"]:
        if venc:
            try:
                d_dt = datetime.strptime(venc[:10], "%Y-%m-%d").date() if "-" in venc else datetime.strptime(venc[:10], "%d/%m/%Y").date()
                ym = d_dt.strftime("%Y-%m")
                if ym in projecao_asaas_map and d_dt >= today:
                    projecao_asaas_map[ym] += val
            except:
                pass

projecao_mensal_a = []
for ym in future_months:
    y, m = ym.split("-")
    lbl = f"{meses_pt.get(m, m)}/{y[2:]}"
    projecao_mensal_a.append({
        "mes": ym,
        "label": lbl,
        "previsto": round(projecao_asaas_map[ym], 2),
        "realizado": 0.0
    })

ac["financeiro"]["projecao_mensal"] = projecao_mensal_a
with open(a_cache_path, "w", encoding="utf-8") as f:
    json.dump(ac, f, ensure_ascii=False, indent=2)
print("[3] asaas_cache.json updated with matching 18-month projections!")

# 4. Patch template.html so getFinData() and drawFinanceiro use the unified 18-month contract model
template_path = os.path.join(dash_dir, "template.html")
with open(template_path, "r", encoding="utf-8") as f:
    t_code = f.read()

# Ensure getFinData builds the unified 18-month monthly projections cleanly
old_get_fin = r"function getFinData\(source\) \{.*?return \{\s*fonte: 'Consolidado \(Vindi & Asaas\)',.*?faturas_tabela: faturas_tabela\s*\};\s*\}"

new_get_fin = """function getFinData(source) {
    const src = source || (FILTER && FILTER.fonte_fin) || 'all';
    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : null;
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : null;

    const vfaturas = (vindi && vindi.faturas_tabela) || [];
    const afaturas = (asaas && asaas.faturas_tabela) || [];

    const activeCurso = (FILTER && FILTER.curso && FILTER.curso !== 'all') ? FILTER.curso : null;

    if (activeCurso) {
        function buildCourseSpecificFin(faturas, label) {
            const courseFaturas = faturas.filter(f => {
                const c = resolveCanonicalCourse(f.curso || (DATA && DATA.students && DATA.students.find(s => s.email === f.email)?.curso) || '');
                return c === activeCurso;
            });
            
            let totRec = 0;
            let totAtraso = 0;
            let qtdAtraso = 0;
            let fatPagas = 0;
            let recMes = 0;
            const now = new Date();
            const currentYm = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');

            const histMap = {};
            courseFaturas.forEach(f => {
                const val = Number(f.valor) || 0;
                const pIso = f.data_pagamento_iso || f.data_pagamento || '';
                const vIso = f.vencimento_iso || f.vencimento || '';
                
                if (f.status === 'paid' || f.status === 'pago' || f.status === 'confirmed' || f.status === 'received') {
                    totRec += val;
                    fatPagas++;
                    const refYm = pIso.slice(0, 7) || vIso.slice(0, 7);
                    if (refYm) {
                        if (!histMap[refYm]) histMap[refYm] = { mes: refYm, label: formatMesAno(refYm), pago: 0 };
                        histMap[refYm].pago += val;
                    }
                    if (refYm === currentYm) recMes += val;
                } else if (f.status === 'em_atraso' || f.status === 'overdue') {
                    totAtraso += val;
                    qtdAtraso++;
                }
            });

            // Mapear faturas e assinaturas ativas do curso específico
            const vSubsList = (vindi && vindi.subscriptions) || [];
            const courseSubs = vSubsList.filter(sub => {
                const c = resolveCanonicalCourse(sub.curso || (DATA && DATA.students && DATA.students.find(s=>s.email===sub.customer_email)?.curso) || '');
                return c === activeCurso && sub.status_financeiro === 'adimplente';
            });
            const courseMrrVindi = courseSubs.reduce((acc, sub) => acc + (Number(sub.valor_parcela) || 0), 0);

            let courseMrrAsaas = 0;
            Object.values((asaas && asaas.data) || {}).forEach(stInfo => {
                const c = resolveCanonicalCourse(stInfo.curso || '');
                if (c === activeCurso && stInfo.status_financeiro === 'adimplente') {
                    courseMrrAsaas += (Number(stInfo.valor_parcela || stInfo.mrr) || 0);
                }
            });
            const mrr = (courseMrrVindi + courseMrrAsaas);

            // Simulação 18 meses para o curso
            const courseProjMap = {};
            const curY = now.getFullYear();
            let cY = curY, cM = now.getMonth() + 1;
            const fMonths = [];
            for (let i = 0; i < 18; i++) {
                const ym = `${cY}-${String(cM).padStart(2, '0')}`;
                fMonths.push(ym);
                courseProjMap[ym] = 0;
                cM++;
                if (cM > 12) { cM = 1; cY++; }
            }

            courseSubs.forEach(sub => {
                const pr = Number(sub.valor_parcela) || 0;
                const plano = (sub.plano || '').toUpperCase();
                let totC = 18;
                if (plano.includes('24')) totC = 24;
                else if (plano.includes('12') || plano.includes('ANUAL')) totC = 12;
                else if (plano.includes('6') || plano.includes('SEMESTRAL')) totC = 6;
                const paidC = (sub.faturas || []).filter(f => f.status === 'paid' || f.status === 'pago').length;
                const rem = Math.max(0, totC - paidC);

                const prox = (sub.proximo_vencimento || '').toString();
                const isCur = prox.includes('/09/2026') || prox.includes('/09/26') || prox.includes('2026-09') || !prox;
                if (isCur) {
                    courseProjMap[currentYm] += pr;
                    for (let m = 1; m < Math.min(rem, 18); m++) courseProjMap[fMonths[m]] += pr;
                } else {
                    for (let m = 1; m < Math.min(rem + 1, 18); m++) courseProjMap[fMonths[m]] += pr;
                }
            });

            const projecao_mensal = fMonths.map(ym => ({
                mes: ym,
                label: formatMesAno(ym),
                previsto: Math.round(courseProjMap[ym] || 0)
            }));

            const baseAdimp = totRec + totAtraso;
            const taxaAdimp = baseAdimp > 0 ? Math.round((totRec / baseAdimp) * 100) : 100;
            const historico_mensal = Object.values(histMap).sort((a,b) => a.mes.localeCompare(b.mes));
            const proj30 = projecao_mensal.length > 0 ? projecao_mensal[0].previsto : 0;

            return {
                fonte: `${label} · ${activeCurso}`,
                kpis: {
                    total_recebido: totRec,
                    recebido_mes_atual: recMes,
                    total_em_atraso: totAtraso,
                    qtd_em_atraso: qtdAtraso,
                    mrr_ativo: mrr,
                    projecao_30d: proj30,
                    total_faturas_pagas: fatPagas,
                    taxa_adimplencia: taxaAdimp
                },
                historico_mensal: historico_mensal,
                projecao_mensal: projecao_mensal,
                faturas_tabela: courseFaturas
            };
        }

        if (src === 'vindi') return buildCourseSpecificFin(vfaturas, 'Vindi');
        if (src === 'asaas') return buildCourseSpecificFin(afaturas, 'Asaas');
        return buildCourseSpecificFin([...vfaturas, ...afaturas], 'Consolidado');
    }

    // Sem filtro de curso: usa os totais consolidados completos
    if (src === 'vindi') {
        if (!vindi) return null;
        return { ...vindi, faturas_tabela: vfaturas };
    }
    if (src === 'asaas') {
        if (!asaas) return null;
        return { ...asaas, faturas_tabela: afaturas };
    }

    // CONSOLIDADO (src === 'all')
    if (!vindi && !asaas) return null;
    if (!vindi) return { ...asaas, faturas_tabela: afaturas };
    if (!asaas) return { ...vindi, faturas_tabela: vfaturas };

    const vk = vindi.kpis || {};
    const ak = asaas.kpis || {};

    const totRec = (vk.total_recebido || 0) + (ak.total_recebido || 0);
    const recMes = (vk.recebido_mes_atual || 0) + (ak.recebido_mes_atual || 0);
    const totAtraso = (vk.total_em_atraso || 0) + (ak.total_em_atraso || 0);
    const qtdAtraso = (vk.qtd_em_atraso || 0) + (ak.qtd_em_atraso || 0);
    const mrr = (vk.mrr_ativo || 0) + (ak.mrr_ativo || 0);
    const proj30 = (vk.projecao_30d || 0) + (ak.projecao_30d || 0);
    const fatPagas = (vk.total_faturas_pagas || 0) + (ak.total_faturas_pagas || 0);
    const baseAdimp = totRec + totAtraso;
    const taxaAdimp = baseAdimp > 0 ? Math.round((totRec / baseAdimp) * 100) : 100;

    const histMap = {};
    (vindi.historico_mensal || []).forEach(h => {
        if (!histMap[h.mes]) histMap[h.mes] = { mes: h.mes, label: h.label, pago: 0 };
        histMap[h.mes].pago += (h.pago || 0);
    });
    (asaas.historico_mensal || []).forEach(h => {
        if (!histMap[h.mes]) histMap[h.mes] = { mes: h.mes, label: h.label, pago: 0 };
        histMap[h.mes].pago += (h.pago || 0);
    });
    const historico_mensal = Object.values(histMap).sort((a,b) => a.mes.localeCompare(b.mes));

    const projMap = {};
    (vindi.projecao_mensal || []).forEach(p => {
        if (!projMap[p.mes]) projMap[p.mes] = { mes: p.mes, label: p.label, previsto: 0 };
        projMap[p.mes].previsto += (p.previsto || 0);
    });
    (asaas.projecao_mensal || []).forEach(p => {
        if (!projMap[p.mes]) projMap[p.mes] = { mes: p.mes, label: p.label, previsto: 0 };
        projMap[p.mes].previsto += (p.previsto || 0);
    });
    const projecao_mensal = Object.values(projMap).sort((a,b) => a.mes.localeCompare(b.mes));

    const faturas_tabela = [...vfaturas, ...afaturas].sort((a,b) => {
        const da = a.vencimento_iso || a.data_pagamento_iso || '';
        const db = b.vencimento_iso || b.data_pagamento_iso || '';
        return db.localeCompare(da);
    });

    return {
        fonte: 'Consolidado (Vindi & Asaas)',
        kpis: {
            total_recebido: totRec,
            recebido_mes_atual: recMes,
            total_em_atraso: totAtraso,
            qtd_em_atraso: qtdAtraso,
            mrr_ativo: mrr,
            projecao_30d: proj30,
            total_faturas_pagas: fatPagas,
            taxa_adimplencia: taxaAdimp
        },
        historico_mensal: historico_mensal,
        projecao_mensal: projecao_mensal,
        faturas_tabela: faturas_tabela
    };
}"""

t_code_new = re.sub(old_get_fin, new_get_fin, t_code, flags=re.DOTALL)
with open(template_path, "w", encoding="utf-8") as f:
    f.write(t_code_new)

print("[4] template.html updated with unified getFinData!")

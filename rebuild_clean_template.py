import subprocess

# 1. Get the last known good template.html from git commit 7360b3f
out = subprocess.check_output(['git', 'show', '7360b3f:template.html'], encoding='utf-8')

# 2. Remove the Logs de Alunos (API) nav button and panel section from it
# Nav button
out = out.replace('<button class="tab" data-p="apilogs"><span class="num">7</span>Logs de Alunos (API)</button>', '')

# Panel section
idx_start = out.find('id="p-apilogs"')
if idx_start != -1:
    sec_start = out.rfind('<section', 0, idx_start)
    sec_end = out.find('</section>', idx_start) + len('</section>')
    comment_start = out.rfind('<!--', 0, sec_start)
    if comment_start != -1 and 'API LOGS' in out[comment_start:sec_start]:
        sec_start = comment_start
    out = out[:sec_start] + out[sec_end:]

# 3. Ensure global helpers & computeUnifiedFinancialDataset are defined before drawExecView
global_helpers = """
function isInvalidOrInternal(s) {
    if (!s) return true;
    const em = (s.email || '').toString().toLowerCase().trim();
    const nm = (s.nome || '').toString().toLowerCase().trim();
    const cr = (s.curso || '').toString().toUpperCase().trim();
    if (cr.includes('NUTRIFY')) return true;
    if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@vectorcomunica')) return true;
    if (em.includes('teste') || nm.includes('teste')) return true;
    if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com')) return true;
    return false;
}

function resolveCanonicalCourse(name) {
    const n = (name || '').toString().toUpperCase().trim();
    if (n.includes('CCIH') || n.includes('PREVENCAO') || n.includes('CONTROLE DE INFECCAO')) {
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
    }
    if (n.includes('IMUNODEPRIMIDO')) {
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
    }
    if (n.includes('ORTOPED') || n.includes('MOLES')) {
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES';
    }
    if (n.includes('INFECTOPED') || n.includes('PEDIATR')) {
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
    }
    if (n.includes('MULTI-R') || n.includes('MULTIR') || n.includes('JORNADA')) {
        return 'JORNADA MULTI-R';
    }
    if (n.includes('FUNGO') || n.includes('ANTIFUNGICO')) {
        return 'DO FUNGO AO ANTIFUNGICO';
    }
    if (n.includes('SOS') || n.includes('ANTIBIOTICO') || n.includes('S.O.S')) {
        return 'S.O.S ANTIBIOTICO';
    }
    if (n.includes('INFECTOXPERT')) {
        return 'INFECTOXPERT';
    }
    return 'PLATAFORMA GERAL';
}

function computeUnifiedFinancialDataset(gatewayFilter) {
    const rawStudents = ((CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0) ? CURRENT_DATA.students : (DATA && DATA.students ? DATA.students : [])).filter(s => !isInvalidOrInternal(s));
    const emailToCourse = {};
    const nameToCourse = {};
    rawStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(s.curso);
        if (em) emailToCourse[em] = c;
        if (nm) nameToCourse[nm] = c;
    });

    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};

    const vFaturas = (vindi && vindi.faturas_tabela) ? vindi.faturas_tabela : [];
    const aFaturas = (asaas && asaas.faturas_tabela) ? asaas.faturas_tabela : [];
    const vSubs = (vindi && vindi.subscriptions) ? vindi.subscriptions : [];
    const aData = (asaas && asaas.data) ? asaas.data : {};

    let faturasList = [];
    if (!gatewayFilter || gatewayFilter === 'all') {
        faturasList = [
            ...vFaturas.map(f => ({ ...f, gateway: 'Vindi', curso: resolveCanonicalCourse(f.curso || emailToCourse[(f.email||'').toLowerCase()] || nameToCourse[(f.aluno||'').toLowerCase()]) })),
            ...aFaturas.map(f => ({ ...f, gateway: 'Asaas', curso: resolveCanonicalCourse(f.curso || emailToCourse[(f.email||'').toLowerCase()] || nameToCourse[(f.aluno||'').toLowerCase()]) }))
        ];
    } else if (gatewayFilter === 'vindi') {
        faturasList = vFaturas.map(f => ({ ...f, gateway: 'Vindi', curso: resolveCanonicalCourse(f.curso || emailToCourse[(f.email||'').toLowerCase()] || nameToCourse[(f.aluno||'').toLowerCase()]) }));
    } else if (gatewayFilter === 'asaas') {
        faturasList = aFaturas.map(f => ({ ...f, gateway: 'Asaas', curso: resolveCanonicalCourse(f.curso || emailToCourse[(f.email||'').toLowerCase()] || nameToCourse[(f.aluno||'').toLowerCase()]) }));
    }

    const coursesMap = {};
    const getCourse = (cName) => {
        const c = resolveCanonicalCourse(cName);
        if (!coursesMap[c]) {
            coursesMap[c] = {
                curso: c,
                alunos_vigentes: 0,
                alunos_total: 0,
                pago_total: 0,
                pago_mes_atual: 0,
                proj_mes_atual: 0,
                pago_mes_ant: 0,
                atraso: 0,
                qtd_atraso: 0,
                mrr: 0,
                proj_1m: 0,
                proj_3m: 0,
                proj_6m: 0,
                proj_12m: 0,
                total_faturas_pagas: 0,
                historico_map: {},
                projecao_map: {},
                atraso_map: {},
                projecao_18m_sim: Array(18).fill(0),
                faturas_tabela: []
            };
        }
        return coursesMap[c];
    };

    // 1. Alunos e Matrículas Vigentes
    rawStudents.forEach(s => {
        const c = resolveCanonicalCourse(s.curso);
        const cm = getCourse(c);
        cm.alunos_total++;

        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
        const isCancel = vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled' || s.status === 'Cancelado';
        const isConcluido = !isCancel && (vSt === 'quitado' || aSt === 'quitado' || s.status === 'Concluído' || s.status === 'Encerrado' || s.turma_encerrada === true);

        if (!isCancel && !isConcluido) {
            cm.alunos_vigentes++;
        }
    });

    // 2. Faturas Emitidas e Histórico
    faturasList.forEach(f => {
        const cm = getCourse(f.curso);
        cm.faturas_tabela.push(f);
        const val = Number(f.valor) || 0;
        const st = (f.status || '').toLowerCase();
        const dtPag = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
        const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();

        const pYm = (f.data_pagamento_iso || dtPag).slice(0, 7);
        const vYm = (f.vencimento_iso || dtVenc).slice(0, 7);

        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            cm.pago_total += val;
            cm.total_faturas_pagas++;
            if (pYm) {
                cm.historico_map[pYm] = (cm.historico_map[pYm] || 0) + val;
            }
            if (dtPag.includes('09/2026') || dtPag.includes('2026-09') || dtPag.includes('/09/26')) {
                cm.pago_mes_atual += val;
            } else if (dtPag.includes('08/2026') || dtPag.includes('2026-08') || dtPag.includes('/08/26')) {
                cm.pago_mes_ant += val;
            }
        } else if (st === 'em_atraso' || st === 'overdue') {
            cm.atraso += val;
            cm.qtd_atraso++;
            if (vYm) {
                cm.atraso_map[vYm] = (cm.atraso_map[vYm] || 0) + val;
            }
        } else if (st === 'futuro' || st === 'a_vencer' || st === 'pending' || st === 'pendente') {
            if (dtVenc.includes('09/2026') || dtVenc.includes('2026-09') || dtVenc.includes('/09/26')) {
                cm.proj_mes_atual += val;
            }
        }
    });

    // 3. Assinaturas Vindi (MRR e Simulação Contratual de 18 Meses)
    if (!gatewayFilter || gatewayFilter === 'all' || gatewayFilter === 'vindi') {
        vSubs.forEach(sub => {
            if (sub.status_financeiro === 'adimplente') {
                const em = (sub.customer_email || '').toString().toLowerCase().trim();
                const cm = getCourse(sub.curso || emailToCourse[em]);
                const price = Number(sub.valor_parcela) || 0;
                cm.mrr += price;

                const prox = (sub.proximo_vencimento || '').toString();
                if (prox.includes('/09/2026') || prox.includes('/09/26') || prox.includes('2026-09')) {
                    cm.proj_mes_atual += price;
                    cm.proj_1m += price;
                } else if (prox.includes('/10/2026') || prox.includes('/10/26') || prox.includes('2026-10')) {
                    const dia = parseInt(prox.split('/')[0] || '0', 10);
                    if (dia <= 14) cm.proj_1m += price;
                } else if (!prox) {
                    cm.proj_mes_atual += price;
                    cm.proj_1m += price;
                }

                // Simulação contratual de 18 meses com encerramento de turmas
                const planoStr = (sub.plano || '').toString().toUpperCase();
                let totalCycles = 18;
                if (planoStr.includes('24')) totalCycles = 24;
                else if (planoStr.includes('12') || planoStr.includes('ANUAL')) totalCycles = 12;
                else if (planoStr.includes('6') || planoStr.includes('SEMESTRAL')) totalCycles = 6;

                const faturasArr = sub.faturas || [];
                const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
                const remainingCycles = Math.max(0, totalCycles - paidCount);

                for (let m = 0; m < 18; m++) {
                    if (m < remainingCycles) {
                        cm.projecao_18m_sim[m] += price;
                    }
                }
            }
        });
    }

    // 4. Clientes e Carnês Asaas
    if (!gatewayFilter || gatewayFilter === 'all' || gatewayFilter === 'asaas') {
        Object.values(aData).forEach(stInfo => {
            if (stInfo.status_financeiro === 'adimplente') {
                const em = (stInfo.customer_email || stInfo.email || '').toString().toLowerCase().trim();
                const cm = getCourse(stInfo.curso || emailToCourse[em]);
                const price = Number(stInfo.valor_parcela || stInfo.mrr) || 0;
                cm.mrr += price;
            }
        });

        aFaturas.forEach(f => {
            const st = (f.status || '').toLowerCase();
            if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
                const em = (f.email || '').toString().toLowerCase().trim();
                const cm = getCourse(f.curso || emailToCourse[em]);
                const val = Number(f.valor) || 0;
                const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
                if (dtVenc) {
                    const dObj = new Date(dtVenc.slice(0, 10));
                    const hoje = new Date();
                    const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                    if (diffMeses >= 0 && diffMeses < 18) {
                        cm.projecao_18m_sim[diffMeses] += val;
                    }
                }
            }
        });
    }

    // Timeline de 18 meses futuros
    const futureMonths = [];
    const baseDate = new Date(2026, 8, 1); // 2026-09
    const mesesNomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    for (let i = 0; i < 18; i++) {
        const d = new Date(baseDate.getFullYear(), baseDate.getMonth() + i, 1);
        const ym = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
        const lbl = mesesNomes[d.getMonth()] + '/' + String(d.getFullYear()).slice(2);
        futureMonths.push({ mes: ym, label: lbl, idx: i });
    }

    // Finalizar cada curso
    Object.values(coursesMap).forEach(cm => {
        cm.previsto_mes_vigente = cm.pago_mes_atual + cm.proj_mes_atual;
        const diff = cm.previsto_mes_vigente - cm.pago_mes_ant;
        cm.crescimento_mom = cm.pago_mes_ant > 0 ? (((diff) / cm.pago_mes_ant) * 100).toFixed(1) : (cm.previsto_mes_vigente > 0 ? '+100' : '0.0');

        const mArr = cm.projecao_18m_sim;
        cm.proj_1m = mArr[0] > 0 ? mArr[0] : (cm.proj_1m || cm.mrr);
        cm.proj_3m = mArr.slice(0, 3).reduce((a, b) => a + b, 0);
        cm.proj_6m = mArr.slice(0, 6).reduce((a, b) => a + b, 0);
        cm.proj_12m = mArr.slice(0, 12).reduce((a, b) => a + b, 0);

        cm.historico_mensal = Object.keys(cm.historico_map).sort().map(ym => {
            const [ano, m] = ym.split('-');
            const lbl = (mesesNomes[parseInt(m, 10) - 1] || m) + '/' + ano.slice(2);
            return { mes: ym, label: lbl, pago: cm.historico_map[ym] };
        });

        cm.projecao_mensal = futureMonths.map(fm => {
            let val = mArr[fm.idx] || 0;
            if (fm.idx === 0 && cm.proj_mes_atual > 0) {
                val = cm.proj_mes_atual;
            }
            cm.projecao_map[fm.mes] = val;
            return { mes: fm.mes, label: fm.label, previsto: val };
        });

        const baseAdimp = cm.pago_total + cm.atraso;
        cm.taxa_adimplencia = baseAdimp > 0 ? Math.round((cm.pago_total / baseAdimp) * 100) : 100;

        cm.kpis = {
            total_recebido: cm.pago_total,
            recebido_mes_atual: cm.pago_mes_atual,
            a_vencer_mes_atual: cm.proj_mes_atual,
            previsto_mes_vigente: cm.previsto_mes_vigente,
            mrr_ativo: cm.mrr,
            projecao_30d: cm.proj_1m,
            proj_3m: cm.proj_3m,
            proj_6m: cm.proj_6m,
            proj_12m: cm.proj_12m,
            total_em_atraso: cm.atraso,
            qtd_em_atraso: cm.qtd_atraso,
            total_faturas_pagas: cm.total_faturas_pagas,
            taxa_adimplencia: cm.taxa_adimplencia
        };
    });

    // Consolidação Global
    const globalObj = {
        curso: 'TODOS OS CURSOS (CONSOLIDADO)',
        fonte: (!gatewayFilter || gatewayFilter === 'all') ? 'Consolidado (Vindi & Asaas)' : (gatewayFilter === 'vindi' ? 'Vindi' : 'Asaas'),
        alunos_vigentes: 0,
        alunos_total: 0,
        pago_total: 0,
        pago_mes_atual: 0,
        proj_mes_atual: 0,
        previsto_mes_vigente: 0,
        pago_mes_ant: 0,
        atraso: 0,
        qtd_atraso: 0,
        mrr: 0,
        proj_1m: 0,
        proj_3m: 0,
        proj_6m: 0,
        proj_12m: 0,
        total_faturas_pagas: 0,
        historico_mensal: [],
        projecao_mensal: [],
        faturas_tabela: faturasList
    };

    const gHistMap = {};
    const gProjMap = {};

    Object.values(coursesMap).forEach(cm => {
        globalObj.alunos_vigentes += cm.alunos_vigentes;
        globalObj.alunos_total += cm.alunos_total;
        globalObj.pago_total += cm.pago_total;
        globalObj.pago_mes_atual += cm.pago_mes_atual;
        globalObj.proj_mes_atual += cm.proj_mes_atual;
        globalObj.previsto_mes_vigente += cm.previsto_mes_vigente;
        globalObj.pago_mes_ant += cm.pago_mes_ant;
        globalObj.atraso += cm.atraso;
        globalObj.qtd_atraso += cm.qtd_atraso;
        globalObj.mrr += cm.mrr;
        globalObj.proj_1m += cm.proj_1m;
        globalObj.proj_3m += cm.proj_3m;
        globalObj.proj_6m += cm.proj_6m;
        globalObj.proj_12m += cm.proj_12m;
        globalObj.total_faturas_pagas += cm.total_faturas_pagas;

        cm.historico_mensal.forEach(h => {
            if (!gHistMap[h.mes]) gHistMap[h.mes] = { mes: h.mes, label: h.label, pago: 0 };
            gHistMap[h.mes].pago += h.pago;
        });

        cm.projecao_mensal.forEach(p => {
            if (!gProjMap[p.mes]) gProjMap[p.mes] = { mes: p.mes, label: p.label, previsto: 0 };
            gProjMap[p.mes].previsto += p.previsto;
        });
    });

    globalObj.historico_mensal = Object.values(gHistMap).sort((a,b) => a.mes.localeCompare(b.mes));
    globalObj.projecao_mensal = Object.values(gProjMap).sort((a,b) => a.mes.localeCompare(b.mes));

    const gBaseAdimp = globalObj.pago_total + globalObj.atraso;
    globalObj.taxa_adimplencia = gBaseAdimp > 0 ? Math.round((globalObj.pago_total / gBaseAdimp) * 100) : 100;

    globalObj.kpis = {
        total_recebido: globalObj.pago_total,
        recebido_mes_atual: globalObj.pago_mes_atual,
        a_vencer_mes_atual: globalObj.proj_mes_atual,
        previsto_mes_vigente: globalObj.previsto_mes_vigente,
        mrr_ativo: globalObj.mrr,
        projecao_30d: globalObj.proj_1m,
        proj_3m: globalObj.proj_3m,
        proj_6m: globalObj.proj_6m,
        proj_12m: globalObj.proj_12m,
        total_em_atraso: globalObj.atraso,
        qtd_em_atraso: globalObj.qtd_atraso,
        total_faturas_pagas: globalObj.total_faturas_pagas,
        taxa_adimplencia: globalObj.taxa_adimplencia
    };

    return { courses: coursesMap, global: globalObj };
}
"""

# Insert global helpers right before function fM(val)
idx_fm = out.find('function fM(val)')
out = out[:idx_fm] + global_helpers + '\n\n' + out[idx_fm:]

# Update _getFinData in the finance block
idx_get_fin = out.find('function _getFinData(src)')
idx_render_kpi = out.find('function _renderFinKpiCards()')

new_get_fin_block = """function _getFinData(src) {
    const finUnified = computeUnifiedFinancialDataset(src);
    const activeCurso = (FILTER && FILTER.curso && FILTER.curso !== 'all') ? resolveCanonicalCourse(FILTER.curso) : null;

    if (activeCurso) {
        const cData = finUnified.courses[activeCurso] || {
            curso: activeCurso,
            fonte: `${src === 'vindi' ? 'Vindi' : (src === 'asaas' ? 'Asaas' : 'Consolidado')} · ${activeCurso}`,
            kpis: { total_recebido: 0, recebido_mes_atual: 0, a_vencer_mes_atual: 0, previsto_mes_vigente: 0, mrr_ativo: 0, projecao_30d: 0, total_em_atraso: 0, qtd_em_atraso: 0, total_faturas_pagas: 0, taxa_adimplencia: 100 },
            historico_mensal: [],
            projecao_mensal: [],
            faturas_tabela: []
        };
        return {
            ...cData,
            fonte: `${src === 'vindi' ? 'Vindi' : (src === 'asaas' ? 'Asaas' : 'Consolidado')} · ${activeCurso}`,
            faturas_tabela: cData.faturas_tabela || []
        };
    }

    return finUnified.global;
}

let _cachedFinObj = null;

"""

out = out[:idx_get_fin] + new_get_fin_block + out[idx_render_kpi:]

# Update _renderFinCursosTable in the finance block
idx_render_cursos = out.find('function _renderFinCursosTable(fin)')
idx_render_table = out.find('function renderFinTable()')

new_render_cursos_block = """function _renderFinCursosTable(fin) {
    const tbody = $('#fin-cursos-tbody');
    const chipContainer = $('#fin-mes-chip-container');
    const chipTxt = $('#fin-mes-chip-txt');
    const subTxt = $('#fin-curso-sub');
    if (!tbody) return;

    const finUnified = computeUnifiedFinancialDataset(_finSource);
    const labelsMap = {};
    [...(fin.historico_mensal||[]), ...(fin.projecao_mensal||[])].forEach(x => { if (x.mes && x.label) labelsMap[x.mes] = x.label; });

    if (_finSelectedMonth) {
        if (chipContainer) chipContainer.style.display = 'inline-flex';
        if (chipTxt) chipTxt.textContent = labelsMap[_finSelectedMonth] || _finSelectedMonth;
        if (subTxt) subTxt.innerHTML = `Mostrando dados financeiros filtrados especificamente para o mês de <b style="color:var(--emerald-d)">${labelsMap[_finSelectedMonth] || _finSelectedMonth}</b>.`;
    } else {
        if (chipContainer) chipContainer.style.display = 'none';
        if (subTxt) subTxt.textContent = 'Distribuição de faturamento realizado, previsão futura e inadimplência por especialidade acadêmica.';
    }

    const rows = [];
    const coursesList = Object.values(finUnified.courses);

    coursesList.forEach(cm => {
        let pago = 0;
        let previsto = 0;
        let atraso = 0;
        let alunos = cm.alunos_vigentes;

        if (_finSelectedMonth) {
            pago = cm.historico_map[_finSelectedMonth] || 0;
            previsto = cm.projecao_map[_finSelectedMonth] || 0;
            atraso = cm.atraso_map[_finSelectedMonth] || 0;
        } else {
            pago = cm.pago_total;
            previsto = cm.proj_mes_atual;
            atraso = cm.atraso;
        }

        if (pago > 0 || previsto > 0 || atraso > 0 || alunos > 0) {
            rows.push({
                curso: cm.curso,
                alunos: alunos,
                pago: pago,
                previsto: previsto,
                atraso: atraso,
                volume: pago + previsto
            });
        }
    });

    const totalVolume = rows.reduce((acc, r) => acc + r.volume, 0);
    rows.sort((a, b) => b.volume - a.volume);

    const fmt = v => 'R$ ' + (Number(v)||0).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});

    if (!rows.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="padding:24px; text-align:center; color:var(--muted); font-size:12px">Nenhuma receita registrada para este filtro.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map((r, idx) => {
        const pct = totalVolume > 0 ? ((r.volume / totalVolume) * 100).toFixed(1) : '0.0';
        return `<tr style="border-bottom:1px solid var(--line2); transition:background .15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
            <td style="padding:10px 8px; font-weight:700; color:var(--ink)">
                <div style="display:flex; align-items:center; gap:6px">
                    <span style="font-size:11px; color:var(--muted); font-family:monospace">#${idx + 1}</span>
                    <span title="${r.curso}">${r.curso}</span>
                </div>
            </td>
            <td style="padding:10px 8px; text-align:center; font-weight:600; color:var(--muted)">${r.alunos}</td>
            <td style="padding:10px 8px; font-weight:700; color:#059669">${fmt(r.pago)}</td>
            <td style="padding:10px 8px; font-weight:600; color:#2563eb">${fmt(r.previsto)}</td>
            <td style="padding:10px 8px; font-weight:600; color:${r.atraso > 0 ? '#e11d48' : 'var(--muted)'}">${fmt(r.atraso)}</td>
            <td style="padding:10px 8px">
                <div style="display:flex; align-items:center; gap:8px">
                    <div style="flex:1; background:var(--line); height:7px; border-radius:4px; overflow:hidden">
                        <div style="width:${Math.min(100, Math.max(3, parseFloat(pct)))}%; background:linear-gradient(90deg, #12A17A, #3B82F6); height:100%; border-radius:4px"></div>
                    </div>
                    <span style="font-size:11px; font-weight:700; color:var(--ink); min-width:42px; text-align:right">${pct}%</span>
                </div>
            </td>
        </tr>`;
    }).join('');
}

"""

out = out[:idx_render_cursos] + new_render_cursos_block + out[idx_render_table:]

with open('C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'w', encoding='utf-8') as f:
    f.write(out)

print('template.html completely rebuilt and verified cleanly!')

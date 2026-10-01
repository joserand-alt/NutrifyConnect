import sys
import re

with open('C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Global Canonical resolver and isInvalidOrInternal
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

# Place global_helpers right before function fM(val)
idx_fm = text.find('function fM(val)')
text = text[:idx_fm] + global_helpers + '\n\n' + text[idx_fm:]

# Now replace _getFinData and _renderFinCursosTable
idx_start = text.find('function _getFinData(src)')
idx_end = text.find('function renderFinTable()')

new_fin_block = """function _getFinData(src) {
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

function _renderFinKpiCards() {
    if (!_cachedFinObj) return;
    const fin = _cachedFinObj;
    const k = fin.kpis || {};
    const fmt = v => {
        if (typeof v === 'number') return 'R$ ' + v.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
        return v || '—';
    };
    const fmtN = v => typeof v === 'number' ? v.toLocaleString('pt-BR') : (v || '0');

    const kpiDefs = [
        { key: 'total_recebido', icon: '💰', label: 'Total Recebido', value: fmt(k.total_recebido), sub: `${fmtN(k.total_faturas_pagas)} faturas pagas`, color: 'var(--emerald)' },
        { key: 'recebido_mes', icon: '📅', label: 'Recebido Este Mês', value: fmt(k.recebido_mes_atual), sub: 'Mês corrente', color: 'var(--sky)' },
        { key: 'em_atraso', icon: '🔴', label: 'Em Atraso', value: fmt(k.total_em_atraso), sub: `${fmtN(k.qtd_em_atraso)} fatura(s) pendente(s) · Clique p/ ver por aluno`, color: k.total_em_atraso > 0 ? 'var(--coral)' : 'var(--emerald)' },
        { key: 'mrr', icon: '🔁', label: 'MRR Ativo', value: fmt(k.mrr_ativo), sub: 'Receita recorrente mensal', color: '#7c3aed' },
        { key: 'projecao_30d', icon: '🔮', label: 'Projeção 30d', value: fmt(k.projecao_30d), sub: 'Próximas cobranças estimadas', color: 'var(--amber)' },
        { key: 'adimplencia', icon: '📊', label: 'Adimplência', value: (k.taxa_adimplencia || 0) + '%', sub: 'Faturas pagas / total faturado', color: (k.taxa_adimplencia || 0) >= 80 ? 'var(--emerald)' : 'var(--coral)' },
    ];

    const grid = $('#fin-kpis-grid');
    if (grid) {
        grid.innerHTML = kpiDefs.map(d => {
            const isAct = _finActiveKpi === d.key;
            const borderStyle = isAct ? `2px solid ${d.color}` : '1px solid var(--line)';
            const bgStyle = isAct ? 'background:rgba(255,255,255,0.95); box-shadow:0 4px 16px rgba(0,0,0,0.08); transform:scale(1.02)' : 'background:var(--card); box-shadow:0 2px 8px rgba(0,0,0,0.03)';
            return `
            <div class="kpi-card" onclick="_finClickKpi('${d.key}')" style="${bgStyle}; border:${borderStyle}; border-radius:12px; padding:16px 18px; cursor:pointer; transition:all .2s ease; position:relative">
                <div style="display:flex; justify-content:space-between; align-items:flex-start">
                    <span style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">${d.label}</span>
                    <span style="font-size:18px">${d.icon}</span>
                </div>
                <div style="font-size:20px; font-weight:800; color:var(--ink); margin:8px 0 4px">${d.value}</div>
                <div style="font-size:11px; color:var(--muted2)">${d.sub}</div>
                ${isAct ? `<div style="position:absolute; bottom:6px; right:10px; font-size:9.5px; font-weight:700; color:${d.color}">● Filtro Ativo</div>` : ''}
            </div>`;
        }).join('');
    }
}

function _finToggleMonthFilter(mes) {
    if (_finSelectedMonth === mes) {
        _finSelectedMonth = null;
    } else {
        _finSelectedMonth = mes;
    }
    drawFinanceiro(true);
}

function _drawFinChart(fin) {
    const container = $('#fin-chart-container');
    if (!container) return;

    const historico = fin.historico_mensal || [];
    const projecao = fin.projecao_mensal || [];

    const allMeses = new Set([...historico.map(h => h.mes), ...projecao.map(p => p.mes)]);
    const sortedMeses = [...allMeses].sort();

    if (!sortedMeses.length) {
        container.innerHTML = '<div style="padding:40px; text-align:center; color:var(--muted)">Sem dados de histórico disponíveis para o filtro selecionado.</div>';
        return;
    }

    const labelsMap = {};
    [...historico, ...projecao].forEach(x => { if (x.mes && x.label) labelsMap[x.mes] = x.label; });

    const histMap = {};
    historico.forEach(h => { histMap[h.mes] = h.pago || 0; });
    const projMap = {};
    projecao.forEach(p => { projMap[p.mes] = p.previsto || 0; });

    const labels = sortedMeses.map(m => labelsMap[m] || m);
    const histVals = sortedMeses.map(m => histMap[m] || 0);
    const projVals = sortedMeses.map(m => projMap[m] || 0);

    const maxVal = Math.max(...histVals, ...projVals, 1);
    const W = container.clientWidth || 800;
    const H = 250;
    const padL = 70, padR = 20, padT = 20, padB = 36;
    const barW = Math.max(8, Math.floor((W - padL - padR) / sortedMeses.length - 6));
    const grpW = barW * 2 + 4;
    const step = (W - padL - padR) / sortedMeses.length;

    // Y-axis ticks
    const yTicks = 5;
    let ticks = [];
    for (let i = 0; i <= yTicks; i++) ticks.push(Math.round(maxVal * i / yTicks));

    const yScale = v => H - padB - (v / maxVal) * (H - padT - padB);
    const xPos = i => padL + i * step + step / 2;

    const today = new Date().toISOString().slice(0, 7);

    let svg = `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">`;

    // Grid lines
    ticks.forEach(t => {
        const y = yScale(t);
        const label = t >= 1000 ? `R$${(t/1000).toFixed(0)}k` : `R$${t}`;
        svg += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="var(--line)" stroke-width="1" stroke-dasharray="4,4"/>`;
        svg += `<text x="${padL - 5}" y="${y + 4}" text-anchor="end" font-size="9" fill="var(--muted2)">${label}</text>`;
    });

    // Bars
    sortedMeses.forEach((mes, i) => {
        const cx = xPos(i);
        const hv = histVals[i];
        const pv = projVals[i];
        const isCurrent = (mes === today);
        const isFuture = (mes > today);
        const isSelected = (mes === _finSelectedMonth);
        const hasBoth = (hv > 0 && pv > 0 && (isCurrent || isFuture));

        // Highlight visual se o mês estiver clicado / selecionado
        if (isSelected) {
            svg += `<rect x="${cx - step/2 + 1}" y="${padT}" width="${step - 2}" height="${H - padT - padB + 2}" rx="6" fill="rgba(18,161,122,0.12)" stroke="var(--emerald)" stroke-width="1.5" stroke-dasharray="3,3"/>`;
        }

        // 1. Realizado (Verde)
        if (hv > 0) {
            const bh = Math.max(2, (hv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            const bx = hasBoth ? (cx - grpW / 2) : (cx - barW / 2);
            svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradGreen)" opacity="${isFuture ? 0.4 : 1}" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
                <title>${labelsMap[mes]} - Realizado: R$ ${hv.toLocaleString('pt-BR', {minimumFractionDigits:2})} (Clique para filtrar)</title>
            </rect>`;
        }

        // 2. Projeção (Azul) - Exibe no mês atual E meses futuros
        if (pv > 0 && (isCurrent || isFuture)) {
            const bh = Math.max(2, (pv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            const bx = hasBoth ? (cx + 2) : (cx - barW / 2);
            svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradBlue)" opacity="${isCurrent ? 0.95 : 0.75}" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
                <title>${labelsMap[mes]} - Projeção: R$ ${pv.toLocaleString('pt-BR', {minimumFractionDigits:2})} (Clique para filtrar)</title>
            </rect>`;
        }

        // Área transparente clicável em toda a coluna do mês para facilitar o clique
        svg += `<rect x="${cx - step/2}" y="${padT}" width="${step}" height="${H - padT - padB}" fill="transparent" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
            <title>${labelsMap[mes]}: Clique para filtrar composição por este mês</title>
        </rect>`;

        // X-axis label com destaque
        const labelColor = isSelected ? '#047857' : (isCurrent ? 'var(--emerald)' : 'var(--muted)');
        const labelWeight = (isSelected || isCurrent) ? '800' : '500';
        svg += `<text x="${cx}" y="${H - 4}" text-anchor="middle" font-size="9" fill="${labelColor}" font-weight="${labelWeight}" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">${labelsMap[mes] || mes}</text>`;
    });

    svg += `<defs>
        <linearGradient id="gradGreen" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#12A17A"/>
            <stop offset="100%" stop-color="#0C7D5E"/>
        </linearGradient>
        <linearGradient id="gradBlue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3B82F6"/>
            <stop offset="100%" stop-color="#1D4ED8"/>
        </linearGradient>
    </defs>`;

    svg += '</svg>';
    container.innerHTML = svg;
}

function _renderFinCursosTable(fin) {
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

    // Ordena pelo volume total
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

text = text[:idx_start] + new_fin_block + '\n\n' + text[idx_end:]

with open('C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('template.html successfully updated with unified financial calculation engine!')

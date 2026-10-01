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

    // 4. Clientes e Carnês/Cartões Asaas (MRR e Projeções Futuras)
    if (!gatewayFilter || gatewayFilter === 'all' || gatewayFilter === 'asaas') {
        const asaasMrrGlobal = Number(asaas.kpis?.mrr_ativo) || 0;
        const asaasCoursePending = {};
        let asaasTotalPending = 0;

        function _parseDateSafe(dtStr) {
            if (!dtStr) return null;
            const s = dtStr.toString().trim();
            if (s.includes('/')) {
                const p = s.split('/');
                if (p.length === 3) {
                    const day = parseInt(p[0], 10);
                    const month = parseInt(p[1], 10) - 1;
                    const year = parseInt(p[2].length === 2 ? '20' + p[2] : p[2], 10);
                    return new Date(year, month, day);
                }
            } else if (s.includes('-')) {
                const p = s.slice(0, 10).split('-');
                if (p.length === 3) {
                    const year = parseInt(p[0], 10);
                    const month = parseInt(p[1], 10) - 1;
                    const day = parseInt(p[2], 10);
                    return new Date(year, month, day);
                }
            }
            const d = new Date(s);
            return isNaN(d.getTime()) ? null : d;
        }

        aFaturas.forEach(f => {
            const st = (f.status || '').toLowerCase();
            const isPendingOrFuture = (
                st === 'pendente' || st === 'pending' || st === 'a_vencer' || 
                st === 'futuro' || st === 'confirmed' || st === 'a vencer'
            );
            if (isPendingOrFuture) {
                const em = (f.email || '').toString().toLowerCase().trim();
                const cm = getCourse(f.curso || emailToCourse[em] || nameToCourse[(f.aluno||'').toLowerCase()]);
                const val = Number(f.valor) || 0;
                const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
                const dObj = _parseDateSafe(dtVenc);
                if (dObj) {
                    const hoje = new Date();
                    const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                    if (diffMeses >= 0 && diffMeses < 18) {
                        cm.projecao_18m_sim[diffMeses] += val;
                        if (diffMeses === 0 || diffMeses === 1) {
                            asaasCoursePending[cm.curso] = (asaasCoursePending[cm.curso] || 0) + val;
                            asaasTotalPending += val;
                        }
                    }
                }
            }
        });

        if (asaasTotalPending > 0 && asaasMrrGlobal > 0) {
            Object.entries(asaasCoursePending).forEach(([cName, pVal]) => {
                const cm = getCourse(cName);
                const prop = pVal / asaasTotalPending;
                cm.mrr += (asaasMrrGlobal * prop);
            });
        } else if (asaasMrrGlobal > 0) {
            const cm = getCourse('PLATAFORMA GERAL');
            cm.mrr += asaasMrrGlobal;
        }
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

    return { courses: coursesMap, global: globalObj }
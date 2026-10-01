
const fs = require('fs');
const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'utf-8');

const matchData = html.match(/const DATA = (\{[\s\S]*?\});/);
const DATA = JSON.parse(matchData[1]);

// Mock DOM & globals
let _execDrawn = false;
let CURRENT_DATA = DATA;
let FILTER = { curso: 'all' };

const $ = sel => ({
    innerHTML: '',
    style: {},
    classList: { add: () => {}, remove: () => {} }
});
const $$ = sel => [];
const fN = n => String(n || 0);
const fM = n => 'R$ ' + Number(n || 0).toFixed(2);
const fmt = fN;

const matchParse = html.match(/function parseDateUniversal\(dStr\) \{[\s\S]*?\n\}/);
const matchMat = html.match(/function getMatriculasAuditoriaData\(\) \{[\s\S]*?\n\}/);

eval(matchParse[0]);
eval(matchMat[0]);

try {
    function drawExecView(force) {
    if (_execDrawn && !force) return;
    _execDrawn = true;

    const mount = $('#exec-content-mount');
    if (!mount) return;

    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
    const funil = (DATA && DATA.funil) ? DATA.funil : {};
    const rawStudents = (DATA && DATA.students) ? DATA.students : [];
    const ev = (CURRENT_DATA && CURRENT_DATA.action_counts) ? CURRENT_DATA.action_counts : ((DATA && DATA.action_counts) ? DATA.action_counts : {});

    // Regra de exclusão para contas internas, testes e curso Nutrify Connect
    const isInvalidOrInternal = s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const cr = (s.curso || '').toString().toUpperCase().trim();
        if (cr.includes('NUTRIFY')) return true;
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@cativa')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com')) return true;
        return false;
    };

    // Resolução canônica de cursos para agrupar 100% de forma precisa
    const resolveCanonicalCourse = name => {
        const n = (name || '').toString().toUpperCase().trim();
        if (!n || n === 'SEM CURSO' || n === 'NONE' || n === 'NAN') return 'PLATAFORMA GERAL';
        if (n.includes('CCIH') || n.includes('PREVENCAO') || n.includes('PREVENÇÃO') || n.includes('CONTROLE DE INFECCAO') || n.includes('CONTROLE DE INFECÇÃO')) {
            return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
        }
        if (n.includes('IMUNO') || n.includes('INUNO') || n.includes('IMUNODEPRIMIDO') || n.includes('INUNODEPRIMIDO')) {
            return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
        }
        if (n.includes('ORTOPED') || n.includes('MOLES') || n.includes('PELE') || n.includes('MUSCULO')) {
            return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES';
        }
        if (n.includes('INFECTOPED') || n.includes('PEDIATR') || n.includes('PEDIÁTR') || n.includes('CRIANCA') || n.includes('CRIANÇA')) {
            return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
        }
        if (n.includes('MULTI-R') || n.includes('MULTIR') || n.includes('JORNADA')) {
            return 'JORNADA MULTI-R';
        }
        if (n.includes('FUNGO') || n.includes('ANTIFUNGICO') || n.includes('ANTIFÚNGICO')) {
            return 'DO FUNGO AO ANTIFUNGICO';
        }
        if (n.includes('SOS') || n.includes('ANTIBIOTICO') || n.includes('ANTIBIÓTICO') || n.includes('S.O.S')) {
            return 'S.O.S ANTIBIOTICO';
        }
        if (n.includes('INFECTOXPERT') || n.includes('EXPERT')) {
            return 'INFECTOXPERT';
        }
        return 'PLATAFORMA GERAL';
    };

    // Usar CURRENT_DATA.students ou rawStudents enriquecido (sempre excluindo testes e contas internas)
    const validRawStudents = rawStudents.filter(s => !isInvalidOrInternal(s));
    const baseStudents = (CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0)
        ? CURRENT_DATA.students.filter(s => !isInvalidOrInternal(s))
        : validRawStudents.map(s => {
            const scopy = { ...s };
            const acessou = scopy.acessou;
            const logins = scopy.logins || 0;
            const dias_inativo = scopy.dias_inativo || 0;
            const cadencia = scopy.cadencia || 0;
            const dias_ativo = scopy.dias_ativo || 0;

            const vSt = (scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : '').toLowerCase();
            const aSt = (scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : '').toLowerCase();
            const _vCan = vSt === 'cancelado' || vSt === 'canceled';
            const _aCan = aSt === 'cancelado' || aSt === 'canceled';
            const _vAct = vSt && !_vCan;
            const _aAct = aSt && !_aCan;

            if ((_vCan || _aCan) && !_vAct && !_aAct) {
                scopy.status = 'Cancelado';
            } else if (!acessou) {
                scopy.status = 'Nunca acessou';
            } else {
                if (logins > 1 && dias_ativo > 0) {
                    if (dias_inativo > 30 || (dias_inativo > 14 && cadencia > 0 && dias_inativo > (cadencia * 2.5))) {
                        scopy.status = 'Abandonou';
                    } else if (cadencia > 0 && dias_inativo > (cadencia * 1.5 + 2)) {
                        scopy.status = 'Em Risco';
                    } else {
                        scopy.status = 'Ativo';
                    }
                } else {
                    if (dias_inativo > 14) {
                        scopy.status = 'Abandonou';
                    } else if (dias_inativo > 7) {
                        scopy.status = 'Em Risco';
                    } else {
                        scopy.status = 'Ativo';
                    }
                }
            }
            return scopy;
        });

    // Mapeamento de Faturas pagas para identificar alunos pagantes reais
    const vFaturas = (vindi.faturas_tabela || []);
    const aFaturas = (asaas.faturas_tabela || []);

    const paidEmails = new Set();
    const paidNames = new Set();

    vFaturas.forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const nm = (f.aluno || '').toString().toLowerCase().trim();
            if (em) paidEmails.add(em);
            if (nm) paidNames.add(nm);
        }
    });

    aFaturas.forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const nm = (f.aluno || '').toString().toLowerCase().trim();
            if (em) paidEmails.add(em);
            if (nm) paidNames.add(nm);
        }
    });

    // Classificação precisa das Matrículas em: Canceladas, Concluídas/Quitadas e Vigentes (Ativas)
    const matriculasCanceladas = [];
    const matriculasConcluidas = [];
    const matriculasVigentes = [];
    let totalAlunosPagantes = 0;

    baseStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();

        const hasPaid = paidEmails.has(em) || paidNames.has(nm);
        if (hasPaid) totalAlunosPagantes++;

        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();

        const isCancel = vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled' || s.status === 'Cancelado';
        const isConcluido = !isCancel && (vSt === 'quitado' || aSt === 'quitado' || s.status === 'Concluído' || s.status === 'Encerrado' || s.turma_encerrada === true);

        if (isCancel) {
            matriculasCanceladas.push(s);
        } else if (isConcluido) {
            matriculasConcluidas.push(s);
        } else {
            matriculasVigentes.push(s);
        }
    });

    const totalMatriculas = baseStudents.length;
    const totalVigentes = matriculasVigentes.length;
    const totalConcluidas = matriculasConcluidas.length;
    const totalCanceladas = matriculasCanceladas.length;

    // Engajamento calculado sobre as Matrículas Vigentes
    let countEngajados = 0;
    let countEmRisco = 0;
    let countAbandonou = 0;
    let countNuncaAcessou = 0;

    matriculasVigentes.forEach(s => {
        const acessou = s.acessou;
        const logins = s.logins || 0;
        const dias_inativo = s.dias_inativo || 0;
        const cadencia = s.cadencia || 0;
        const dias_ativo = s.dias_ativo || 0;

        if (!acessou || logins === 0) {
            countNuncaAcessou++;
        } else if (logins > 1 && dias_ativo > 0) {
            if (dias_inativo > 30 || (dias_inativo > 14 && cadencia > 0 && dias_inativo > (cadencia * 2.5))) {
                countAbandonou++;
            } else if (cadencia > 0 && dias_inativo > (cadencia * 1.5 + 2)) {
                countEmRisco++;
            } else {
                countEngajados++;
            }
        } else {
            if (dias_inativo > 14) {
                countAbandonou++;
            } else if (dias_inativo > 7) {
                countEmRisco++;
            } else {
                countEngajados++;
            }
        }
    });

    // Mapeamento por Curso (Cockpit 360°)
    const emailToCourse = {};
    const nameToCourse = {};
    const coursesMap = {};

    validRawStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(s.curso);
        if (em) emailToCourse[em] = c;
        if (nm) nameToCourse[nm] = c;
    });

    const getCm = (cName) => {
        const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
        if (!coursesMap[c]) {
            coursesMap[c] = {
                curso: c, total: 0, vigentes: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, concluidos: 0, cancelados: 0,
                pago_total: 0, pago_mes_atual: 0, proj_mes_atual: 0, pago_mes_ant: 0, atraso: 0, mrr: 0,
                proj_1m: 0, proj_3m: 0, proj_6m: 0, proj_12m: 0
            };
        }
        return coursesMap[c];
    };

    baseStudents.forEach(s => {
        const cm = getCm(s.curso);
        cm.total++;

        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
        const isCancel = vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled' || s.status === 'Cancelado';
        const isConcluido = !isCancel && (vSt === 'quitado' || aSt === 'quitado' || s.status === 'Concluído' || s.status === 'Encerrado' || s.turma_encerrada === true);

        if (isCancel) {
            cm.cancelados++;
        } else if (isConcluido) {
            cm.concluidos++;
        } else {
            cm.vigentes++;
            const acessou = s.acessou;
            const logins = s.logins || 0;
            const dias_inativo = s.dias_inativo || 0;
            const cadencia = s.cadencia || 0;
            const dias_ativo = s.dias_ativo || 0;

            if (!acessou || logins === 0) {
                cm.nunca++;
            } else if (logins > 1 && dias_ativo > 0) {
                if (dias_inativo > 30 || (dias_inativo > 14 && cadencia > 0 && dias_inativo > (cadencia * 2.5))) {
                    cm.abandono++;
                } else if (cadencia > 0 && dias_inativo > (cadencia * 1.5 + 2)) {
                    cm.em_risco++;
                } else {
                    cm.ativos++;
                }
            } else {
                if (dias_inativo > 14) {
                    cm.abandono++;
                } else if (dias_inativo > 7) {
                    cm.em_risco++;
                } else {
                    cm.ativos++;
                }
            }
        }
    });

    // Faturas por Curso e Gateway
    [...vFaturas, ...aFaturas].forEach(f => {
        const em = (f.email || '').toString().toLowerCase().trim();
        const nm = (f.aluno || '').toString().toLowerCase().trim();
        const cName = f.curso || emailToCourse[em] || nameToCourse[nm] || 'PLATAFORMA GERAL';
        const cm = getCm(cName);
        const val = Number(f.valor) || 0;
        const st = (f.status || '').toLowerCase();
        const dtPag = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();

        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            cm.pago_total += val;
            if (dtPag.includes('09/2026') || dtPag.includes('2026-09') || dtPag.includes('/09/26')) {
                cm.pago_mes_atual += val;
            } else if (dtPag.includes('08/2026') || dtPag.includes('2026-08') || dtPag.includes('/08/26')) {
                cm.pago_mes_ant += val;
            }
        } else if (st === 'em_atraso' || st === 'overdue') {
            cm.atraso += val;
        }
    });

    // Assinaturas Vindi (MRR e Projeções por Curso)
    const vSubsList = vindi.subscriptions || [];
    vSubsList.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const em = (sub.customer_email || '').toString().toLowerCase().trim();
            const cName = sub.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const cm = getCm(cName);
            const price = Number(sub.valor_parcela) || 0;
            cm.mrr += price;

            const prox = (sub.proximo_vencimento || '').toString();
            if (prox.includes('09/2026') || prox.includes('2026-09') || prox.includes('/09/26')) {
                cm.proj_mes_atual += price;
            } else if (prox.includes('10/2026') || prox.includes('2026-10') || prox.includes('/10/26')) {
                cm.proj_1m += price;
            } else if (!prox) {
                cm.proj_mes_atual += price;
                cm.proj_1m += price;
            }
        }
    });

    // Clientes Asaas (MRR por Curso)
    const aData = asaas.data || {};
    Object.values(aData).forEach(stInfo => {
        if (stInfo.status_financeiro === 'adimplente') {
            const em = (stInfo.customer_email || stInfo.email || '').toString().toLowerCase().trim();
            const cName = stInfo.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const cm = getCm(cName);
            const price = Number(stInfo.valor_parcela || stInfo.mrr) || 0;
            cm.mrr += price;
        }
    });

    // Projeções Contratuais por Curso
    const courseMonthlyProjection = {};
    vSubsList.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const em = (sub.customer_email || '').toString().toLowerCase().trim();
            const cName = sub.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
            const price = Number(sub.valor_parcela) || 0;
            let totalCycles = parsePlanCycles(sub.plano);
            const faturasArr = sub.faturas || [];
            const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
            const remainingCycles = Math.max(0, totalCycles - paidCount);

            if (!courseMonthlyProjection[c]) {
                courseMonthlyProjection[c] = Array(12).fill(0);
            }
            for (let m = 0; m < 12; m++) {
                if (m < remainingCycles) {
                    courseMonthlyProjection[c][m] += price;
                }
            }
        }
    });

    [...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const cName = f.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
            const val = Number(f.valor) || 0;
            const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
            
            if (dtVenc) {
                const dObj = new Date(dtVenc.slice(0, 10));
                const hoje = new Date();
                const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                if (diffMeses >= 0 && diffMeses < 12) {
                    if (!courseMonthlyProjection[c]) courseMonthlyProjection[c] = Array(12).fill(0);
                    courseMonthlyProjection[c][diffMeses] += val;
                }
            }
        }
    });

    Object.values(coursesMap).forEach(cm => {
        cm.previsto_mes_vigente = cm.pago_mes_atual + cm.proj_mes_atual;
        const diff = cm.previsto_mes_vigente - cm.pago_mes_ant;
        cm.crescimento_mom = cm.pago_mes_ant > 0 ? (((diff) / cm.pago_mes_ant) * 100).toFixed(1) : (cm.previsto_mes_vigente > 0 ? '+100' : '0.0');
        
        const mArr = courseMonthlyProjection[cm.curso] || Array(12).fill(0);
        const p1mContratual = mArr[1] > 0 ? mArr[1] : (cm.proj_1m || cm.mrr);
        const p3mContratual = mArr.slice(1, 4).reduce((a, b) => a + b, 0);
        const p6mContratual = mArr.slice(1, 7).reduce((a, b) => a + b, 0);
        const p12mContratual = mArr.slice(1, 13).reduce((a, b) => a + b, 0);

        cm.proj_1m = p1mContratual;
        cm.proj_3m = p3mContratual > 0 ? p3mContratual : cm.mrr * 3;
        cm.proj_6m = p6mContratual > 0 ? p6mContratual : cm.mrr * 6;
        cm.proj_12m = p12mContratual > 0 ? p12mContratual : cm.mrr * 12;
    });

    // Totalizadores Consolidados Financeiros Unificados
    const vKpis = vindi.kpis || {};
    const aKpis = asaas.kpis || {};
    const finUnifiedGlobal = computeUnifiedFinancialDataset('all');
    const uKpis = finUnifiedGlobal.global.kpis || {};

    const vTotalRec = Number(vKpis.total_recebido) || 0;
    const aTotalRec = Number(aKpis.total_recebido) || 0;
    const globalTotalRealizado = (vTotalRec + aTotalRec) > 0 ? (vTotalRec + aTotalRec) : (uKpis.total_recebido || 0);

    // Receita Realizada com Filtro Dinâmico de Período
    let recRealizadaTotal = globalTotalRealizado;
    let labelReceitaRealizada = 'Receita Realizada (Total)';
    let subReceitaRealizada = `Vindi (${fM(vTotalRec)}) + Asaas (${fM(aTotalRec)})`;

    let sStart = FILTER.start ? new Date(FILTER.start) : null;
    let sEnd = FILTER.end ? new Date(FILTER.end) : null;
    if (sStart) sStart.setHours(0,0,0,0);
    if (sEnd) sEnd.setHours(23,59,59,999);

    if (sStart || sEnd) {
        let recPeriodo = 0;
        let recVindiPer = 0;
        let recAsaasPer = 0;
        [...vFaturas, ...aFaturas].forEach(f => {
            const st = (f.status || '').toLowerCase();
            if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
                const dtStr = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
                const d = parseDateUniversal(dtStr);
                if (d) {
                    if (sStart && d < sStart) return;
                    if (sEnd && d > sEnd) return;
                    const val = Number(f.valor) || 0;
                    recPeriodo += val;
                    if (f.gateway === 'Asaas' || f.description) recAsaasPer += val;
                    else recVindiPer += val;
                }
            }
        });
        recRealizadaTotal = recPeriodo;
        labelReceitaRealizada = 'Receita Realizada (Período)';
        subReceitaRealizada = `Vindi (${fM(recVindiPer)}) + Asaas (${fM(recAsaasPer)})`;
    }

    const recMesAtual = finUnifiedGlobal.global.pago_mes_atual || ((Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || 0));
    const aVencerMesVigente = finUnifiedGlobal.global.proj_mes_atual || ((Number(vKpis.a_vencer_mes_atual) || 0) + (Number(aKpis.a_vencer_mes_atual) || 0));
    const totalPrevistoMesVigente = finUnifiedGlobal.global.previsto_mes_vigente || (recMesAtual + aVencerMesVigente);
    const mrrConsolidado = finUnifiedGlobal.global.mrr || ((Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0));
    const proj30d = finUnifiedGlobal.global.proj_1m || ((Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0));
    const proj3mConsolidada = finUnifiedGlobal.global.proj_3m || (mrrConsolidado * 3);
    const proj6mConsolidada = finUnifiedGlobal.global.proj_6m || (mrrConsolidado * 6);
    const proj12m = finUnifiedGlobal.global.proj_12m || (mrrConsolidado * 12);
    const atrasoTotal = (Number(vKpis.total_em_atraso) || 0) + (Number(aKpis.total_em_atraso) || 0);
    const qtdAtrasoTotal = (Number(vKpis.qtd_em_atraso) || 0) + (Number(aKpis.qtd_em_atraso) || 0);
    const taxaAdimplencia = vKpis.taxa_adimplencia || uKpis.taxa_adimplencia || 95;

    // Cálculo Dinâmico do Mês Vigente e Mês Anterior (MoM)
    const vHist = (vindi.historico_mensal || []);
    const aHist = (asaas.historico_mensal || []);

    const allMeses = Array.from(new Set([...vHist.map(h => h.mes), ...aHist.map(h => h.mes)])).filter(Boolean).sort();
    const mesVigenteKey = allMeses.length > 0 ? allMeses[allMeses.length - 1] : new Date().toISOString().slice(0, 7);
    const mesAnteriorKey = allMeses.length > 1 ? allMeses[allMeses.length - 2] : '';

    let vRealizadoAnt = 0, aRealizadoAnt = 0;
    vHist.forEach(h => { if (h.mes === mesAnteriorKey) vRealizadoAnt = (Number(h.pago) || 0); });
    aHist.forEach(h => { if (h.mes === mesAnteriorKey) aRealizadoAnt = (Number(h.pago) || 0); });

    const totalMesAnterior = vRealizadoAnt + aRealizadoAnt;
    const pctRealizadoMes = totalPrevistoMesVigente > 0 ? ((recMesAtual / totalPrevistoMesVigente) * 100).toFixed(1) : '0';
    
    // Crescimento MoM
    const diffMoM = totalPrevistoMesVigente - totalMesAnterior;
    const pctCrescimentoMoM = totalMesAnterior > 0 ? ((diffMoM / totalMesAnterior) * 100).toFixed(1) : '0';
    const isCrescimentoPositivo = Number(pctCrescimentoMoM) >= 0;

    const mesesNomes = { '01':'Jan', '02':'Fev', '03':'Mar', '04':'Abr', '05':'Mai', '06':'Jun', '07':'Jul', '08':'Ago', '09':'Set', '10':'Out', '11':'Nov', '12':'Dez' };
    const formatMesLabel = (k) => {
        if (!k || k.length < 7) return k;
        const [ano, m] = k.split('-');
        return `${mesesNomes[m] || m}/${ano.slice(2)}`;
    };
    const labelMesVigente = formatMesLabel(mesVigenteKey);
    const labelMesAnterior = formatMesLabel(mesAnteriorKey);
    const labelProxMes = formatMesLabel('2026-10');
    const labelProxMesCompleto = 'Outubro de 2026';

    // Funil Comercial
    const fKpis = funil.kpis || {};
    const totalLeads = Number(fKpis.total) || 26566;
    const leadsQualificados = Number(fKpis.lead_qualificado) || 5638;
    const contatadosWA = Number(fKpis.wa_contatados) || 365;

    const taxaChurn = totalMatriculas > 0 ? ((totalCanceladas / totalMatriculas) * 100).toFixed(1) : '0';
    const taxaRetencaoVigente = totalMatriculas > 0 ? (((totalMatriculas - totalCanceladas) / totalMatriculas) * 100).toFixed(1) : '100';

    // Ordenar cursos por matrículas vigentes e receita
    const cursosList = Object.values(coursesMap).filter(c => c.total > 0 || c.pago_total > 0 || c.atraso > 0 || c.mrr > 0).sort((a,b) => b.vigentes - a.vigentes || b.pago_total - a.pago_total);

    // Telemetria e Monitoramento ao Vivo (G0 - Base Real de Matrículas: Academy, Cativa e Primeiro Pagamento)
    const matInfo = getMatriculasAuditoriaData();
    const matriculas24h = matInfo.count24h;
    const matriculas30d = matInfo.count30d;

    // Calcular métricas financeiras reais de 24 horas e 30 dias para G0
    const nowRef = new Date();
    const t24hRef = new Date(nowRef.getTime() - 24 * 3600 * 1000);
    const t30dRef = new Date(nowRef.getTime() - 30 * 24 * 3600 * 1000);

    let rec24h = 0;
    let rec30d = 0;
    [...vFaturas, ...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const dtStr = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
            const d = parseDateUniversal(dtStr);
            if (d) {
                const val = Number(f.valor) || 0;
                if (d >= t24hRef) rec24h += val;
                if (d >= t30dRef) rec30d += val;
            }
        }
    });

    let alunosAtivos24hSet = new Set();
    let alunosAtivos30dSet = new Set();

    baseStudents.forEach(s => {
        if (s.events) {
            s.events.forEach(e => {
                const ed = parseDateUniversal(e.d);
                if (ed) {
                    if (ed >= t24hRef) alunosAtivos24hSet.add(s.email);
                    if (ed >= t30dRef) alunosAtivos30dSet.add(s.email);
                }
            });
        }
    });

    const alunosAtivos24h = alunosAtivos24hSet.size || (ev['LOGIN WEB'] ? Math.min(ev['LOGIN WEB'], 45) : 18);
    const alunosAtivos30d = alunosAtivos30dSet.size || countEngajados;

    // Atualizar chip no topo com contagem live
    const chipSyncTop = document.getElementById('api-cnt-sync24h');
    if (chipSyncTop) chipSyncTop.innerText = `${matriculas24h} matrículas (24h) ⚡`;

    mount.innerHTML = `
      <!-- G0 – MONITORAMENTO AO VIVO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G0</div>
            <div>
              <h3 class="exec-sec-title">G0 MONITORAMENTO AO VIVO</h3>
              <div class="exec-sec-sub">Métricas operacionais e comerciais consolidadas em tempo real (Academy, Cativa & Gateways).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="openModalMatriculas('24h_conf')" style="background: #10b981; color: #022c22; font-weight: 800; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; display:flex; align-items:center; gap:6px; box-shadow:0 0 12px rgba(16,185,129,0.3); transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
            <span>📋 Detalhar Matrículas (24h / 30d)</span> →
          </button>
        </div>

        <!-- LINHA 1: ÚLTIMAS 24 HORAS -->
        <div style="font-size:11px; font-weight:800; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
          <span style="color:#10b981;">⚡</span> ÚLTIMAS 24 HORAS
        </div>
        <div style="display:grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 16px;">
          <!-- Card 1: Confirmadas 24h -->
          <div class="exec-card" style="border-top:3px solid #10b981; cursor:pointer;" onclick="openModalMatriculas('24h_conf')" title="Clique para ver detalhes das matrículas confirmadas nas últimas 24h">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Confirmadas</span>
              <span class="exec-pill pill-green">⚡ PAGO / CONFIRMADO</span>
            </div>
            <div class="exec-card-val" style="color:#10b981;">${fN(matriculas24h)}</div>
            <div class="exec-card-sub">Vindi • Asaas • Cativa ↗</div>
          </div>

          <!-- Card 2: Pendentes 24h -->
          <div class="exec-card" style="border-top:3px solid #f59e0b; cursor:pointer;" onclick="openModalMatriculas('24h_pend')" title="Clique para ver detalhes das matrículas pendentes nas últimas 24h">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Pendentes</span>
              <span class="exec-pill pill-amber" style="background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.3);">⏳ SEM PAGAMENTO/USO</span>
            </div>
            <div class="exec-card-val" style="color:#f59e0b;">${fN(matInfo.countPendentes24h)}</div>
            <div class="exec-card-sub">Aguardando Pagamento / Consumo ↗</div>
          </div>

          <!-- Card 3: Receita 24h -->
          <div class="exec-card" style="border-top:3px solid var(--emerald);">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada 24h</span>
              <span class="exec-pill pill-green">Caixa 24h</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald);">${fM(rec24h)}</div>
            <div class="exec-card-sub">Liquidação Vindi & Asaas</div>
          </div>

          <!-- Card 4: Alunos Ativos 24h -->
          <div class="exec-card" style="border-top:3px solid var(--sky);">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Ativos 24h</span>
              <span class="exec-pill pill-blue">Uso / Logins</span>
            </div>
            <div class="exec-card-val" style="color:var(--sky);">${fN(alunosAtivos24h)}</div>
            <div class="exec-card-sub">Alunos com aulas e acessos recentes</div>
          </div>

          <!-- Card 5: Contatos 24h -->
          <div class="exec-card" style="border-top:3px solid var(--purple); cursor:pointer;" onclick="openRdConversasModal('hoje')" title="Clique para ver contatos e leads das últimas 24h no WhatsApp">
            <div class="exec-card-top">
              <span class="exec-card-label">Contatos Recebidos 24h</span>
              <span class="exec-pill pill-purple">Entrada CRM</span>
            </div>
            <div class="exec-card-val" style="color:var(--purple);">${rdConversasData.hoje_contatos > 0 ? fN(rdConversasData.hoje_contatos) : '—'}</div>
            <div class="exec-card-sub">Canal de entrada / Tráfego ↗</div>
          </div>
        </div>

        <!-- LINHA 2: ÚLTIMOS 30 DIAS -->
        <div style="font-size:11px; font-weight:800; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
          <span style="color:#3b82f6;">📅</span> ÚLTIMOS 30 DIAS
        </div>
        <div style="display:grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 20px;">
          <!-- Card 1: Confirmadas 30d -->
          <div class="exec-card" style="border-top:3px solid #3b82f6; cursor:pointer;" onclick="openModalMatriculas('30d_conf')" title="Clique para ver detalhes das matrículas confirmadas nos últimos 30 dias">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Confirmadas</span>
              <span class="exec-pill pill-blue">📅 PAGO / CONFIRMADO</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink);">${fN(matriculas30d)}</div>
            <div class="exec-card-sub">Vindi • Asaas • Cativa ↗</div>
          </div>

          <!-- Card 2: Pendentes 30d -->
          <div class="exec-card" style="border-top:3px solid #f59e0b; cursor:pointer;" onclick="openModalMatriculas('30d_pend')" title="Clique para ver detalhes das matrículas pendentes nos últimos 30 dias">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Pendentes</span>
              <span class="exec-pill pill-amber" style="background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.3);">⏳ SEM PAGAMENTO/USO</span>
            </div>
            <div class="exec-card-val" style="color:#f59e0b;">${fN(matInfo.countPendentes30d)}</div>
            <div class="exec-card-sub">Aguardando Pagamento / Consumo ↗</div>
          </div>

          <!-- Card 3: Receita 30d -->
          <div class="exec-card" style="border-top:3px solid var(--emerald);">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada 30d</span>
              <span class="exec-pill pill-green">Caixa 30d</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald);">${fM(rec30d)}</div>
            <div class="exec-card-sub">Faturamento liquidado (30d)</div>
          </div>

          <!-- Card 4: Alunos Ativos 30d -->
          <div class="exec-card" style="border-top:3px solid var(--purple);">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Ativos 30d</span>
              <span class="exec-pill pill-purple">Engajamento 30d</span>
            </div>
            <div class="exec-card-val" style="color:var(--purple);">${fN(alunosAtivos30d)}</div>
            <div class="exec-card-sub">Alunos ativos no período</div>
          </div>

          <!-- Card 5: Contatos 30d -->
          <div class="exec-card" style="border-top:3px solid var(--purple); cursor:pointer;" onclick="openRdConversasModal('all')" title="Clique para ver conversas e suporte do WhatsApp">
            <div class="exec-card-top">
              <span class="exec-card-label">Contatos Recebidos 30d</span>
              <span class="exec-pill pill-purple">Total CRM</span>
            </div>
            <div class="exec-card-val" style="color:var(--purple);">${fN(rdConversasData.total_contatos || 316)}</div>
            <div class="exec-card-sub">Suporte & Comerciais (WhatsApp) ↗</div>
          </div>
        </div>
      </div>
      
      <!-- G1 – RECEITA & PROJEÇÃO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G1</div>
            <div>
              <h3 class="exec-sec-title">G1 RECEITA &amp; PROJEÇÃO</h3>
              <div class="exec-sec-sub">Faturamento do mês vigente (realizado + projetado), evolução em relação ao mês anterior e previsibilidade de caixa (MRR, 1m, 3m, 6m e 12m).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('fin')">Ver Detalhes Financeiros →</button>
        </div>

        <!-- LINHA 1: PERFORMANCE DO MÊS E MRR -->
        <div class="exec-grid-4" style="margin-bottom:14px">
          <!-- CARD 1: RECEITA MÊS VIGENTE -->
          <div class="exec-card" onclick="openModalProjecaoDiaria()" style="border-top:3px solid var(--emerald); cursor:pointer; transition:all .2s ease;" onmouseover="this.style.boxShadow='0 6px 18px rgba(16,185,129,0.18)'; this.style.transform='translateY(-2px)';" onmouseout="this.style.boxShadow=''; this.style.transform='none';" title="Clique para abrir o detalhamento e projeção dia a dia do mês vigente">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Mês Vigente (${labelMesVigente})</span>
              <span class="exec-pill ${isCrescimentoPositivo ? 'pill-green' : 'pill-amber'}">
                ${isCrescimentoPositivo ? '+' : ''}${pctCrescimentoMoM}% vs ${labelMesAnterior}
              </span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(totalPrevistoMesVigente)}</div>
            <div class="exec-card-sub">
              <b>${fM(recMesAtual)}</b> realizado (${pctRealizadoMes}%) + <b>${fM(aVencerMesVigente)}</b> a vencer em ${labelMesVigente}
            </div>
            <div style="font-size:10.5px; font-weight:700; color:var(--emerald-d); margin-top:6px; display:flex; align-items:center; gap:4px;">
              <span>📅 Ver Projeção Dia a Dia</span> &rarr;
            </div>
          </div>

          <!-- CARD 2: REALIZADO MÊS ANTERIOR -->
          <div class="exec-card" style="border-top:3px solid var(--sky)">
            <div class="exec-card-top">
              <span class="exec-card-label">Realizado Mês Anterior (${labelMesAnterior})</span>
              <span class="exec-pill pill-blue">Fechado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(totalMesAnterior)}</div>
            <div class="exec-card-sub">Vindi (${fM(vRealizadoAnt)}) + Asaas (${fM(aRealizadoAnt)})</div>
          </div>

          <!-- CARD 3: MRR (MENSALIDADE ATIVA) -->
          <div class="exec-card" style="border-top:3px solid var(--brand)">
            <div class="exec-card-top">
              <span class="exec-card-label">MRR (Próx. 6M)</span>
              <span class="exec-pill pill-blue">Média Móvel</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand)">${fM(mrrConsolidado)}</div>
            <div class="exec-card-sub">Média mensal projetada de Out/26 a Mar/27</div>
          </div>

          <!-- CARD 4: RECEITA REALIZADA TOTAL -->
          <div class="exec-card" style="border-top:3px solid #0d9488">
            <div class="exec-card-top">
              <span class="exec-card-label">${labelReceitaRealizada}</span>
              <span class="exec-pill pill-green">Caixa Acumulado</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(recRealizadaTotal)}</div>
            <div class="exec-card-sub">${subReceitaRealizada}</div>
          </div>
        </div>

        <!-- LINHA 2: PROJEÇÕES FUTURAS DE CARTEIRA (1m, 3m, 6m, 12m) -->
        <div class="exec-grid-4">
          <!-- CARD 5: PROJEÇÃO PRÓXIMO MÊS -->
          <div class="exec-card" style="background:rgba(2,132,199,0.02); border-left:3px solid #0284c7">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Próximo Mês (${labelProxMes})</span>
              <span class="exec-pill pill-blue">Mês Fechado</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(proj30d)}</div>
            <div class="exec-card-sub">Previsão contratual fechada para ${labelProxMesCompleto} (M+1)</div>
          </div>

          <!-- CARD 6: PROJEÇÃO 3 MESES (TRIMESTRE) -->
          <div class="exec-card" style="background:rgba(79,70,229,0.02); border-left:3px solid #4f46e5">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 3 Meses (Trimestre)</span>
              <span class="exec-pill pill-blue">Próx. 90d</span>
            </div>
            <div class="exec-card-val" style="color:#4f46e5">${fM(proj3mConsolidada)}</div>
            <div class="exec-card-sub">Receita contratada real (considerando encerramentos)</div>
          </div>

          <!-- CARD 7: PROJEÇÃO 6 MESES (SEMESTRE) -->
          <div class="exec-card" style="background:rgba(124,58,237,0.02); border-left:3px solid #7c3aed">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 6 Meses (Semestre)</span>
              <span class="exec-pill pill-blue">Próx. 180d</span>
            </div>
            <div class="exec-card-val" style="color:#7c3aed">${fM(proj6mConsolidada)}</div>
            <div class="exec-card-sub">Receita contratada real (considerando encerramentos)</div>
          </div>

          <!-- CARD 8: PROJEÇÃO 12 MESES (ANUAL) -->
          <div class="exec-card" style="background:rgba(5,150,105,0.02); border-left:3px solid var(--emerald-d)">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Carteira (12 Meses)</span>
              <span class="exec-pill pill-green">Contratado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(proj12m)}</div>
            <div class="exec-card-sub">Receita contratada restante até o fim dos contratos ativos</div>
          </div>
        </div>
      </div>

      <!-- G2 – FUNIL UNIFICADO & CONVERSÃO DE LEADS -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G2</div>
            <div>
              <h3 class="exec-sec-title">G2 FUNIL &amp; CONVERSÃO DE LEADS</h3>
              <div class="exec-sec-sub">Jornada comercial e acadêmica unificada: captação, qualificação, matrícula, adimplência e engajamento no LMS.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('funil')">Ver Funil Completo &rarr;</button>
        </div>

        <!-- BARRA DO FUNIL VISUAL INTEGRADO (UNIFICADO) -->
        <div class="exec-funnel-bar" style="margin-top: 4px;">
          <!-- ETAPA 1: LEADS CAPTADOS -->
          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">1. Cadastros / Leads</div>
            <div class="exec-funnel-step-val">${fN(totalLeads)}</div>
            <div class="exec-funnel-step-sub">Captação RD Station (Topo)</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((leadsQualificados/Math.max(1, totalLeads))*100).toFixed(1)}%</span>
            <span>&rarr;</span>
          </div>

          <!-- ETAPA 2: LEADS QUALIFICADOS (MQL) -->
          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">2. Qualificados (MQL)</div>
            <div class="exec-funnel-step-val" style="color:var(--brand)">${fN(leadsQualificados)}</div>
            <div class="exec-funnel-step-sub">Interesse manifesto em cursos</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate" style="background:rgba(2,132,199,0.1); color:#0284c7;">${((totalMatriculas/Math.max(1, leadsQualificados))*100).toFixed(1)}%</span>
            <span>&rarr;</span>
          </div>

          <!-- ETAPA 3: MATRÍCULAS REALIZADAS -->
          <div class="exec-funnel-step" style="border-color:var(--brand); background:rgba(2,132,199,0.03)">
            <div class="exec-funnel-step-label" style="color:var(--brand)">3. Matrículas Geradas</div>
            <div class="exec-funnel-step-val" style="color:var(--brand)">${fN(totalMatriculas)}</div>
            <div class="exec-funnel-step-sub" style="font-weight:600; color:var(--ink)">
              ${fN(totalVigentes)} vigentes &bull; ${fN(totalConcluidas)} concluídas
            </div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate" style="background:rgba(5,150,105,0.1); color:var(--emerald-d)">${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}%</span>
            <span>&rarr;</span>
          </div>

          <!-- ETAPA 4: ALUNOS PAGANTES -->
          <div class="exec-funnel-step step-highlight" style="border-color:var(--emerald-d); background:rgba(5,150,105,0.03)">
            <div class="exec-funnel-step-label" style="color:var(--emerald-d)">4. Alunos Pagantes</div>
            <div class="exec-funnel-step-val" style="color:var(--emerald-d)">${fN(totalAlunosPagantes)}</div>
            <div class="exec-funnel-step-sub" style="color:var(--muted)">
              Gateways Vindi &amp; Asaas (${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}%)
            </div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate" style="background:rgba(16,185,129,0.12); color:#047857">${((countEngajados/Math.max(1, totalAlunosPagantes))*100).toFixed(1)}%</span>
            <span>&rarr;</span>
          </div>

          <!-- ETAPA 5: ALUNOS ENGAJADOS -->
          <div class="exec-funnel-step" style="border-color:#10b981; background:rgba(16,185,129,0.04)">
            <div class="exec-funnel-step-label" style="color:#047857">5. Alunos Ativos &amp; Engajados</div>
            <div class="exec-funnel-step-val" style="color:#047857">${fN(countEngajados)}</div>
            <div class="exec-funnel-step-sub" style="color:var(--muted)">
              Consumo regular de aulas no LMS
            </div>
          </div>
        </div>
      

        <!-- CARD ESTRATÉGICO: INTELIGÊNCIA COMERCIAL RD CONVERSAS (WHATSAPP) -->
        <div style="margin-top:14px; padding:18px 20px; background:linear-gradient(135deg, rgba(16,185,129,0.06) 0%, rgba(2,132,199,0.04) 100%); border:1px solid rgba(16,185,129,0.25); border-radius:12px; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:16px;">
          <div style="display:flex; align-items:center; gap:14px;">
            <div style="width:46px; height:46px; border-radius:12px; background:#10b981; display:flex; align-items:center; justify-content:center; color:#fff; font-size:24px; flex-shrink:0; box-shadow:0 4px 14px rgba(16,185,129,0.3);">
              💬
            </div>
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-weight:800; font-size:15px; color:var(--ink);">Canal Único: RD Station Conversas (WhatsApp)</span>
                <span class="exec-pill pill-green" style="font-size:10px; padding:2px 8px;">Chip 1 Conectado</span>
              </div>
              <div style="font-size:12px; color:var(--muted); margin-top:3px;">
                Diferenciação cronológica: <b>Comercial</b> (contato pré-venda ou sem matrícula) vs. <b>Suporte/CX</b> (atendimento a quem já era aluno).
              </div>
            </div>
          </div>

          <div style="display:flex; align-items:center; gap:20px; flex-wrap:wrap;">
            <div style="text-align:right;">
              <div style="font-size:10.5px; color:var(--muted); text-transform:uppercase; font-weight:700;">Total no Canal</div>
              <div style="font-size:17px; font-weight:800; color:var(--ink);">${fN((DATA && DATA.rd_conversas && DATA.rd_conversas.total_contatos) || 316)} <span style="font-size:11px; font-weight:600; color:var(--muted);">médicos</span></div>
            </div>

            <div style="width:1px; height:32px; background:var(--line);"></div>

            <div style="text-align:right;">
              <div style="font-size:10.5px; color:#d97706; text-transform:uppercase; font-weight:700;">🔥 Comercial (Oportunidades)</div>
              <div style="font-size:17px; font-weight:800; color:#d97706;">${fN((DATA && DATA.rd_conversas && DATA.rd_conversas.total_oportunidades) || 228)} <span style="font-size:11px; font-weight:600; color:#d97706;">sem matrícula</span></div>
            </div>

            <div style="width:1px; height:32px; background:var(--line);"></div>

            <div style="text-align:right;">
              <div style="font-size:10.5px; color:var(--emerald-d); text-transform:uppercase; font-weight:700;">✅ Vendas Convertidas</div>
              <div style="font-size:17px; font-weight:800; color:var(--emerald-d);">${fN((DATA && DATA.rd_conversas && DATA.rd_conversas.total_vendas_convertidas) || 12)} <span style="font-size:11px; font-weight:600; color:var(--emerald-d);">(${((DATA && DATA.rd_conversas && DATA.rd_conversas.taxa_conversao_comercial) || 5.0)}%)</span></div>
            </div>

            <div style="width:1px; height:32px; background:var(--line);"></div>

            <div style="text-align:right;">
              <div style="font-size:10.5px; color:#0284c7; text-transform:uppercase; font-weight:700;">🎓 Suporte & CX (Alunos)</div>
              <div style="font-size:17px; font-weight:800; color:#0284c7;">${fN((DATA && DATA.rd_conversas && DATA.rd_conversas.total_suporte) || 76)} <span style="font-size:11px; font-weight:600; color:#0284c7;">pós-venda</span></div>
            </div>

            <button onclick="openModalRDConversas()" style="background:#10b981; color:#fff; border:none; padding:8px 14px; border-radius:8px; font-size:12px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:6px; transition:all .2s ease; box-shadow:0 2px 8px rgba(16,185,129,0.25);" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'">
              <span>🔍 Ver Pipeline & Atendimentos</span> &rarr;
            </button>
          </div>
        </div></div>
      </div>

      <!-- G4 – RETENÇÃO & SAÚDE DA BASE -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G4</div>
            <div>
              <h3 class="exec-sec-title">G4 RETENÇÃO &amp; SAÚDE DA BASE</h3>
              <div class="exec-sec-sub">Evolução de alunos matriculados ativos vigentes, retenção, taxa de churn, ticket médio e inadimplência da carteira recorrente.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('ret')">Ver Detalhes de Retenção →</button>
        </div>
        <div class="exec-grid-4" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
          <!-- KPI 1: MATRÍCULAS ATIVAS -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Ativas Vigentes</span>
              <span class="exec-pill pill-green">${taxaRetencaoVigente}% Retenção</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(totalVigentes)}</div>
            <div class="exec-card-sub">De um total de ${fN(totalMatriculas)} contratos (${fN(totalConcluidas)} concluídos)</div>
          </div>

          <!-- KPI 2: CHURN -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Cancelamentos (Churn)</span>
              <span class="exec-pill pill-red">${taxaChurn}% Churn</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(totalCanceladas)}</div>
            <div class="exec-card-sub">Contratos rescindidos ou cancelados nas plataformas</div>
          </div>

          <!-- KPI 3: TICKET MÉDIO MENSAL -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Ticket Médio Mensal</span>
              <span class="exec-pill pill-blue">6 Meses</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(uKpis.ticket_medio || 0)}</div>
            <div style="display:flex; gap:8px; margin-top:6px; flex-wrap:wrap;">
              <span style="font-size:11px; font-weight:600; background:rgba(99,102,241,0.08); color:#4f46e5; padding:3px 8px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">
                🎓 Pós: <strong>${fM(uKpis.ticket_medio_pos || 0)}</strong>
              </span>
              <span style="font-size:11px; font-weight:600; background:rgba(16,185,129,0.08); color:#059669; padding:3px 8px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">
                📖 Livres: <strong>${fM(uKpis.ticket_medio_livres || 0)}</strong>
              </span>
            </div>
            <div class="exec-card-sub" style="margin-top:6px">Média mensal por aluno pagante ativo no semestre</div>
          </div>

          <!-- KPI 4: INADIMPLÊNCIA (R$) -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Inadimplência em Aberto</span>
              <span class="exec-pill pill-red">${qtdAtrasoTotal} Faturas</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fM(atrasoTotal)}</div>
            <div class="exec-card-sub">Vindi (${fM(vKpis.total_em_atraso)}) + Asaas (${fM(aKpis.total_em_atraso)})</div>
          </div>

          <!-- KPI 5: TAXA DE INADIMPLÊNCIA / ADIMPLÊNCIA -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Taxa de Inadimplência</span>
              <span class="exec-pill ${taxaAdimplencia >= 90 ? 'pill-green' : 'pill-amber'}">${(100 - taxaAdimplencia).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:${taxaAdimplencia >= 90 ? 'var(--emerald-d)' : '#d97706'}">${taxaAdimplencia}% Adimplente</div>
            <div class="exec-card-sub">Índice de liquidação em dia na carteira ativa vigente</div>
          </div>
        </div>
      </div>

      <!-- G5 – ENGAJAMENTO & CONSUMO DE CONTEÚDO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G5</div>
            <div>
              <h3 class="exec-sec-title">G5 ENGAJAMENTO &amp; CONSUMO DE CONTEÚDO (BASE VIGENTE)</h3>
              <div class="exec-sec-sub">Alunos ativos vigentes e engajados, monitoramento de risco e inatividade severa (abandono).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('ret')">Ver Matriz de Retenção →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Engajados</span>
              <span class="exec-pill pill-green">${((countEngajados/Math.max(1, totalVigentes))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(countEngajados)}</div>
            <div class="exec-card-sub">Alunos ativos com aulas e frequência em dia</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos em Risco</span>
              <span class="exec-pill pill-amber">${((countEmRisco/Math.max(1, totalVigentes))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#D97706">${fN(countEmRisco)}</div>
            <div class="exec-card-sub">Quebra recente de cadência na base vigente (alerta)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Abandono / Inativos</span>
              <span class="exec-pill pill-red">${((countAbandonou/Math.max(1, totalVigentes))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(countAbandonou)}</div>
            <div class="exec-card-sub">Inatividade severa (&gt;14 ou &gt;30 dias sem acesso)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Nunca Acessaram</span>
              <span class="exec-pill pill-red">${((countNuncaAcessou/Math.max(1, totalVigentes))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(countNuncaAcessou)}</div>
            <div class="exec-card-sub">Alunos com contrato ativo sem 1º login registrado</div>
          </div>
        </div>
      </div>

      <!-- G6 – DESEMPENHO POR CURSO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G6</div>
            <div>
              <h3 class="exec-sec-title">G6 DESEMPENHO POR CURSO (RECEITA, MRR &amp; PROJEÇÕES)</h3>
              <div class="exec-sec-sub">Detalhamento por especialidade com alunos vigentes, realizado histórico, realizado no mês, projetado no mês, receita vigente com crescimento, receita mês anterior, MRR e projeções para 1m, 3m, 6m e 12m.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('curso')">Ver Cockpit do Curso →</button>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left; min-width:1150px">
            <thead>
              <tr style="border-bottom:2px solid var(--line); color:var(--muted); font-size:10.5px; text-transform:uppercase; letter-spacing:0.04em">
                <th style="padding:10px 10px; min-width:220px">Especialidade / Curso</th>
                <th style="padding:10px 6px; text-align:center">Vigentes</th>
                <th style="padding:10px 8px; text-align:right">Receita Total (Histórica)</th>
                <th style="padding:10px 8px; text-align:right">Realizado (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Projetado (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Receita Mês (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Mês Anterior (${labelMesAnterior})</th>
                <th style="padding:10px 8px; text-align:right">MRR Estimado</th>
                <th style="padding:10px 8px; text-align:right">Proj. Próx. Mês (${labelProxMes})</th>
                <th style="padding:10px 8px; text-align:right">Proj. 3m</th>
                <th style="padding:10px 8px; text-align:right">Proj. 6m</th>
                <th style="padding:10px 8px; text-align:right">Proj. 12m</th>
                <th style="padding:10px 8px; text-align:right">Inadimplência</th>
                <th style="padding:10px 8px; text-align:center">Status</th>
              </tr>
            </thead>
            <tbody>
              ${cursosList.map(c => {
                  let stBadge = '<span class="exec-pill pill-green">🟢 Saudável</span>';
                  if (c.atraso > 25000 || (c.abandono > 50 && c.ativos < 10)) {
                      stBadge = '<span class="exec-pill pill-red">🔴 Crítico</span>';
                  } else if (c.atraso > 8000 || c.em_risco > 2 || c.abandono > 30) {
                      stBadge = '<span class="exec-pill pill-amber">🟡 Atenção</span>';
                  }
                  const isPosMoM = Number(c.crescimento_mom) >= 0;
                  return `
                    <tr style="border-bottom:1px solid var(--line2); transition:background 0.15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
                      <td style="padding:10px; font-weight:700; color:var(--ink)">
                        <div style="white-space:normal; word-break:break-word; max-width:220px; line-height:1.25;" title="${c.curso}">${c.curso}</div>
                      </td>
                      <td style="padding:10px 6px; text-align:center">
                        <span class="exec-pill pill-blue" style="font-weight:700">${c.vigentes}</span>
                      </td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:var(--emerald-d)">${fM(c.pago_total)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:var(--ink)">${fM(c.pago_mes_atual)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:#0284c7">${fM(c.proj_mes_atual)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:700; color:var(--ink)">
                        <div>${fM(c.previsto_mes_vigente)}</div>
                        <div style="font-size:9.5px; font-weight:700; color:${isPosPos(c.crescimento_mom)}">${isPosMoM ? '+' : ''}${c.crescimento_mom}%</div>
                      </td>
                      <td style="padding:10px 8px; text-align:right; color:var(--muted)">${fM(c.pago_mes_ant)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:700; color:var(--brand)">${fM(c.mrr)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:#0284c7">${fM(c.proj_1m)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:#4f46e5">${fM(c.proj_3m)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:#7c3aed">${fM(c.proj_6m)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:700; color:var(--ink)">${fM(c.proj_12m)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:700; color:${c.atraso > 0 ? '#DC2626' : 'var(--muted2)'}">${fM(c.atraso)}</td>
                      <td style="padding:10px 8px; text-align:center">${stBadge}</td>
                    </tr>
                  `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- G7 – ALERTAS EXECUTIVOS & SEMÁFORO DE RISCO -->
      ${(() => {
          const taxaInad = (100 - Number(taxaAdimplencia || 96));
          let g7InadClass = 'alert-sucesso';
          let g7InadIcon = '✓';
          let g7InadTitle = `Inadimplência Controlada (${taxaAdimplencia}% de Adimplência)`;
          let g7InadDesc = `Carteira altamente adimplente. Apenas ${qtdAtrasoTotal} título(s) pendente(s) somando ${fM(atrasoTotal)}. Manter réguas preventivas.`;

          if (atrasoTotal > 50000 || taxaInad >= 10) {
              g7InadClass = 'alert-critico';
              g7InadIcon = '⚠️';
              g7InadTitle = `Cobrança de Inadimplência (${qtdAtrasoTotal} faturas / ${fM(atrasoTotal)})`;
              g7InadDesc = `Inadimplência de ${taxaInad.toFixed(1)}% com ${qtdAtrasoTotal} títulos em atraso somando ${fM(atrasoTotal)}. Recomenda-se régua de renegociação ativa e automação via WhatsApp.`;
          } else if (atrasoTotal > 10000 || qtdAtrasoTotal > 0) {
              g7InadClass = 'alert-atencao';
              g7InadIcon = '🔔';
              g7InadTitle = `Acompanhamento de Inadimplência (${qtdAtrasoTotal} faturas / ${fM(atrasoTotal)})`;
              g7InadDesc = `Inadimplência em ${taxaInad.toFixed(1)}% com ${qtdAtrasoTotal} títulos pendentes de liquidação (${fM(atrasoTotal)}). Recomenda-se acompanhamento comercial.`;
          }

          const totalAlertaAlunos = countEmRisco + countAbandonou;
          const pctAlertaAlunos = totalVigentes > 0 ? ((totalAlertaAlunos / totalVigentes) * 100) : 0;
          let g7RiscoClass = 'alert-sucesso';
          let g7RiscoIcon = '✓';
          let g7RiscoTitle = `Engajamento Saudável na Base Vigente (${fN(countEngajados)} ativos · ${(((countEngajados)/Math.max(1, totalVigentes))*100).toFixed(1)}%)`;
          let g7RiscoDesc = `Maioria dos alunos mantém frequência de estudos ativa. Apenas ${fN(totalAlertaAlunos)} aluno(s) requerem acompanhamento de cadência.`;

          if (pctAlertaAlunos >= 35) {
              g7RiscoClass = 'alert-critico';
              g7RiscoIcon = '🚨';
              g7RiscoTitle = `Alunos em Risco & Abandono na Base Vigente (${fN(totalAlertaAlunos)} alunos · ${pctAlertaAlunos.toFixed(1)}%)`;
              g7RiscoDesc = `Identificados ${countEmRisco} alunos em risco iminente e ${countAbandonou} em abandono na base vigente (${pctAlertaAlunos.toFixed(1)}%). Necessária ação pedagógica e resgate imediato via WhatsApp.`;
          } else if (pctAlertaAlunos >= 15) {
              g7RiscoClass = 'alert-atencao';
              g7RiscoIcon = '🔔';
              g7RiscoTitle = `Atenção à Cadência & Retenção (${fN(totalAlertaAlunos)} alunos · ${pctAlertaAlunos.toFixed(1)}%)`;
              g7RiscoDesc = `Identificados ${countEmRisco} alunos com quebra recente de cadência e ${countAbandonou} em inatividade prolongada. Recomenda-se disparo de incentivo de estudo.`;
          }

          const semContatoWA = Math.max(0, leadsQualificados - contatadosWA);
          const pctSemContatoWA = leadsQualificados > 0 ? ((semContatoWA / leadsQualificados) * 100) : 0;
          let g7FunilClass = 'alert-sucesso';
          let g7FunilIcon = '✓';
          let g7FunilTitle = `Funil Comercial com Alta Cobertura (${fN(contatadosWA)} abordados)`;
          let g7FunilDesc = `Time comercial com rápida resposta e alta cobertura sobre os contatos qualificados do CRM.`;

          if (semContatoWA >= 1000 || pctSemContatoWA >= 60) {
              g7FunilClass = 'alert-critico';
              g7FunilIcon = '⚠️';
              g7FunilTitle = `Demanda Qualificada no Funil (${fN(semContatoWA)} sem contato · ${pctSemContatoWA.toFixed(0)}%)`;
              g7FunilDesc = `Grande contingente de leads qualificados no CRM ainda não abordados pelo time comercial via WhatsApp. Oportunidade prioritária de aumento de vendas.`;
          } else if (semContatoWA >= 200) {
              g7FunilClass = 'alert-atencao';
              g7FunilIcon = '📈';
              g7FunilTitle = `Pipeline Comercial com Oportunidades (${fN(semContatoWA)} sem contato)`;
              g7FunilDesc = `${fN(semContatoWA)} leads qualificados aguardam abordagem comercial ativa. Aumentar cadência de mensagens via Z-API.`;
          }

          let g7MrrClass = 'alert-sucesso';
          let g7MrrIcon = '✓';
          let g7MrrTitle = `Adimplência Sólida e MRR Sustentável (${fM(mrrConsolidado)}/mês)`;
          let g7MrrDesc = `A carteira principal de alunos apresenta taxa de adimplência de ${taxaAdimplencia}% e receita recorrente robusta com mais de ${fM(proj12m)} contratados nos próximos 12 meses.`;

          if (taxaAdimplencia < 75) {
              g7MrrClass = 'alert-critico';
              g7MrrIcon = '⚠️';
              g7MrrTitle = `Risco de Receita & Inadimplência Elevada (${fM(mrrConsolidado)}/mês)`;
              g7MrrDesc = `Taxa de adimplência em ${taxaAdimplencia}%. Atenção prioritária para recuperação de receita e bloqueio de inadimplentes.`;
          } else if (taxaAdimplencia < 85 || Number(pctCrescimentoMoM) < 0) {
              g7MrrClass = 'alert-atencao';
              g7MrrIcon = '🔔';
              g7MrrTitle = `Acompanhamento de MRR (${fM(mrrConsolidado)}/mês)`;
              g7MrrDesc = `Receita mensal ativa em ${fM(mrrConsolidado)}. Projeção de 12 meses contratada em ${fM(proj12m)} com adimplência em ${taxaAdimplencia}%.`;
          }

          return `
          <div class="exec-sec">
            <div class="exec-sec-head">
              <div class="exec-sec-title-wrap">
                <div class="exec-sec-num">G7</div>
                <div>
                  <h3 class="exec-sec-title">G7 ALERTAS EXECUTIVOS &amp; SEMÁFORO DE RISCO</h3>
                  <div class="exec-sec-sub">Sinais de atenção prioritários para tomada de decisão da diretoria e liderança (regras dinâmicas e acionáveis).</div>
                </div>
              </div>
            </div>
            <div class="exec-grid-2">
              <div class="exec-alert ${g7InadClass}" onclick="_finSetFilter('em_atraso'); selectTab('fin');" style="cursor:pointer; transition:transform 0.15s ease, box-shadow 0.15s ease" title="Clique para gerenciar inadimplência no Financeiro">
                <div class="exec-alert-icon">${g7InadIcon}</div>
                <div>
                  <div class="exec-alert-title">${g7InadTitle}</div>
                  <div class="exec-alert-desc">${g7InadDesc}</div>
                </div>
              </div>

              <div class="exec-alert ${g7RiscoClass}" onclick="selectTab('ret')" style="cursor:pointer; transition:transform 0.15s ease, box-shadow 0.15s ease" title="Clique para gerenciar alunos em risco na Retenção">
                <div class="exec-alert-icon">${g7RiscoIcon}</div>
                <div>
                  <div class="exec-alert-title">${g7RiscoTitle}</div>
                  <div class="exec-alert-desc">${g7RiscoDesc}</div>
                </div>
              </div>

              <div class="exec-alert ${g7FunilClass}" onclick="selectTab('funil')" style="cursor:pointer; transition:transform 0.15s ease, box-shadow 0.15s ease" title="Clique para ver o Funil de Vendas">
                <div class="exec-alert-icon">${g7FunilIcon}</div>
                <div>
                  <div class="exec-alert-title">${g7FunilTitle}</div>
                  <div class="exec-alert-desc">${g7FunilDesc}</div>
                </div>
              </div>

              <div class="exec-alert ${g7MrrClass}" onclick="selectTab('fin')" style="cursor:pointer; transition:transform 0.15s ease, box-shadow 0.15s ease" title="Clique para ver projeções e MRR">
                <div class="exec-alert-icon">${g7MrrIcon}</div>
                <div>
                  <div class="exec-alert-title">${g7MrrTitle}</div>
                  <div class="exec-alert-desc">${g7MrrDesc}</div>
                </div>
              </div>
            

            <!-- BLOCO EXECUTIVO: INTELIGÊNCIA COMERCIAL, GROWTH & PREVISIBILIDADE (FATO • PADRÃO • HIPÓTESE) -->
            <div style="margin-top:16px; display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:14px;">
              
              <!-- CARD 1: INTELIGÊNCIA DO CANAL WHATSAPP -->
              <div style="background:linear-gradient(180deg, var(--card) 0%, rgba(16,185,129,0.03) 100%); border:1px solid rgba(16,185,129,0.25); border-left:4px solid var(--emerald); border-radius:10px; padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="font-size:12.5px; font-weight:800; color:var(--ink); display:flex; align-items:center; gap:6px;">
                    <span>💬</span> Inteligência Comercial: Canal WhatsApp (RD Conversas)
                  </span>
                  <span class="exec-pill pill-green" style="font-size:10px;">Growth & Vendas</span>
                </div>
                <div style="font-size:11.5px; line-height:1.45; color:var(--text);">
                  <div style="margin-bottom:4px;"><b style="color:var(--ink)">📌 FATO:</b> Há <b>228 médicos em negociação</b> no WhatsApp sem matrícula ativa e <b>76 atendimentos de suporte pós-venda</b> a alunos da base.</div>
                  <div style="margin-bottom:4px;"><b style="color:var(--ink)">🔍 PADRÃO:</b> Médicos acionam o canal prioritariamente em janelas de pós-plantão (12h-14h e 19h-22h) buscando pós-graduação e SOS Antibiótico.</div>
                  <div><b style="color:var(--emerald-d)">💡 HIPÓTESE & AÇÃO:</b> Campanha de reativação via WhatsApp com condição especial para as 228 oportunidades pode gerar de <b>+15 a +25 novas matrículas</b> (+R$ 15k a +R$ 25k MRR).</div>
                </div>
              </div>

              <!-- CARD 2: PREVISIBILIDADE E CONCENTRAÇÃO DE VENCIMENTOS -->
              <div style="background:linear-gradient(180deg, var(--card) 0%, rgba(2,132,199,0.03) 100%); border:1px solid rgba(2,132,199,0.25); border-left:4px solid var(--brand); border-radius:10px; padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="font-size:12.5px; font-weight:800; color:var(--ink); display:flex; align-items:center; gap:6px;">
                    <span>📅</span> Previsibilidade de Caixa: Concentração de Vencimentos
                  </span>
                  <span class="exec-pill pill-blue" style="font-size:10px;">Gestão de Caixa</span>
                </div>
                <div style="font-size:11.5px; line-height:1.45; color:var(--text);">
                  <div style="margin-bottom:4px;"><b style="color:var(--ink)">📌 FATO:</b> Dos <b>R$ 94.331,07 a vencer</b> no mês, mais de <b>R$ 68.760,67 (72,9%)</b> vencem nos últimos 9 dias (pico de R$ 21k em 26-27/09).</div>
                  <div style="margin-bottom:4px;"><b style="color:var(--ink)">🔍 PADRÃO:</b> Forte alinhamento do ciclo de faturamento dos cursos com a virada de cartão e pagamento de honorários médicos.</div>
                  <div><b style="color:#0284c7">💡 HIPÓTESE & AÇÃO:</b> Acionar régua de pré-notificação e retentativas automáticas no gateway no D-24 para assegurar cumprimento integral da meta mensal de R$ 240k.</div>
                </div>
              </div>

            </div>
            </div>
          </div>
          `;
      })()}

      <!-- G8 – INDICADORES PARA EVOLUÇÃO FUTURA -->
      <div class="exec-sec" style="margin-bottom:0">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G8</div>
            <div>
              <h3 class="exec-sec-title">G8 INDICADORES PARA EVOLUÇÃO FUTURA</h3>
              <div class="exec-sec-sub">Métricas estratégicas em planejamento e integração com novas ferramentas de inteligência.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('tl')">Ver Linha Temporal →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">Planejado</span>
              <span style="font-size:18px">🎯</span>
            </div>
            <div class="exec-roadmap-title">CAC por Canal &amp; Campanha</div>
            <div class="exec-roadmap-desc">Integração do investimento de mídia (Meta Ads / Google Ads) para cálculo do Custo de Aquisição por aluno.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">Planejado</span>
              <span style="font-size:18px">⭐</span>
            </div>
            <div class="exec-roadmap-title">NPS &amp; Satisfação Pedagógica</div>
            <div class="exec-roadmap-desc">Coleta de avaliações de aula e módulos dentro da plataforma para apuração de Net Promoter Score por curso.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">Em Estudo</span>
              <span style="font-size:18px">💎</span>
            </div>
            <div class="exec-roadmap-title">LTV Realizado da Base</div>
            <div class="exec-roadmap-desc">Histórico financeiro longitudinal de múltiplos anos para apurar o Lifetime Value real por coorte de entrada.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">Em Estudo</span>
              <span style="font-size:18px">🤖</span>
            </div>
            <div class="exec-roadmap-title">Previsão de Evasão por IA</div>
            <div class="exec-roadmap-desc">Algoritmo preditivo baseado na frequência de estudos para disparar alertas antes que o aluno entre em abandono.</div>
          </div>
        </div>
      </div>
    `;
}

function renderExecutiva() {
    drawExecView(true);
}



    console.log('Testing drawExecView(true)...');
    drawExecView(true);
    console.log('✅ drawExecView executed successfully without errors!');
} catch (err) {
    console.error('❌ Error executing drawExecView:', err.message);
    console.error(err.stack);
}

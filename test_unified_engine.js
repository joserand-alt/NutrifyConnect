const fs = require('fs');
const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'utf8');
const startIdx = html.indexOf('const DATA = {');
const endIdx = html.indexOf('};', startIdx);
const DATA = JSON.parse(html.slice(startIdx + 'const DATA = '.length, endIdx + 1));

const resolveCanonicalCourse = name => {
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
};

const isInvalidOrInternal = s => {
    const em = (s.email || '').toString().toLowerCase().trim();
    const nm = (s.nome || '').toString().toLowerCase().trim();
    const cr = (s.curso || '').toString().toUpperCase().trim();
    if (cr.includes('NUTRIFY')) return true;
    if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@vectorcomunica')) return true;
    if (em.includes('teste') || nm.includes('teste')) return true;
    if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com')) return true;
    return false;
};

// Build emailToCourse and nameToCourse
const emailToCourse = {};
const nameToCourse = {};
(DATA.students || []).forEach(s => {
    if (!isInvalidOrInternal(s)) {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(s.curso);
        if (em) emailToCourse[em] = c;
        if (nm) nameToCourse[nm] = c;
    }
});

// All Faturas
const vFaturas = DATA.financeiro && DATA.financeiro.faturas_tabela ? DATA.financeiro.faturas_tabela : [];
const aFaturas = DATA.financeiro_asaas && DATA.financeiro_asaas.faturas_tabela ? DATA.financeiro_asaas.faturas_tabela : [];
const vSubs = DATA.financeiro && DATA.financeiro.subscriptions ? DATA.financeiro.subscriptions : [];
const aData = DATA.financeiro_asaas && DATA.financeiro_asaas.data ? DATA.financeiro_asaas.data : {};

console.log('=== VERIFYING COURSES MAP AND METRICS ===');
const courses = {};

const getCourseObj = c => {
    c = resolveCanonicalCourse(c);
    if (!courses[c]) {
        courses[c] = {
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
            projecao_mensal_18m: Array(18).fill(0),
            historico_mensal: {}
        };
    }
    return courses[c];
};

// 1. Process Students
(DATA.students || []).forEach(s => {
    if (isInvalidOrInternal(s)) return;
    const c = resolveCanonicalCourse(s.curso);
    const co = getCourseObj(c);
    co.alunos_total++;

    const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
    const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
    const isCancel = vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled' || s.status === 'Cancelado';
    const isConcluido = !isCancel && (vSt === 'quitado' || aSt === 'quitado' || s.status === 'Concluído' || s.status === 'Encerrado' || s.turma_encerrada === true);

    if (!isCancel && !isConcluido) {
        co.alunos_vigentes++;
    }
});

// 2. Process Faturas
[...vFaturas, ...aFaturas].forEach(f => {
    const em = (f.email || '').toString().toLowerCase().trim();
    const nm = (f.aluno || '').toString().toLowerCase().trim();
    const c = resolveCanonicalCourse(f.curso || emailToCourse[em] || nameToCourse[nm]);
    const co = getCourseObj(c);

    const val = Number(f.valor) || 0;
    const st = (f.status || '').toLowerCase();
    const dtPag = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
    const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();

    if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
        co.pago_total += val;
        const ym = (f.data_pagamento_iso || dtPag).slice(0, 7);
        if (ym) {
            co.historico_mensal[ym] = (co.historico_mensal[ym] || 0) + val;
        }
        if (dtPag.includes('09/2026') || dtPag.includes('2026-09') || dtPag.includes('/09/26')) {
            co.pago_mes_atual += val;
        } else if (dtPag.includes('08/2026') || dtPag.includes('2026-08') || dtPag.includes('/08/26')) {
            co.pago_mes_ant += val;
        }
    } else if (st === 'em_atraso' || st === 'overdue') {
        co.atraso += val;
        co.qtd_atraso++;
    } else if (st === 'futuro' || st === 'a_vencer' || st === 'pending' || st === 'pendente') {
        if (dtVenc.includes('09/2026') || dtVenc.includes('2026-09') || dtVenc.includes('/09/26')) {
            co.proj_mes_atual += val;
        }
    }
});

// 3. Process Subscriptions (Vindi)
vSubs.forEach(sub => {
    if (sub.status_financeiro === 'adimplente') {
        const em = (sub.customer_email || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(sub.curso || emailToCourse[em]);
        const co = getCourseObj(c);
        const price = Number(sub.valor_parcela) || 0;
        co.mrr += price;

        const prox = (sub.proximo_vencimento || '').toString();
        if (prox.includes('/09/2026') || prox.includes('/09/26') || prox.includes('2026-09')) {
            co.proj_mes_atual += price;
            co.proj_1m += price;
        } else if (prox.includes('/10/2026') || prox.includes('/10/26') || prox.includes('2026-10')) {
            const dia = parseInt(prox.split('/')[0] || '0', 10);
            if (dia <= 14) {
                co.proj_1m += price;
            }
        } else if (!prox) {
            co.proj_mes_atual += price;
            co.proj_1m += price;
        }

        // 18-month simulation for this subscription
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
                co.projecao_mensal_18m[m] += price;
            }
        }
    }
});

// 4. Process Asaas Active Customers
Object.values(aData).forEach(stInfo => {
    if (stInfo.status_financeiro === 'adimplente') {
        const em = (stInfo.customer_email || stInfo.email || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(stInfo.curso || emailToCourse[em]);
        const co = getCourseObj(c);
        const price = Number(stInfo.valor_parcela || stInfo.mrr) || 0;
        co.mrr += price;
    }
});

// 5. Asaas Pending Faturas into 18m
aFaturas.forEach(f => {
    const st = (f.status || '').toLowerCase();
    if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
        const em = (f.email || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(f.curso || emailToCourse[em]);
        const co = getCourseObj(c);
        const val = Number(f.valor) || 0;
        const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
        if (dtVenc) {
            const dObj = new Date(dtVenc.slice(0, 10));
            const hoje = new Date();
            const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
            if (diffMeses >= 0 && diffMeses < 18) {
                co.projecao_mensal_18m[diffMeses] += val;
            }
        }
    }
});

// 6. Calculate projections and consolidations
Object.values(courses).forEach(co => {
    co.previsto_mes_vigente = co.pago_mes_atual + co.proj_mes_atual;
    const mArr = co.projecao_mensal_18m;
    co.proj_1m = mArr[0] > 0 ? mArr[0] : (co.proj_1m || co.mrr);
    co.proj_3m = mArr.slice(0, 3).reduce((a, b) => a + b, 0);
    co.proj_6m = mArr.slice(0, 6).reduce((a, b) => a + b, 0);
    co.proj_12m = mArr.slice(0, 12).reduce((a, b) => a + b, 0);
});

console.log('COURSE | VIGENTES | REALIZADO TOTAL | REALIZADO SET/26 | PROJETADO SET/26 | PREVISTO SET/26 | MRR | ATRASO');
Object.values(courses).sort((a,b) => b.pago_total - a.pago_total).forEach(co => {
    console.log(
        co.curso.slice(0, 30).padEnd(30) + ' | ' +
        String(co.alunos_vigentes).padStart(3) + ' vig (' + String(co.alunos_total).padStart(3) + ' tot) | R$ ' +
        co.pago_total.toFixed(2).padStart(11) + ' | R$ ' +
        co.pago_mes_atual.toFixed(2).padStart(9) + ' | R$ ' +
        co.proj_mes_atual.toFixed(2).padStart(9) + ' | R$ ' +
        co.previsto_mes_vigente.toFixed(2).padStart(9) + ' | R$ ' +
        co.mrr.toFixed(2).padStart(9) + ' | R$ ' +
        co.atraso.toFixed(2).padStart(9)
    );
});

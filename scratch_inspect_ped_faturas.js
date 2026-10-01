const DATA = require('./extracted_data.js');

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

const rawStudents = (DATA.students || []);
const emailToCourse = {};
rawStudents.forEach(s => {
    const em = (s.email || '').toString().toLowerCase().trim();
    const c = resolveCanonicalCourse(s.curso);
    if (em) emailToCourse[em] = c;
});

const vSubs = (DATA.financeiro && DATA.financeiro.subscriptions) || [];
const pedSubs = vSubs.filter(sub => {
    const em = (sub.customer_email || '').toString().toLowerCase().trim();
    const c = resolveCanonicalCourse(sub.curso || emailToCourse[em]);
    return c === 'POS-GRADUACAO EM INFECTOPEDIATRIA';
});

console.log('--- PED SUBS ANALYSIS ---');
pedSubs.forEach(sub => {
    if (sub.status_financeiro === 'adimplente') {
        const fatDates = (sub.faturas || []).map(f => ({
            id: f.id,
            status: f.status,
            valor: f.valor,
            venc: f.vencimento,
            pag: f.data_pagamento
        }));
        console.log(`\nSub ${sub.subscription_id} (${sub.customer_name}): plano="${sub.plano}", val=${sub.valor_parcela}, prox_venc="${sub.proximo_vencimento}"`);
        console.log(`  faturas count: ${fatDates.length}, paid: ${fatDates.filter(f => f.status==='paid'||f.status==='pago').length}`);
        console.log('  faturas list:', JSON.stringify(fatDates));
    }
});

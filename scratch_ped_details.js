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
const nameToCourse = {};
rawStudents.forEach(s => {
    const em = (s.email || '').toString().toLowerCase().trim();
    const nm = (s.nome || '').toString().toLowerCase().trim();
    const c = resolveCanonicalCourse(s.curso);
    if (em) emailToCourse[em] = c;
    if (nm) nameToCourse[nm] = c;
});

const vSubs = (DATA.financeiro && DATA.financeiro.subscriptions) || [];
const pedSubs = vSubs.filter(sub => {
    const em = (sub.customer_email || '').toString().toLowerCase().trim();
    const c = resolveCanonicalCourse(sub.curso || emailToCourse[em]);
    return c === 'POS-GRADUACAO EM INFECTOPEDIATRIA';
});

console.log('Total PED subs:', pedSubs.length);

let mrr = 0;
pedSubs.forEach((sub, idx) => {
    const price = Number(sub.valor_parcela) || 0;
    const faturasArr = sub.faturas || [];
    const paidFaturas = faturasArr.filter(f => f.status === 'paid' || f.status === 'pago');
    const futureFaturas = faturasArr.filter(f => f.status !== 'paid' && f.status !== 'pago' && f.status !== 'canceled');
    
    // Check start date / billing dates
    const planoStr = (sub.plano || '').toString().toUpperCase();
    let totalCycles = 18;
    if (planoStr.includes('24')) totalCycles = 24;
    else if (planoStr.includes('12') || planoStr.includes('ANUAL')) totalCycles = 12;
    else if (planoStr.includes('6') || planoStr.includes('SEMESTRAL')) totalCycles = 6;
    
    const remainingCycles = Math.max(0, totalCycles - paidFaturas.length);
    
    if (sub.status_financeiro === 'adimplente') {
        mrr += price;
    }

    console.log(`[${idx+1}] ${sub.customer_name} | status_fin: ${sub.status_financeiro} | valor: ${price} | plano: ${sub.plano} | totalCycles: ${totalCycles} | paid: ${paidFaturas.length} | remCycles: ${remainingCycles} | totalFaturasInSub: ${faturasArr.length}`);
});

console.log('Computed MRR for PED:', mrr);

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

function parsePlanCyclesOld(planoStr) {
    const planoStrUpper = (planoStr || '').toString().toUpperCase();
    let totalCycles = 18;
    if (planoStrUpper.includes('24')) totalCycles = 24;
    else if (planoStrUpper.includes('12') || planoStrUpper.includes('ANUAL')) totalCycles = 12;
    else if (planoStrUpper.includes('6') || planoStrUpper.includes('SEMESTRAL')) totalCycles = 6;
    return totalCycles;
}

function parsePlanCyclesNew(planoStr) {
    if (!planoStr) return 18;
    const p = planoStr.toString().toUpperCase().trim();
    if (p.includes('À VISTA') || p.includes('A VISTA')) return 1;
    const mX = p.match(/\b(\d+)\s*X\b/);
    if (mX) return parseInt(mX[1], 10);
    const mWord = p.match(/\b(\d+)\s*(?:MESES|PARCELAS|VEZES)\b/);
    if (mWord) return parseInt(mWord[1], 10);
    const mHyphen = p.match(/-\s*(\d+)(?!\s*%)(\s*X)?$/);
    if (mHyphen) return parseInt(mHyphen[1], 10);
    if (p.includes('RESIDENTES 24')) return 24;
    if (p.includes('ANUAL')) return 12;
    if (p.includes('SEMESTRAL')) return 6;
    if (p.includes('PÓS') || p.includes('POS') || p.includes('MENSALIDADE')) return 18;
    return 12;
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

// Simulate OLD vs NEW
const oldSim = Array(18).fill(0);
const newSim = Array(18).fill(0);

pedSubs.forEach(sub => {
    if (sub.status_financeiro === 'adimplente') {
        const price = Number(sub.valor_parcela) || 0;
        const faturasArr = sub.faturas || [];
        const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;

        // Old
        const oldCycles = parsePlanCyclesOld(sub.plano);
        const oldRem = Math.max(0, oldCycles - paidCount);
        for (let m = 0; m < 18; m++) {
            if (m < oldRem) oldSim[m] += price;
        }

        // New
        const newCycles = parsePlanCyclesNew(sub.plano);
        const newRem = Math.max(0, newCycles - paidCount);
        for (let m = 0; m < 18; m++) {
            if (m < newRem) newSim[m] += price;
        }
    }
});

const meses = ['Set/26', 'Out/26', 'Nov/26', 'Dez/26', 'Jan/27', 'Fev/27', 'Mar/27', 'Abr/27', 'Mai/27', 'Jun/27', 'Jul/27', 'Ago/27', 'Set/27', 'Out/27'];
console.log('Month   | Old Sim   | New Sim');
console.log('-----------------------------');
for (let i = 0; i < 14; i++) {
    console.log(`${meses[i]}  | ${oldSim[i].toFixed(1).padStart(9, ' ')} | ${newSim[i].toFixed(1).padStart(9, ' ')}`);
}

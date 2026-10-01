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

const courses = [
    'POS-GRADUACAO EM INFECTOPEDIATRIA',
    'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES',
    'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)',
    'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'
];

courses.forEach(cName => {
    const cSubs = vSubs.filter(sub => {
        const em = (sub.customer_email || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(sub.curso || emailToCourse[em]);
        return c === cName;
    });

    let mrr = 0;
    const sim = Array(18).fill(0);

    cSubs.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const price = Number(sub.valor_parcela) || 0;
            mrr += price;
            const faturasArr = sub.faturas || [];
            const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
            const cycles = parsePlanCyclesNew(sub.plano);
            const remaining = Math.max(0, cycles - paidCount);
            for (let m = 0; m < 18; m++) {
                if (m < remaining) sim[m] += price;
            }
        }
    });

    console.log(`\n=== ${cName} ===`);
    console.log(`MRR: R$ ${mrr.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
    console.log(`Simulação próximos 12 meses:`);
    const meses = ['Set/26', 'Out/26', 'Nov/26', 'Dez/26', 'Jan/27', 'Fev/27', 'Mar/27', 'Abr/27', 'Mai/27', 'Jun/27', 'Jul/27', 'Ago/27'];
    for (let i = 0; i < 12; i++) {
        console.log(`  ${meses[i]}: R$ ${sim[i].toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
    }
});

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

function parsePlanCycles(planoStr) {
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
    if (p.includes('SEMESTRAL') || p.match(/\b6\s*X\b/)) return 6;
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

const simWithOffset = Array(18).fill(0);
let pedMrr = 0;
let aVencerSetembro = 0;

pedSubs.forEach(sub => {
    if (sub.status_financeiro === 'adimplente') {
        const price = Number(sub.valor_parcela) || 0;
        pedMrr += price;

        const prox = (sub.proximo_vencimento || '').toString();
        const faturasArr = sub.faturas || [];
        const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
        const totalCycles = parsePlanCycles(sub.plano);
        const remainingCycles = Math.max(0, totalCycles - paidCount);

        // Check if student already paid for September 2026
        const paidSept = faturasArr.some(f => {
            const dt = (f.data_pagamento || f.data_pagamento_iso || '').toString();
            return (f.status === 'paid' || f.status === 'pago') && (dt.includes('09/2026') || dt.includes('2026-09') || dt.includes('/09/26'));
        });

        // Determine starting month index for future installments:
        // m = 0 is September 2026
        // If already paid in Sept or prox_venc is Oct/2026+, first remaining installment is due in October (m = 1)
        // Otherwise, first remaining installment is due in September (m = 0)
        let startM = 0;
        if (paidSept || prox.includes('/10/2026') || prox.includes('2026-10') || prox.includes('/10/26')) {
            startM = 1;
        } else {
            aVencerSetembro += price;
        }

        for (let i = 0; i < remainingCycles; i++) {
            const targetM = startM + i;
            if (targetM < 18) {
                simWithOffset[targetM] += price;
            }
        }
    }
});

console.log('PED MRR:', pedMrr);
console.log('PED A Vencer Setembro (calculado):', aVencerSetembro);
const meses = ['Set/26', 'Out/26', 'Nov/26', 'Dez/26', 'Jan/27', 'Fev/27', 'Mar/27', 'Abr/27', 'Mai/27', 'Jun/27', 'Jul/27', 'Ago/27', 'Set/27', 'Out/27'];
console.log('\nProjeção com Offset:');
for (let i = 0; i < 14; i++) {
    console.log(`  ${meses[i]}: R$ ${simWithOffset[i].toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
}

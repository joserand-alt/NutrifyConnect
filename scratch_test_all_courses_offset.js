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
const aFaturas = (DATA.financeiro_asaas && DATA.financeiro_asaas.faturas_tabela) || [];

const coursesMap = {};
const getCourse = (cName) => {
    const c = resolveCanonicalCourse(cName);
    if (!coursesMap[c]) {
        coursesMap[c] = {
            curso: c,
            mrr: 0,
            proj_mes_atual: 0,
            pago_mes_atual: 0,
            projecao_18m_sim: Array(18).fill(0)
        };
    }
    return coursesMap[c];
};

// 1. Vindi Subs
vSubs.forEach(sub => {
    if (sub.status_financeiro === 'adimplente') {
        const em = (sub.customer_email || '').toString().toLowerCase().trim();
        const cm = getCourse(sub.curso || emailToCourse[em]);
        const price = Number(sub.valor_parcela) || 0;
        cm.mrr += price;

        const prox = (sub.proximo_vencimento || '').toString();
        const faturasArr = sub.faturas || [];
        const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
        const totalCycles = parsePlanCycles(sub.plano);
        const remainingCycles = Math.max(0, totalCycles - paidCount);

        const paidSept = faturasArr.some(f => {
            const dt = (f.data_pagamento || f.data_pagamento_iso || '').toString();
            return (f.status === 'paid' || f.status === 'pago') && (dt.includes('09/2026') || dt.includes('2026-09') || dt.includes('/09/26'));
        });

        let startM = 0;
        if (paidSept || prox.includes('/10/2026') || prox.includes('2026-10') || prox.includes('/10/26')) {
            startM = 1;
        } else {
            cm.proj_mes_atual += price;
        }

        for (let i = 0; i < remainingCycles; i++) {
            const targetM = startM + i;
            if (targetM < 18) {
                cm.projecao_18m_sim[targetM] += price;
            }
        }
    }
});

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

// 2. Asaas future invoices
aFaturas.forEach(f => {
    const st = (f.status || '').toLowerCase();
    const isPendingOrFuture = (st === 'pendente' || st === 'pending' || st === 'a_vencer' || st === 'futuro' || st === 'confirmed' || st === 'a vencer');
    if (isPendingOrFuture) {
        const em = (f.email || '').toString().toLowerCase().trim();
        const cm = getCourse(f.curso || emailToCourse[em]);
        const val = Number(f.valor) || 0;
        const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
        const dObj = _parseDateSafe(dtVenc);
        if (dObj) {
            const base = new Date(2026, 8, 1);
            const diffMeses = (dObj.getFullYear() - base.getFullYear()) * 12 + (dObj.getMonth() - base.getMonth());
            if (diffMeses >= 0 && diffMeses < 18) {
                cm.projecao_18m_sim[diffMeses] += val;
            }
        }
    }
});

const meses = ['Set/26', 'Out/26', 'Nov/26', 'Dez/26', 'Jan/27', 'Fev/27', 'Mar/27', 'Abr/27'];
Object.values(coursesMap).forEach(cm => {
    console.log(`\nCurso: ${cm.curso}`);
    console.log(`  MRR: R$ ${cm.mrr.toFixed(2)} | A vencer Setembro: R$ ${cm.proj_mes_atual.toFixed(2)}`);
    console.log(`  Projeção:`);
    for (let i = 0; i < 8; i++) {
        console.log(`    ${meses[i]}: R$ ${cm.projecao_18m_sim[i].toFixed(2)}`);
    }
});

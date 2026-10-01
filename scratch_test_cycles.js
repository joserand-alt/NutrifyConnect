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

function parseCycles(planoStr) {
    const p = (planoStr || '').toUpperCase();
    // Look for explicit regex patterns like '18X', '24X', '12X', '10X', '6X', '3X', '24 MESES', etc.
    const mX = p.match(/(\d+)\s*(?:X|VEZES|PARCELAS|MESES)/);
    if (mX) {
        return parseInt(mX[1], 10);
    }
    if (p.includes('24X') || p.includes('24 X') || p.includes('- 24')) return 24;
    if (p.includes('18X') || p.includes('18 X') || p.includes('- 18')) return 18;
    if (p.includes('12X') || p.includes('12 X') || p.includes('- 12') || p.includes('ANUAL')) return 12;
    if (p.includes('10X') || p.includes('10 X') || p.includes('- 10')) return 10;
    if (p.includes('SEMESTRAL') || p.includes('6X') || p.includes('6 X')) return 6;
    if (p.includes('3X') || p.includes('3 X')) return 3;
    if (p.includes('A VISTA') || p.includes('À VISTA')) return 1;
    // Default for Pós-Graduação is 18 months
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

console.log('Testing cycle parsing for PED plans:');
const planTested = {};
pedSubs.forEach(s => {
    if (!planTested[s.plano]) {
        planTested[s.plano] = parseCycles(s.plano);
        console.log(`Plano: "${s.plano}" -> Parsed Cycles: ${planTested[s.plano]}`);
    }
});

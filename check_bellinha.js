const DATA = require('./temp_data.js'); 
const rawStudents = DATA.students || []; 
const isInvalidOrInternal = (s) => { 
    const em = (s.email || '').toString().toLowerCase().trim(); 
    if (!em || em.indexOf('@') === -1) return true; 
    if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@cativa') || em.includes('@estrategia1') || em.includes('@adtivo') || em.includes('teste')) return true; 
    if (em === 'gcotta29@gmail.com' || em === 'j.o.s.e.r.a.n.d@gmail.com' || em === 'email@email.com') return true; 
    if ((s.nome || '').toLowerCase().includes('teste')) return true; 
    return false; 
}; 
const normalizeCourse = (cName) => { 
    if (!cName) return 'PLATAFORMA GERAL'; 
    let s = cName.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().trim(); 
    if (s.includes('INFECTOPEDIATRIA') || s.includes('PEDIATRIA')) return 'POS-GRADUACAO EM INFECTOPEDIATRIA'; 
    if (s.includes('IMUNODEPRIMIDO')) return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'; 
    if (s.includes('ORTOPEDIC') || s.includes('PARTES MOLES')) return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES'; 
    if (s.includes('CCIH') || s.includes('HOSPITALAR')) return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'; 
    if (s.includes('TERAPIA INTENSIVA') || s.includes('UTI')) return 'POS-GRADUACAO EM INFECTOLOGIA EM TERAPIA INTENSIVA'; 
    if (s.includes('ANTIBIOTICO') || s.includes('SOS')) return 'S.O.S ANTIBIOTICO'; 
    if (s.includes('FUNGO') || s.includes('ANTIFUNGICO')) return 'DO FUNGO AO ANTIFUNGICO'; 
    if (s.includes('MULTI-R') || s.includes('JORNADA')) return 'JORNADA MULTI-R'; 
    if (s.includes('GESTACAO') || s.includes('GESTANTE')) return 'INFECCOES NA GESTACAO'; 
    if (s.includes('HIV') || s.includes('HEPATITE')) return 'HIV E HEPATITES VIRAIS'; 
    if (s.includes('INFECTOCAST')) return 'POS-GRADUACAO INFECTOCAST'; 
    return s; 
}; 
const parseDateUniversal = (ds) => { 
    if (!ds) return null; 
    let d = new Date(ds); 
    if (!isNaN(d.getTime())) return d; 
    const m = ds.match(/^(\d{2})[\/\-](\d{2})[\/\-](\d{4})/); 
    if (m) { 
        return new Date(m[3], parseInt(m[2])-1, m[1]); 
    } 
    return null; 
}; 
const validStudents = rawStudents.filter(s => !isInvalidOrInternal(s)); 
const now = new Date(DATA.last_updated || Date.now()); 
const vFats = (DATA.financeiro || {}).faturas_tabela || []; 
const aFats = (DATA.financeiro_asaas || {}).faturas_tabela || []; 
const allBills = vFats.concat(aFats); 
const studentCoursePaidBills = new Map(); 
allBills.forEach(f => { 
    const st = (f.status || '').toLowerCase(); 
    if (st !== 'paid' && st !== 'pago' && st !== 'received' && st !== 'confirmed') return; 
    const em = (f.email || '').toString().toLowerCase().trim(); 
    const nm = (f.cliente || f.customer_name || '').toString().toLowerCase().trim(); 
    const cNorm = normalizeCourse(f.plano || f.description || f.descricao || ''); 
    if (!em && !nm) return; 
    let d = null; 
    const dp = f.data_pagamento_iso || f.data_pagamento || f.vencimento_iso; 
    if (dp) { d = new Date(dp); if (isNaN(d.getTime())) d = null; } 
    if (!d) return; 
    [em, nm].forEach(k => { 
        if (!k) return; 
        ['___' + cNorm, '___GLOBAL'].forEach(suf => { 
            const key = k + suf; 
            if (!studentCoursePaidBills.has(key)) studentCoursePaidBills.set(key, []); 
            studentCoursePaidBills.get(key).push({ date: d, gateway: f.gateway || 'API', val: f.valor_pago || f.valor || 0 }); 
        }); 
    }); 
}); 
const matriculasConfirmadas = []; 
const matriculasPendentes = []; 
const processedPairs = new Set(); 
validStudents.forEach(s => { 
    const em = (s.email || '').toString().toLowerCase().trim(); 
    const nm = (s.nome || '').toString().trim(); 
    const cNorm = normalizeCourse(s.curso || ''); 
    const pairKey = em + '___' + cNorm; 
    if (processedPairs.has(pairKey)) return; 
    processedPairs.add(pairKey); 
    const targetBills = studentCoursePaidBills.get(em + '___' + cNorm) || studentCoursePaidBills.get(nm.toLowerCase() + '___' + cNorm) || studentCoursePaidBills.get(em + '___GLOBAL') || studentCoursePaidBills.get(nm.toLowerCase() + '___GLOBAL'); 
    if (targetBills && targetBills.length > 0) { 
        targetBills.sort((a, b) => a.date - b.date); 
        const firstPaid = targetBills[0]; 
        const effDate = firstPaid.date; 
        if (effDate && effDate <= now) { 
            matriculasConfirmadas.push({ email: em, curso: s.curso, data: effDate, tipo: 'confirmada', nome: s.nome }); 
        } 
    } else { 
        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase(); 
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase(); 
        const vindiCanceled = vSt === 'cancelado' || vSt === 'canceled'; 
        const asaasCanceled = aSt === 'cancelado' || aSt === 'canceled'; 
        const vindiActive = s.vindi && (s.vindi.status_assinatura === 'active' || s.vindi.status_financeiro === 'adimplente'); 
        const asaasActive = s.asaas && (s.asaas.status_assinatura === 'active' || s.asaas.status_financeiro === 'adimplente' || s.asaas.status_financeiro === 'pago'); 
        const vF = s.vindi ? (s.vindi.faturas || []) : []; 
        const aF = s.asaas ? (s.asaas.faturas || []) : []; 
        const vPaid = vF.some(f => (f.status === 'pago' || f.status === 'paid' || f.pago)); 
        const aPaid = aF.some(f => (f.status === 'pago' || f.status === 'paid' || f.status === 'RECEIVED' || f.status === 'CONFIRMED' || f.pago)); 
        const hasFinanceiro = vindiActive || asaasActive || vPaid || aPaid; 
        const hasConsumo = (Number(s.aulas_feitas || 0) > 0); 
        let isPendente = false; 
        if ((vindiCanceled || asaasCanceled) && !vindiActive && !asaasActive && !hasConsumo) { 
            isPendente = false; 
        } else if (!hasFinanceiro && !hasConsumo && s.status !== 'Concluído') { 
            isPendente = true; 
        } 
        if (isPendente) { 
            const rawInscStr = s.data_insc || s.data_inscricao || s.data_matricula || s.first || (s.asaas && s.asaas.faturas && s.asaas.faturas[0] && (s.asaas.faturas[0].data_criacao || s.asaas.faturas[0].dateCreated || s.asaas.faturas[0].vencimento_iso || s.asaas.faturas[0].vencimento)) || (s.vindi && s.vindi.faturas && s.vindi.faturas[0] && (s.vindi.faturas[0].vencimento_iso || s.vindi.faturas[0].vencimento)) || s.created_at; 
            const dtInsc = parseDateUniversal(rawInscStr); 
            if (dtInsc && dtInsc <= now) { 
                matriculasPendentes.push({ email: em, curso: s.curso, data: dtInsc, tipo: 'pendente', nome: s.nome }); 
            } 
        } 
    } 
}); 
const allMatriculas = [...matriculasConfirmadas, ...matriculasPendentes]; 
allMatriculas.sort((a, b) => b.data - a.data); 
console.log('Top 15 Últimas Matrículas (Confirmadas e Pendentes):'); 
allMatriculas.slice(0, 15).forEach(m => { 
    console.log('[' + m.tipo.toUpperCase() + '] ' + m.email + ' - ' + m.data.toISOString().split('T')[0] + ' - ' + (m.curso || 'PLATAFORMA GERAL')); 
});

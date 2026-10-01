import os, re

dash_dir = r'C:\Users\DELL\Desktop\Dash_InfectoCast'
template_path = os.path.join(dash_dir, 'template.html')

with open(template_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update getMatriculasAuditoriaData
start_fn = code.find('function getMatriculasAuditoriaData()')
end_fn = code.find('function getSync24hData()', start_fn)

new_get_data = '''function getMatriculasAuditoriaData() {
    const rawStudents = (DATA && DATA.students) ? DATA.students : [];
    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
    const vFaturas = (vindi.faturas_tabela || []);
    const aFaturas = (asaas.faturas_tabela || []);

    const isInvalidOrInternal = s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const cr = (s.curso || '').toString().toUpperCase().trim();
        if (cr.includes('NUTRIFY')) return true;
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@cativa') || em.includes('@estrategia1') || em.includes('@adtivo')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com') || em.includes('wgww@gmail.com')) return true;
        return false;
    };

    function normalizeCourse(cName) {
        if (!cName) return 'GERAL';
        let s = String(cName).toUpperCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
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
    }

    // 1. Mapear TODOS os pagamentos aprovados no gateway por aluno e por curso
    const studentCoursePaidBills = new Map();
    const allFats = [...vFaturas, ...aFaturas];

    allFats.forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const nm = (f.aluno || '').toString().toLowerCase().trim();
            const dt = parseDateUniversal(f.data_pagamento || f.data_pagamento_iso || f.vencimento || f.vencimento_iso);
            const gw = f.gateway || (vFaturas.includes(f) ? 'Vindi' : 'Asaas');
            const cNorm = normalizeCourse(f.plano || f.description || f.curso || '');
            
            if (dt) {
                const keys = [];
                if (em) keys.push(em + '___' + cNorm, em + '___GLOBAL');
                if (nm) keys.push(nm + '___' + cNorm, nm + '___GLOBAL');
                
                keys.forEach(k => {
                    if (!studentCoursePaidBills.has(k)) studentCoursePaidBills.set(k, []);
                    studentCoursePaidBills.get(k).push({ date: dt, gateway: gw, valor: f.valor, plano: f.plano || f.description });
                });
            }
        }
    });

    const now = new Date();
    const t24h = new Date(now.getTime() - 24 * 3600 * 1000);
    const t30d = new Date(now.getTime() - 30 * 24 * 3600 * 1000);

    const validStudents = rawStudents.filter(s => !isInvalidOrInternal(s));
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

        const paidBillsCourse = studentCoursePaidBills.get(em + '___' + cNorm) || studentCoursePaidBills.get(nm.toLowerCase() + '___' + cNorm);
        const paidBillsGlobal = studentCoursePaidBills.get(em + '___GLOBAL') || studentCoursePaidBills.get(nm.toLowerCase() + '___GLOBAL');
        const targetBills = paidBillsCourse || paidBillsGlobal;

        // 1. Matrícula Confirmada (Tem pagamento aprovado no gateway)
        if (targetBills && targetBills.length > 0) {
            targetBills.sort((a, b) => a.date - b.date);
            const firstPaid = targetBills[0];
            const effDate = firstPaid.date;

            if (effDate && effDate <= now) {
                const pad = n => n < 10 ? '0' + n : n;
                const dtFmt = pad(effDate.getDate()) + '/' + pad(effDate.getMonth()+1) + '/' + effDate.getFullYear() + ' ' + pad(effDate.getHours()) + ':' + pad(effDate.getMinutes());
                
                matriculasConfirmadas.push({
                    nome: nm || 'Aluno',
                    email: em,
                    curso: s.curso || 'PLATAFORMA GERAL',
                    data: effDate,
                    data_fmt: dtFmt,
                    origem: 'Primeiro Pagamento (' + firstPaid.gateway + ')',
                    gateway: firstPaid.gateway,
                    tipo: 'confirmada',
                    origem_label: 'Matrícula Confirmada',
                    valor: firstPaid.valor,
                    is_24h: effDate >= t24h,
                    is_30d: effDate >= t30d
                });
            }
        } else {
            // 2. Matrícula Pendente (Mesma regra da Visão por Curso: sem financeiro e sem consumo)
            const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
            const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
            const vindiCanceled = vSt === 'cancelado' || vSt === 'canceled';
            const asaasCanceled = aSt === 'cancelado' || aSt === 'canceled';
            const vindiActive = vSt === 'active' || vSt === 'ativo' || vSt === 'adimplente' || vSt === 'em_dia';
            const asaasActive = aSt === 'active' || aSt === 'ativo' || aSt === 'received' || aSt === 'confirmed' || aSt === 'adimplente' || aSt === 'em_dia';
            const vFats = s.vindi ? (s.vindi.faturas || []) : [];
            const aFats = s.asaas ? (s.asaas.faturas || []) : [];
            const vPaid = vFats.some(f => (f.status === 'pago' || f.status === 'paid' || f.pago));
            const aPaid = aFats.some(f => (f.status === 'pago' || f.status === 'paid' || f.status === 'RECEIVED' || f.status === 'CONFIRMED' || f.pago));

            const hasFinanceiro = vindiActive || asaasActive || vPaid || aPaid;
            const hasConsumo = (Number(s.aulas_feitas || 0) > 0);

            let isPendente = false;
            if ((vindiCanceled || asaasCanceled) && !vindiActive && !asaasActive && !hasConsumo) {
                isPendente = false;
            } else if (!hasFinanceiro && !hasConsumo && s.status !== 'Concluído') {
                isPendente = true;
            }

            if (isPendente) {
                const dtInsc = parseDateUniversal(s.data_insc || s.data_inscricao || s.data_matricula || s.first);
                if (dtInsc && dtInsc <= now) {
                    const pad = n => n < 10 ? '0' + n : n;
                    const dtFmt = pad(dtInsc.getDate()) + '/' + pad(dtInsc.getMonth()+1) + '/' + dtInsc.getFullYear() + ' ' + pad(dtInsc.getHours()) + ':' + pad(dtInsc.getMinutes());
                    
                    matriculasPendentes.push({
                        nome: nm || 'Lead / Inscrição',
                        email: em,
                        curso: s.curso || 'PLATAFORMA GERAL',
                        data: dtInsc,
                        data_fmt: dtFmt,
                        origem: 'Cadastro Plataforma (' + (s.plataforma || 'Academy') + ')',
                        gateway: s.plataforma || 'Academy',
                        tipo: 'pendente',
                        origem_label: 'Matrícula Pendente (Aguardando Pagamento)',
                        valor: 0,
                        aulas_feitas: Number(s.aulas_feitas || 0),
                        is_24h: dtInsc >= t24h,
                        is_30d: dtInsc >= t30d
                    });
                }
            }
        }
    });

    matriculasConfirmadas.sort((a, b) => b.data - a.data);
    matriculasPendentes.sort((a, b) => b.data - a.data);

    const list24h = matriculasConfirmadas.filter(m => m.is_24h);
    const list30d = matriculasConfirmadas.filter(m => m.is_30d);

    const pendentes24h = matriculasPendentes.filter(m => m.is_24h);
    const pendentes30d = matriculasPendentes.filter(m => m.is_30d);

    return {
        count24h: list24h.length,
        count30d: list30d.length,
        totalConfirmadas: matriculasConfirmadas.length,
        countPendentes24h: pendentes24h.length,
        countPendentes30d: pendentes30d.length,
        totalPendentes: matriculasPendentes.length,
        list24h,
        list30d,
        allRecords: matriculasConfirmadas,
        pendentes24h,
        pendentes30d,
        allPendentes: matriculasPendentes
    };
}

'''

code = code[:start_fn] + new_get_data + code[end_fn:]

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated getMatriculasAuditoriaData in template.html!")

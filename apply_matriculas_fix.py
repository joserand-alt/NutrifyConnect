import re
import sys
import subprocess

with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

# 1. New getMatriculasAuditoriaData
new_get_data = '''function getMatriculasAuditoriaData() {
    const rawStudents = (DATA && DATA.students) ? DATA.students : [];
    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
    const vFaturas = (vindi.faturas_tabela || []);
    const aFaturas = (asaas.faturas_tabela || []);

    const isInvalidOrInternal = s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || s.aluno || '').toString().toLowerCase().trim();
        const cr = (s.curso || s.plano || s.description || '').toString().toUpperCase().trim();
        if (cr.includes('NUTRIFY')) return true;
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@cativa') || em.includes('@estrategia1') || em.includes('@adtivo')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com') || em.includes('wgww@gmail.com')) return true;
        return false;
    };

    function normalizeCourse(cName) {
        if (!cName) return 'PLATAFORMA GERAL';
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

    // 1. Mapear data de matrícula/inscrição da plataforma Academy e Cativa
    const studentInscMap = new Map();
    rawStudents.forEach(s => {
        const em = (s.email || '').toLowerCase().trim();
        const nm = (s.nome || '').trim();
        const cNorm = normalizeCourse(s.curso || '');
        const dtStr = s.data_insc || s.data_inscricao || s.data_matricula || s.first;
        const dt = parseDateUniversal(dtStr);
        if (dt) {
            if (em) studentInscMap.set(em + '___' + cNorm, dt);
            if (nm) studentInscMap.set(nm.toLowerCase() + '___' + cNorm, dt);
            if (em) studentInscMap.set(em + '___GLOBAL', dt);
            if (nm) studentInscMap.set(nm.toLowerCase() + '___GLOBAL', dt);
        }
    });

    // 2. Mapear pagamentos aprovados no gateway por aluno e curso
    const allFats = [...vFaturas, ...aFaturas];
    const studentMap = new Map();

    allFats.forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            if (isInvalidOrInternal(f)) return;
            const dt = parseDateUniversal(f.data_pagamento || f.data_pagamento_iso || f.vencimento || f.vencimento_iso);
            if (dt) {
                const em = (f.email || '').toLowerCase().trim();
                const nm = (f.aluno || '').trim();
                const cNorm = normalizeCourse(f.plano || f.description || f.curso || '');
                const key = (em || nm.toLowerCase()) + '___' + cNorm;
                if (!studentMap.has(key)) {
                    studentMap.set(key, { nome: nm, email: em, curso: cNorm, bills: [] });
                }
                studentMap.get(key).bills.push({
                    date: dt,
                    valor: Number(f.valor) || 0,
                    gateway: f.gateway || (vFaturas.includes(f) ? 'Vindi' : 'Asaas'),
                    plano: f.plano || f.description
                });
            }
        }
    });

    const now = new Date();
    const t48hCalendar = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 2, 0, 0, 0);
    const t30dCalendar = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30, 0, 0, 0);

    const pad = n => n < 10 ? '0' + n : n;
    const formatDt = dt => {
        if (!dt) return '';
        return pad(dt.getDate()) + '/' + pad(dt.getMonth()+1) + '/' + dt.getFullYear() + (dt.getHours() === 0 && dt.getMinutes() === 0 ? '' : ' ' + pad(dt.getHours()) + ':' + pad(dt.getMinutes()));
    };

    const matriculasConfirmadas = [];

    studentMap.forEach(s => {
        s.bills.sort((a,b) => a.date - b.date);
        const firstBill = s.bills[0];
        const latestBill = s.bills[s.bills.length - 1];

        // Buscar data de inscrição original da plataforma
        const inscDt = studentInscMap.get(s.email + '___' + s.curso) || studentInscMap.get(s.nome.toLowerCase() + '___' + s.curso) || studentInscMap.get(s.email + '___GLOBAL') || studentInscMap.get(s.nome.toLowerCase() + '___GLOBAL');
        
        // A verdadeira data de matrícula é a menor entre a inscrição e o primeiro pagamento
        let matriculaDate = firstBill.date;
        if (inscDt && inscDt < matriculaDate) {
            matriculaDate = inscDt;
        }

        // Verificar se o plano menciona safra anterior (ex: Março/26, 18X)
        const desc = (latestBill.plano || '').toLowerCase();
        if (desc.includes('março/26') || desc.includes('marco/26') || desc.includes('mar/26')) {
            const dMar = new Date(2026, 2, 1);
            if (dMar < matriculaDate) matriculaDate = dMar;
        }

        const diffMsMatricula = now.getTime() - matriculaDate.getTime();
        const diffMsLatest = now.getTime() - latestBill.date.getTime();

        const isNova48h = (matriculaDate >= t48hCalendar && matriculaDate <= now) || (diffMsMatricula >= -3600000 && diffMsMatricula <= 48 * 3600 * 1000) || (matriculaDate.getHours() === 0 && diffMsMatricula <= 72 * 3600 * 1000 && diffMsMatricula >= -3600000);
        const hasPaid48h = (latestBill.date >= t48hCalendar && latestBill.date <= now) || (diffMsLatest >= -3600000 && diffMsLatest <= 48 * 3600 * 1000) || (latestBill.date.getHours() === 0 && diffMsLatest <= 72 * 3600 * 1000 && diffMsLatest >= -3600000);
        const isRecorrencia48h = hasPaid48h && !isNova48h;

        const isNova30d = (matriculaDate >= t30dCalendar && matriculaDate <= now) || (diffMsMatricula <= 30 * 24 * 3600 * 1000);
        const hasPaid30d = (latestBill.date >= t30dCalendar && latestBill.date <= now) || (diffMsLatest <= 30 * 24 * 3600 * 1000);
        const isRecorrencia30d = hasPaid30d && !isNova30d;

        const safraStr = pad(matriculaDate.getMonth()+1) + '/' + matriculaDate.getFullYear();

        matriculasConfirmadas.push({
            nome: s.nome || 'Aluno',
            email: s.email,
            curso: s.curso || 'PLATAFORMA GERAL',
            data: matriculaDate,
            data_fmt: formatDt(matriculaDate),
            safra: safraStr,
            gateway: latestBill.gateway,
            tipo: 'confirmada',
            valor: isNova48h ? firstBill.valor : latestBill.valor,
            primeiro_pagamento_data: firstBill.date,
            primeiro_pagamento_fmt: formatDt(firstBill.date),
            primeiro_pagamento_valor: firstBill.valor,
            ultimo_pagamento_data: latestBill.date,
            ultimo_pagamento_fmt: formatDt(latestBill.date),
            ultimo_pagamento_valor: latestBill.valor,
            is_nova_48h: isNova48h,
            is_recorrencia_48h: isRecorrencia48h,
            is_nova_30d: isNova30d,
            is_recorrencia_30d: isRecorrencia30d,
            origem_label: isNova48h ? 'Nova Matrícula (1º Pagamento)' : (isRecorrencia48h ? `Mensalidade Paga (Safra ${safraStr})` : `Aluno da Base (Safra ${safraStr})`)
        });
    });

    // 3. Matrículas Pendentes (Alunos cadastrados na plataforma sem financeiro e sem uso)
    const validStudents = rawStudents.filter(s => !isInvalidOrInternal(s));
    const matriculasPendentes = [];

    validStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').trim();
        const cNorm = normalizeCourse(s.curso || '');
        const key = (em || nm.toLowerCase()) + '___' + cNorm;

        // Se já está confirmada no financeiro, não é pendente
        if (studentMap.has(key)) return;

        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
        const vindiCanceled = vSt === 'cancelado' || vSt === 'canceled';
        const asaasCanceled = aSt === 'cancelado' || aSt === 'canceled';
        const vindiActive = vSt === 'active' || vSt === 'ativo';
        const asaasActive = aSt === 'active' || aSt === 'ativo' || aSt === 'received' || aSt === 'confirmed';
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
            const rawInscStr = s.data_insc || s.data_inscricao || s.data_matricula || s.first || (s.asaas && s.asaas.faturas && s.asaas.faturas[0] && (s.asaas.faturas[0].data_criacao || s.asaas.faturas[0].dateCreated || s.asaas.faturas[0].vencimento_iso || s.asaas.faturas[0].vencimento)) || (s.vindi && s.vindi.faturas && s.vindi.faturas[0] && (s.vindi.faturas[0].vencimento_iso || s.vindi.faturas[0].vencimento)) || s.created_at;
            const dtInsc = parseDateUniversal(rawInscStr);
            if (dtInsc && dtInsc <= now) {
                const diffMs = now.getTime() - dtInsc.getTime();
                const is48h = (dtInsc >= t48hCalendar && dtInsc <= now) || (diffMs >= -3600000 && diffMs <= 48 * 3600 * 1000) || (dtInsc.getHours() === 0 && diffMs <= 72 * 3600 * 1000 && diffMs >= -3600000);
                const is30d = (dtInsc >= t30dCalendar && dtInsc <= now) || (diffMs <= 30 * 24 * 3600 * 1000);

                let fatVal = 0;
                let origStr = 'Cadastro Plataforma (' + (s.plataforma || 'Academy') + ')';
                if (s.asaas && s.asaas.faturas && s.asaas.faturas.length > 0) {
                    fatVal = Number(s.asaas.faturas[0].valor || 0);
                    origStr = 'Pedido Asaas (' + (s.asaas.faturas[0].forma_pagamento || 'Boleto/PIX') + ')';
                } else if (s.vindi && s.vindi.faturas && s.vindi.faturas.length > 0) {
                    fatVal = Number(s.vindi.faturas[0].valor || 0);
                    origStr = 'Assinatura Vindi';
                }

                matriculasPendentes.push({
                    nome: nm || 'Lead / Inscrição',
                    email: em,
                    curso: s.curso || 'PLATAFORMA GERAL',
                    data: dtInsc,
                    data_fmt: formatDt(dtInsc),
                    origem: origStr,
                    gateway: s.plataforma || 'Academy',
                    tipo: 'pendente',
                    origem_label: 'Matrícula Pendente (Aguardando Pagamento)',
                    valor: fatVal,
                    aulas_feitas: Number(s.aulas_feitas || 0),
                    is_nova_48h: is48h,
                    is_nova_30d: is30d,
                    is_recorrencia_48h: false,
                    is_recorrencia_30d: false
                });
            }
        }
    });

    matriculasConfirmadas.sort((a, b) => b.data - a.data);
    matriculasPendentes.sort((a, b) => b.data - a.data);

    const listNovas48h = matriculasConfirmadas.filter(m => m.is_nova_48h).sort((a,b) => b.data - a.data);
    const listRecorrencias48h = matriculasConfirmadas.filter(m => m.is_recorrencia_48h).sort((a,b) => b.ultimo_pagamento_data - a.ultimo_pagamento_data);
    const listTodasPagas48h = [...listNovas48h, ...listRecorrencias48h].sort((a,b) => b.ultimo_pagamento_data - a.ultimo_pagamento_data);

    const listNovas30d = matriculasConfirmadas.filter(m => m.is_nova_30d).sort((a,b) => b.data - a.data);
    const listRecorrencias30d = matriculasConfirmadas.filter(m => m.is_recorrencia_30d).sort((a,b) => b.ultimo_pagamento_data - a.ultimo_pagamento_data);
    const listTodasPagas30d = [...listNovas30d, ...listRecorrencias30d].sort((a,b) => b.ultimo_pagamento_data - a.ultimo_pagamento_data);

    const pendentes48h = matriculasPendentes.filter(m => m.is_nova_48h);
    const pendentes30d = matriculasPendentes.filter(m => m.is_nova_30d);

    return {
        countNovas48h: listNovas48h.length,
        countRecorrencias48h: listRecorrencias48h.length,
        countPagas48h: listTodasPagas48h.length,
        count48h: listNovas48h.length,
        count24h: listNovas48h.length,

        countNovas30d: listNovas30d.length,
        countRecorrencias30d: listRecorrencias30d.length,
        countPagas30d: listTodasPagas30d.length,
        count30d: listNovas30d.length,

        totalConfirmadas: matriculasConfirmadas.length,

        countPendentes48h: pendentes48h.length,
        countPendentes24h: pendentes48h.length,
        countPendentes30d: pendentes30d.length,
        totalPendentes: matriculasPendentes.length,

        listNovas48h,
        listRecorrencias48h,
        listTodasPagas48h,
        list48h: listNovas48h,
        list24h: listNovas48h,

        listNovas30d,
        listRecorrencias30d,
        listTodasPagas30d,
        list30d: listNovas30d,

        allRecords: matriculasConfirmadas,
        pendentes48h,
        pendentes24h: pendentes48h,
        pendentes30d,
        allPendentes: matriculasPendentes
    };
}'''

start_fn = tmpl.find('function getMatriculasAuditoriaData()')
end_fn = tmpl.find('function getSync24hData()')
if start_fn != -1 and end_fn != -1:
    tmpl = tmpl[:start_fn] + new_get_data + '\n\n' + tmpl[end_fn:]
    print("getMatriculasAuditoriaData successfully replaced!")
else:
    print("Could not find getMatriculasAuditoriaData bounds!")
    sys.exit(1)

with open('template.html', 'w', encoding='utf-8') as f:
    f.write(tmpl)

print("template.html updated successfully!")

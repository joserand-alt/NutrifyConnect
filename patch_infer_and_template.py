import os, re

dash_dir = r'C:\Users\DELL\Desktop\Dash_InfectoCast'
template_path = os.path.join(dash_dir, 'template.html')

# 2. Update template.html getMatriculasAuditoriaData()
with open(template_path, 'r', encoding='utf-8') as f:
    t_code = f.read()

old_func_pattern = r'function getMatriculasAuditoriaData\(\) \{[\s\S]*?return \{\s*count24h: list24h\.length,\s*count30d: list30d\.length,\s*list24h,\s*list30d,\s*allRecords: allMatriculas\s*\};\s*\}'

new_func_code = '''function getMatriculasAuditoriaData() {
    const rawStudents = (DATA && DATA.students) ? DATA.students : [];
    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
    const telemetria = (DATA && DATA.telemetria_sync) ? DATA.telemetria_sync : [];
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
    const allMatriculas = [];
    const processedPairs = new Set();

    validStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().trim();
        const cNorm = normalizeCourse(s.curso || '');
        const pairKey = em + '___' + cNorm;
        
        if (processedPairs.has(pairKey)) return;
        processedPairs.add(pairKey);
        
        // REGRA DE OURO:
        // Se o aluno tem faturas pagas no gateway para este curso, o marco da matricula e a DATA DO PRIMEIRO PAGAMENTO PAGO.
        // Se nao tem pagamento no gateway (acesso direto/plataforma), o marco e a data de inscricao na plataforma.
        
        let effDate = null;
        let origem = '';
        let valor = 0;
        let tipo = '';
        
        const paidBillsCourse = studentCoursePaidBills.get(em + '___' + cNorm) || studentCoursePaidBills.get(nm.toLowerCase() + '___' + cNorm);
        const paidBillsGlobal = studentCoursePaidBills.get(em + '___GLOBAL') || studentCoursePaidBills.get(nm.toLowerCase() + '___GLOBAL');
        
        const targetBills = paidBillsCourse || paidBillsGlobal;
        
        if (targetBills && targetBills.length > 0) {
            targetBills.sort((a, b) => a.date - b.date);
            const firstPaid = targetBills[0];
            effDate = firstPaid.date;
            origem = 'Primeiro Pagamento (' + firstPaid.gateway + ')';
            valor = firstPaid.valor;
            tipo = 'gateway';
        } else {
            const dtInsc = parseDateUniversal(s.data_insc || s.data_inscricao || s.data_matricula || s.first);
            if (dtInsc) {
                effDate = dtInsc;
                origem = 'Cadastro Plataforma (' + (s.plataforma || 'Academy') + ')';
                tipo = 'plataforma';
            }
        }
        
        if (effDate && effDate <= now) {
            const is24h = effDate >= t24h;
            const is30d = effDate >= t30d;
            
            const pad = n => n < 10 ? '0' + n : n;
            const dtFmt = pad(effDate.getDate()) + '/' + pad(effDate.getMonth()+1) + '/' + effDate.getFullYear() + ' ' + pad(effDate.getHours()) + ':' + pad(effDate.getMinutes());
            
            allMatriculas.push({
                nome: nm || 'Aluno',
                email: em,
                curso: s.curso || 'PLATAFORMA GERAL',
                data: effDate,
                data_fmt: dtFmt,
                origem: origem,
                tipo: tipo,
                valor: valor,
                is_24h: is24h,
                is_30d: is30d
            });
        }
    });

    allMatriculas.sort((a, b) => b.data - a.data);

    const list24h = allMatriculas.filter(m => m.is_24h);
    const list30d = allMatriculas.filter(m => m.is_30d);

    return {
        count24h: list24h.length,
        count30d: list30d.length,
        list24h,
        list30d,
        allRecords: allMatriculas
    };
}'''

t_code, count_t = re.subn(old_func_pattern, lambda m: new_func_code, t_code)
print(f"[template.html] Replaced getMatriculasAuditoriaData: {count_t} matches")
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(t_code)

print("Patching complete!")

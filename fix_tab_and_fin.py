import re

template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# -------------------------------------------------------------
# 1. Null-safety in initFilters
# -------------------------------------------------------------
old_init_filters = """function initFilters() {
    const cursos = new Set();
    const alunos = new Set();
    DATA.students.forEach(s => {
        if(s.curso && s.curso !== 'Sem Curso') Object.keys(DATA.curriculum).forEach(c => cursos.add(c));
        alunos.add(s.nome + " (" + s.email + ")");
    });
    
    const selCurso = $('#filter-curso');
    const sortedCourses = Object.keys(DATA.curriculum).sort((a, b) => {
        const aPos = a.startsWith('POS') || a.startsWith('PÓS');
        const bPos = b.startsWith('POS') || b.startsWith('PÓS');
        if (aPos && !bPos) return -1;
        if (!aPos && bPos) return 1;
        return a.localeCompare(b);
    });
    selCurso.innerHTML = '<option value="all">Todos os Cursos</option>' + sortedCourses.map(c => `<option value="${c}">${c}</option>`).join('');
    
    const selAluno = $('#filter-aluno');
    selAluno.innerHTML = '<option value="all">Todos os Alunos</option>' + Array.from(alunos).map(a => `<option value="${a}">${a}</option>`).join('');
    
    selCurso.onchange = e => { FILTER.curso = e.target.value; applyFilters(); };
    selAluno.onchange = e => { FILTER.aluno = e.target.value; applyFilters(); };
    $('#filter-date-start').onchange = e => { FILTER.start = e.target.value; applyFilters(); };
    $('#filter-date-end').onchange = e => { FILTER.end = e.target.value; applyFilters(); };
}"""

new_init_filters = """function initFilters() {
    const cursos = new Set();
    const alunos = new Set();
    const stList = (DATA && DATA.students) ? DATA.students : [];
    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};

    stList.forEach(s => {
        if(s.curso && s.curso !== 'Sem Curso' && curric) Object.keys(curric).forEach(c => cursos.add(c));
        if(s.nome || s.email) alunos.add((s.nome || 'Aluno') + " (" + (s.email || '') + ")");
    });
    
    const selCurso = $('#filter-curso');
    const sortedCourses = Object.keys(curric).sort((a, b) => {
        const aPos = a.startsWith('POS') || a.startsWith('PÓS');
        const bPos = b.startsWith('POS') || b.startsWith('PÓS');
        if (aPos && !bPos) return -1;
        if (!aPos && bPos) return 1;
        return a.localeCompare(b);
    });
    if (selCurso) selCurso.innerHTML = '<option value="all">Todos os Cursos</option>' + sortedCourses.map(c => `<option value="${c}">${c}</option>`).join('');
    
    const selAluno = $('#filter-aluno');
    if (selAluno) selAluno.innerHTML = '<option value="all">Todos os Alunos</option>' + Array.from(alunos).map(a => `<option value="${a}">${a}</option>`).join('');
    
    if (selCurso) selCurso.onchange = e => { FILTER.curso = e.target.value; applyFilters(); };
    if (selAluno) selAluno.onchange = e => { FILTER.aluno = e.target.value; applyFilters(); };
    if ($('#filter-date-start')) $('#filter-date-start').onchange = e => { FILTER.start = e.target.value; applyFilters(); };
    if ($('#filter-date-end')) $('#filter-date-end').onchange = e => { FILTER.end = e.target.value; applyFilters(); };
}"""

if old_init_filters in text:
    text = text.replace(old_init_filters, new_init_filters)
    print("1. initFilters updated")
else:
    print("1. old_init_filters not found directly, using regex")
    text = re.sub(r'function initFilters\(\)\s*\{[\s\S]*?#filter-date-end[\s\S]*?\}', new_init_filters, text, count=1)
    print("1. initFilters regex replaced")

# -------------------------------------------------------------
# 2. Centralized Tab Switching at line ~2100
# -------------------------------------------------------------
p_tabs_1 = re.compile(
    r"function switchTab\(pId\)\s*\{[\s\S]*?\$\$'\.tab'\.forEach\(t=>t\.onclick=e=>\{[\s\S]*?if\(\$\('\.filters'\)\) \$\('\.filters'\)\.style\.display = 'flex';\s*\}\s*\}\);"
)

r_tabs_1 = """function selectTab(pId) {
    if (!pId) return;
    $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.p === pId));
    $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));

    if (pId === 'home') drawHome(true);
    if (pId === 'prog') renderRows();
    if (pId === 'tl') drawTimeline(true);
    if (pId === 'mod') renderModules();
    if (pId === 'origem') drawOrigem(true);
    if (pId === 'fin') drawFinanceiro(true);
    if (pId === 'funil') {
        drawFunil(true);
        if ($('.filters')) $('.filters').style.display = 'none';
    } else {
        if ($('.filters')) $('.filters').style.display = 'flex';
    }
}
window.selectTab = selectTab;
window.switchTab = selectTab;

// TABS LISTENERS
$$('.tab').forEach(t => {
    t.onclick = e => {
        e.preventDefault();
        selectTab(t.dataset.p);
    };
});"""

text, n_tabs = p_tabs_1.subn(r_tabs_1, text)
print(f"2. Primary tab listener replaced: {n_tabs}")

# -------------------------------------------------------------
# 3. Remove duplicate tab listener at line ~3940
# -------------------------------------------------------------
p_tabs_2 = re.compile(
    r"// INIT\s*\$\$'\.tab'\.forEach\(b => \{[\s\S]*?if \(\$\('\.filters'\)\) \$\('\.filters'\)\.style\.display = 'flex';\s*\}\s*\}\s*\};\s*\}\);"
)

r_tabs_2 = """// INIT - Tabs já vinculadas via selectTab()"""

text, n_tabs2 = p_tabs_2.subn(r_tabs_2, text)
print(f"3. Duplicate tab listener removed: {n_tabs2}")

# -------------------------------------------------------------
# 4. Enhance _getFinData with robust faturas extraction
# -------------------------------------------------------------
p_get_fin = re.compile(
    r"function _getFinData\(src\)\s*\{[\s\S]*?return \{\s*fonte: 'Consolidado \(Vindi & Asaas\)',[\s\S]*?faturas_tabela: faturas_tabela\s*\};\s*\}"
)

r_get_fin = """function _getFinData(src) {
    const vindi = (DATA.financeiro && DATA.financeiro.kpis) ? DATA.financeiro : null;
    const asaas = (DATA.financeiro_asaas && DATA.financeiro_asaas.kpis) ? DATA.financeiro_asaas : null;

    // Extrair faturas dos alunos caso não estejam na raiz
    function getFaturasFromStudents(gw) {
        const list = [];
        (DATA.students || []).forEach(s => {
            const gData = gw === 'Vindi' ? s.vindi : s.asaas;
            if (gData && gData.faturas) {
                gData.faturas.forEach(f => {
                    list.push({
                        ...f,
                        aluno: f.aluno || s.nome || s.email,
                        email: f.email || s.email,
                        plano: f.plano || gData.plano || '',
                        gateway: gw
                    });
                });
            }
        });
        return list;
    }

    let vfaturas = (vindi && vindi.faturas_tabela && vindi.faturas_tabela.length)
        ? vindi.faturas_tabela.map(f => ({...f, gateway: 'Vindi'}))
        : getFaturasFromStudents('Vindi');

    let afaturas = (asaas && asaas.faturas_tabela && asaas.faturas_tabela.length)
        ? asaas.faturas_tabela.map(f => ({...f, gateway: 'Asaas'}))
        : getFaturasFromStudents('Asaas');

    if (src === 'vindi') {
        if (!vindi) return null;
        return { ...vindi, faturas_tabela: vfaturas };
    }
    if (src === 'asaas') {
        if (!asaas) return null;
        return { ...asaas, faturas_tabela: afaturas };
    }

    // CONSOLIDADO (src === 'all')
    if (!vindi && !asaas) return null;
    if (!vindi) return { ...asaas, faturas_tabela: afaturas };
    if (!asaas) return { ...vindi, faturas_tabela: vfaturas };

    const vk = vindi.kpis || {};
    const ak = asaas.kpis || {};

    const totRec = (vk.total_recebido || 0) + (ak.total_recebido || 0);
    const recMes = (vk.recebido_mes_atual || 0) + (ak.recebido_mes_atual || 0);
    const totAtraso = (vk.total_em_atraso || 0) + (ak.total_em_atraso || 0);
    const qtdAtraso = (vk.qtd_em_atraso || 0) + (ak.qtd_em_atraso || 0);
    const mrr = (vk.mrr_ativo || 0) + (ak.mrr_ativo || 0);
    const proj30 = (vk.projecao_30d || 0) + (ak.projecao_30d || 0);
    const fatPagas = (vk.total_faturas_pagas || 0) + (ak.total_faturas_pagas || 0);
    const baseAdimp = totRec + totAtraso;
    const taxaAdimp = baseAdimp > 0 ? Math.round((totRec / baseAdimp) * 100) : 100;

    // Mesclar histórico mensal
    const histMap = {};
    (vindi.historico_mensal || []).forEach(h => {
        if (!histMap[h.mes]) histMap[h.mes] = { mes: h.mes, label: h.label, pago: 0 };
        histMap[h.mes].pago += (h.pago || 0);
    });
    (asaas.historico_mensal || []).forEach(h => {
        if (!histMap[h.mes]) histMap[h.mes] = { mes: h.mes, label: h.label, pago: 0 };
        histMap[h.mes].pago += (h.pago || 0);
    });
    const historico_mensal = Object.values(histMap).sort((a,b) => a.mes.localeCompare(b.mes));

    // Mesclar projeção mensal
    const projMap = {};
    (vindi.projecao_mensal || []).forEach(p => {
        if (!projMap[p.mes]) projMap[p.mes] = { mes: p.mes, label: p.label, previsto: 0 };
        projMap[p.mes].previsto += (p.previsto || 0);
    });
    (asaas.projecao_mensal || []).forEach(p => {
        if (!projMap[p.mes]) projMap[p.mes] = { mes: p.mes, label: p.label, previsto: 0 };
        projMap[p.mes].previsto += (p.previsto || 0);
    });
    const projecao_mensal = Object.values(projMap).sort((a,b) => a.mes.localeCompare(b.mes));

    // Mesclar todas as faturas
    const faturas_tabela = [...vfaturas, ...afaturas].sort((a,b) => {
        const da = a.vencimento_iso || a.data_pagamento_iso || '';
        const db = b.vencimento_iso || b.data_pagamento_iso || '';
        return db.localeCompare(da);
    });

    return {
        fonte: 'Consolidado (Vindi & Asaas)',
        kpis: {
            total_recebido: totRec,
            recebido_mes_atual: recMes,
            total_em_atraso: totAtraso,
            qtd_em_atraso: qtdAtraso,
            mrr_ativo: mrr,
            projecao_30d: proj30,
            total_faturas_pagas: fatPagas,
            taxa_adimplencia: taxaAdimp
        },
        historico_mensal: historico_mensal,
        projecao_mensal: projecao_mensal,
        faturas_tabela: faturas_tabela
    };
}"""

text, n_fin = p_get_fin.subn(r_get_fin, text)
print(f"4. _getFinData replaced: {n_fin}")

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Template patch completed!")

import re

template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# ==============================================================================
# 1. Update HTML of the Faturas Card
# ==============================================================================
old_faturas_head = """    <!-- 3. TABELA GERAL DE FATURAS E COBRAN?AS -->
    <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px">
        <div>
          <h3 id="fin-table-title" style="font-size:15px; font-weight:800; color:var(--ink); margin:0 0 4px">Todas as Faturas e Cobran?as (Consolidado)</h3>
          <div style="font-size:11.5px; color:var(--muted)">Consulte pagamentos efetuados, cobran?as pendentes e acione contatos via WhatsApp.</div>
        </div>
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap">
          <input type="text" id="fin-search-input" oninput="renderFinTable()" placeholder="Buscar por aluno, email ou plano..." style="padding:6px 12px; border:1px solid var(--line2); border-radius:8px; font-size:12px; width:260px; outline:none; background:var(--bg); color:var(--text)">
          <div id="fin-filter-chips" style="display:flex; gap:6px"></div>
        </div>
      </div>

      <div style="overflow-x:auto">
        <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left">
          <thead>
            <tr style="border-bottom:2px solid var(--line2); color:var(--muted); font-size:11px; text-transform:uppercase">
              <th style="padding:10px 8px">Fatura</th>
              <th style="padding:10px 8px">Gateway</th>
              <th style="padding:10px 8px">Aluno</th>
              <th style="padding:10px 8px">Plano / Curso</th>
              <th style="padding:10px 8px">Vencimento</th>
              <th style="padding:10px 8px">Pagamento</th>
              <th style="padding:10px 8px">Valor</th>
              <th style="padding:10px 8px">Forma</th>
              <th style="padding:10px 8px">Status</th>
              <th style="padding:10px 8px; text-align:right">A?es</th>
            </tr>
          </thead>
          <tbody id="fin-table-tbody"></tbody>
        </table>
      </div>"""

# Let's search with regex to handle encoding characters in Portuguese
p_card_head = re.compile(
    r'<!-- 3\. TABELA GERAL DE FATURAS E COBRAN[^\n]*-->\s*<div style="background:var\(--card\); border:1px solid var\(--line\); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba\(0,0,0,0\.03\)">[\s\S]*?<tbody id="fin-table-tbody"></tbody>\s*</table>\s*</div>'
)

new_faturas_card_html = """    <!-- 3. TABELA GERAL DE FATURAS E COBRANÇAS -->
    <div id="fin-faturas-card" style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba(0,0,0,0.03); scroll-margin-top:20px">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px">
        <div>
          <div style="display:flex; align-items:center; gap:8px">
            <h3 id="fin-table-title" style="font-size:15px; font-weight:800; color:var(--ink); margin:0">Todas as Faturas e Cobranças (Consolidado)</h3>
            <span id="fin-table-kpi-badge" style="display:none; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px"></span>
          </div>
          <div id="fin-table-desc" style="font-size:11.5px; color:var(--muted); margin-top:3px">Consulte pagamentos efetuados, cobranças pendentes e acione contatos via WhatsApp.</div>
        </div>
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap">
          <!-- Toggle Visão por Aluno vs Visão por Fatura -->
          <div style="display:flex; background:var(--bg); border:1px solid var(--line2); border-radius:8px; padding:2px">
            <button id="btn-fin-view-aluno" onclick="_finSetViewMode('aluno')" style="border:none; background:transparent; padding:5px 10px; border-radius:6px; font-size:11.5px; font-weight:700; cursor:pointer; color:var(--muted); transition:all .15s">👤 Visão por Aluno</button>
            <button id="btn-fin-view-fatura" onclick="_finSetViewMode('fatura')" style="border:none; background:var(--paper); color:var(--ink); padding:5px 10px; border-radius:6px; font-size:11.5px; font-weight:700; cursor:pointer; box-shadow:0 1px 4px rgba(0,0,0,0.06); transition:all .15s">📄 Visão por Fatura</button>
          </div>
          <input type="text" id="fin-search-input" oninput="renderFinTable()" placeholder="Buscar por aluno, email ou plano..." style="padding:6px 12px; border:1px solid var(--line2); border-radius:8px; font-size:12px; width:220px; outline:none; background:var(--bg); color:var(--text)">
          <div id="fin-filter-chips" style="display:flex; gap:6px"></div>
        </div>
      </div>

      <div style="overflow-x:auto">
        <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left">
          <thead id="fin-table-thead"></thead>
          <tbody id="fin-table-tbody"></tbody>
        </table>
      </div>"""

text, n_head = p_card_head.subn(lambda m: new_faturas_card_html, text)
print(f"1. Faturas card HTML replaced: {n_head}")


# ==============================================================================
# 2. Update Javascript: drawFinanceiro, KPI click, View Mode, and renderFinTable
# ==============================================================================
# Let's locate from `let _finDrawn = false;` down to `function renderFinTable() { ... }`

p_fin_js = re.compile(
    r"let _finDrawn = false;\s*let _finFilterStatus = 'all';\s*let _finSource = 'all';[\s\S]*?function renderFinTable\(\)\s*\{[\s\S]*?\}\.join\(''\);\s*\}"
)

new_fin_js = """let _finDrawn = false;
let _finFilterStatus = 'all';
let _finSource = 'all'; // 'all' | 'asaas' | 'vindi'
let _finSelectedMonth = null; // null or 'YYYY-MM'
let _finActiveKpi = null; // null | 'total_recebido' | 'recebido_mes' | 'em_atraso' | 'mrr' | 'projecao_30d' | 'adimplencia'
let _finTableViewMode = 'fatura'; // 'fatura' | 'aluno'
let _allFinFaturas = [];
let _finExpandedStudents = new Set(); // emails of expanded students in accordion

function _finSetSource(src) {
    _finSource = src;
    ['all', 'asaas', 'vindi'].forEach(s => {
        const el = $(`#fin-src-${s}`);
        if (el) {
            if (s === src) {
                el.style.background = 'var(--ink)';
                el.style.color = '#fff';
            } else {
                el.style.background = 'transparent';
                el.style.color = 'var(--muted)';
            }
        }
    });
    drawFinanceiro(true);
}

function _finSetFilter(status) {
    _finFilterStatus = status;
    // Se o usuário clicar no chip em_atraso, sincroniza com o KPI
    if (status === 'em_atraso') {
        _finActiveKpi = 'em_atraso';
        _finTableViewMode = 'aluno';
    } else if (status === 'paid') {
        _finActiveKpi = 'total_recebido';
    } else if (status === 'futuro') {
        _finActiveKpi = 'projecao_30d';
    } else {
        _finActiveKpi = null;
    }
    _updateFinChips();
    _updateFinViewButtons();
    _renderFinKpiCards();
    renderFinTable();
}

function _finSetViewMode(mode) {
    _finTableViewMode = mode;
    _updateFinViewButtons();
    renderFinTable();
}

function _updateFinViewButtons() {
    const btnA = $('#btn-fin-view-aluno');
    const btnF = $('#btn-fin-view-fatura');
    if (btnA && btnF) {
        if (_finTableViewMode === 'aluno') {
            btnA.style.background = 'var(--paper)';
            btnA.style.color = 'var(--ink)';
            btnA.style.boxShadow = '0 1px 4px rgba(0,0,0,0.06)';
            btnF.style.background = 'transparent';
            btnF.style.color = 'var(--muted)';
            btnF.style.boxShadow = 'none';
        } else {
            btnF.style.background = 'var(--paper)';
            btnF.style.color = 'var(--ink)';
            btnF.style.boxShadow = '0 1px 4px rgba(0,0,0,0.06)';
            btnA.style.background = 'transparent';
            btnA.style.color = 'var(--muted)';
            btnA.style.boxShadow = 'none';
        }
    }
}

function _updateFinChips() {
    const statusOpts = [
        { key: 'all', label: 'Todos' },
        { key: 'paid', label: '✅ Pago' },
        { key: 'em_atraso', label: '🔴 Em Atraso' },
        { key: 'futuro', label: '🔮 Futuro' },
        { key: 'a_vencer', label: '⏰ A Vencer' },
    ];
    const chips = $('#fin-filter-chips');
    if (chips) {
        chips.innerHTML = statusOpts.map(o =>
            `<button class="chip${_finFilterStatus === o.key ? ' on' : ''}" onclick="_finSetFilter('${o.key}')" style="font-size:11px; padding:5px 10px">${o.label}</button>`
        ).join('');
    }
}

function _finClickKpi(key) {
    if (_finActiveKpi === key) {
        // Toggle off
        _finActiveKpi = null;
        _finFilterStatus = 'all';
        _finSelectedMonth = null;
    } else {
        _finActiveKpi = key;
        if (key === 'em_atraso') {
            _finFilterStatus = 'em_atraso';
            _finTableViewMode = 'aluno'; // ativa automaticamente a visão por aluno!
        } else if (key === 'total_recebido') {
            _finFilterStatus = 'paid';
            _finSelectedMonth = null;
        } else if (key === 'recebido_mes') {
            _finFilterStatus = 'paid';
            const now = new Date();
            const ym = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');
            _finSelectedMonth = ym;
        } else if (key === 'projecao_30d') {
            _finFilterStatus = 'futuro';
        } else if (key === 'mrr') {
            _finFilterStatus = 'all';
            _finTableViewMode = 'aluno';
        } else if (key === 'adimplencia') {
            _finFilterStatus = 'all';
        }
    }

    _updateFinChips();
    _updateFinViewButtons();
    _renderFinKpiCards();
    renderFinTable();

    // Rola suavemente até o card de faturas
    const card = document.getElementById('fin-faturas-card');
    if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function _finToggleStudentDetails(email) {
    if (_finExpandedStudents.has(email)) {
        _finExpandedStudents.delete(email);
    } else {
        _finExpandedStudents.add(email);
    }
    renderFinTable();
}

function _getFinData(src) {
    const vindi = DATA.financeiro;
    const asaas = DATA.financeiro_asaas;

    const vfaturas = (vindi && vindi.faturas_tabela) ? vindi.faturas_tabela.map(f => ({ ...f, gateway: 'Vindi', _aluno: f.aluno, _email: f.email, _plano: f.plano })) : [];
    const afaturas = (asaas && asaas.faturas_tabela) ? asaas.faturas_tabela.map(f => ({ ...f, gateway: 'Asaas', _aluno: f.aluno, _email: f.email, _plano: f.plano })) : [];

    const activeCurso = (FILTER && FILTER.curso && FILTER.curso !== 'all') ? FILTER.curso : null;

    if (activeCurso) {
        function buildCourseSpecificFin(faturas, label) {
            const courseFaturas = faturas.filter(f => f.curso === activeCurso);
            
            let totRec = 0;
            let totAtraso = 0;
            let qtdAtraso = 0;
            let fatPagas = 0;
            let recMes = 0;
            const now = new Date();
            const currentYm = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');

            const histMap = {};
            const projMap = {};

            courseFaturas.forEach(f => {
                const val = Number(f.valor) || 0;
                const pIso = f.data_pagamento_iso || f.data_pagamento || '';
                const vIso = f.vencimento_iso || f.vencimento || '';
                
                if (f.status === 'paid' || f.status === 'pago') {
                    totRec += val;
                    fatPagas++;
                    const refYm = pIso.slice(0, 7) || vIso.slice(0, 7);
                    if (refYm) {
                        if (!histMap[refYm]) histMap[refYm] = { mes: refYm, label: refYm, pago: 0 };
                        histMap[refYm].pago += val;
                    }
                    if (refYm === currentYm) recMes += val;
                } else if (f.status === 'em_atraso') {
                    totAtraso += val;
                    qtdAtraso++;
                } else if (f.status === 'futuro' || f.status === 'a_vencer' || f.status === 'pending') {
                    const refYm = vIso.slice(0, 7);
                    if (refYm) {
                        if (!projMap[refYm]) projMap[refYm] = { mes: refYm, label: refYm, previsto: 0 };
                        projMap[refYm].previsto += val;
                    }
                }
            });

            const baseAdimp = totRec + totAtraso;
            const taxaAdimp = baseAdimp > 0 ? Math.round((totRec / baseAdimp) * 100) : 100;
            const historico_mensal = Object.values(histMap).sort((a,b) => a.mes.localeCompare(b.mes));
            const projecao_mensal = Object.values(projMap).sort((a,b) => a.mes.localeCompare(b.mes));
            const proj30 = projecao_mensal.length > 0 ? projecao_mensal[0].previsto : 0;
            const mrr = projecao_mensal.slice(0, 2).reduce((acc, p) => acc + p.previsto, 0) / Math.max(1, Math.min(2, projecao_mensal.length));

            return {
                fonte: `${label} · ${activeCurso}`,
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
                faturas_tabela: courseFaturas
            };
        }

        if (src === 'vindi') return buildCourseSpecificFin(vfaturas, 'Vindi');
        if (src === 'asaas') return buildCourseSpecificFin(afaturas, 'Asaas');
        return buildCourseSpecificFin([...vfaturas, ...afaturas], 'Consolidado');
    }

    // Sem filtro de curso: usa os totais consolidados completos
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
}

let _cachedFinObj = null;

function _renderFinKpiCards() {
    if (!_cachedFinObj) return;
    const fin = _cachedFinObj;
    const k = fin.kpis || {};
    const fmt = v => {
        if (typeof v === 'number') return 'R$ ' + v.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
        return v || '—';
    };
    const fmtN = v => typeof v === 'number' ? v.toLocaleString('pt-BR') : (v || '0');

    const kpiDefs = [
        { key: 'total_recebido', icon: '💰', label: 'Total Recebido', value: fmt(k.total_recebido), sub: `${fmtN(k.total_faturas_pagas)} faturas pagas`, color: 'var(--emerald)' },
        { key: 'recebido_mes', icon: '📅', label: 'Recebido Este Mês', value: fmt(k.recebido_mes_atual), sub: 'Mês corrente', color: 'var(--sky)' },
        { key: 'em_atraso', icon: '🔴', label: 'Em Atraso', value: fmt(k.total_em_atraso), sub: `${fmtN(k.qtd_em_atraso)} fatura(s) pendente(s) · Clique p/ ver por aluno`, color: k.total_em_atraso > 0 ? 'var(--coral)' : 'var(--emerald)' },
        { key: 'mrr', icon: '🔁', label: 'MRR Ativo', value: fmt(k.mrr_ativo), sub: 'Receita recorrente mensal', color: '#7c3aed' },
        { key: 'projecao_30d', icon: '🔮', label: 'Projeção 30d', value: fmt(k.projecao_30d), sub: 'Próximas cobranças estimadas', color: 'var(--amber)' },
        { key: 'adimplencia', icon: '📊', label: 'Adimplência', value: (k.taxa_adimplencia || 0) + '%', sub: 'Faturas pagas / total faturado', color: (k.taxa_adimplencia || 0) >= 80 ? 'var(--emerald)' : 'var(--coral)' },
    ];

    const grid = $('#fin-kpis-grid');
    if (grid) {
        grid.innerHTML = kpiDefs.map(d => {
            const isAct = _finActiveKpi === d.key;
            const borderStyle = isAct ? `2px solid ${d.color}` : '1px solid var(--line)';
            const bgStyle = isAct ? 'background:rgba(255,255,255,0.95); box-shadow:0 4px 16px rgba(0,0,0,0.08); transform:scale(1.02)' : 'background:var(--card); box-shadow:0 2px 8px rgba(0,0,0,0.03)';
            const activeBadge = isAct ? `<span style="font-size:9.5px; font-weight:800; padding:1px 6px; border-radius:10px; background:${d.color}; color:#fff; margin-left:auto">● Ativo</span>` : '';
            return `
            <div onclick="_finClickKpi('${d.key}')" style="${bgStyle}; border:${borderStyle}; border-radius:12px; padding:16px 18px; cursor:pointer; transition:all .2s; position:relative" title="Clique para filtrar as faturas">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px">
                    <span style="font-size:18px">${d.icon}</span>
                    <span style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:var(--muted)">${d.label}</span>
                    ${activeBadge}
                </div>
                <div style="font-family:var(--disp); font-size:24px; font-weight:700; color:${d.color}; line-height:1.1; letter-spacing:-.02em">${d.value}</div>
                <div style="font-size:11px; color:var(--muted2); margin-top:4px">${d.sub}</div>
            </div>`;
        }).join('');
    }
}

function drawFinanceiro(force) {
    if (_finDrawn && !force) return;
    _finDrawn = true;

    const activeCurso = (FILTER && FILTER.curso && FILTER.curso !== 'all') ? FILTER.curso : null;
    const badgeFiltro = $('#fin-curso-filtro-badge');
    if (badgeFiltro) {
        if (activeCurso) {
            badgeFiltro.style.display = 'inline-block';
            badgeFiltro.textContent = `Curso ativo: ${activeCurso}`;
        } else {
            badgeFiltro.style.display = 'none';
        }
    }

    const fin = _getFinData(_finSource);
    if (!fin) {
        $('#fin-kpis-grid').innerHTML = '<div style="padding:24px; color:var(--muted); font-size:13px; text-align:center">Dados financeiros não disponíveis para o filtro selecionado.</div>';
        return;
    }
    _cachedFinObj = fin;

    // Renderiza os cards de KPI clicáveis
    _renderFinKpiCards();

    // --- Gráfico de barras ---
    _drawFinChart(fin);

    // --- Tabela de Composição da Receita por Curso ---
    _renderFinCursosTable(fin);

    // --- Montar todas as faturas para a tabela global ---
    _allFinFaturas = (fin.faturas_tabela || []);

    _updateFinChips();
    _updateFinViewButtons();
    renderFinTable();
}

function renderFinTable() {
    const thead = $('#fin-table-thead');
    const tbody = $('#fin-table-tbody');
    const countEl = $('#fin-table-count');
    const kpiBadge = $('#fin-table-kpi-badge');
    if (!tbody) return;

    const searchTxt = ($('#fin-search-input') && $('#fin-search-input').value || '').toLowerCase().trim();

    let faturas = _allFinFaturas.filter(f => {
        // Filtro por mês clicado no gráfico
        if (_finSelectedMonth) {
            const pIso = f.data_pagamento_iso || f.data_pagamento || '';
            const vIso = f.vencimento_iso || f.vencimento || '';
            const refYm = (f.status === 'paid' || f.status === 'pago') ? (pIso.slice(0, 7) || vIso.slice(0, 7)) : vIso.slice(0, 7);
            if (refYm !== _finSelectedMonth) return false;
        }

        // Filtro por status
        if (_finFilterStatus !== 'all') {
            const st = f.status || '';
            if (_finFilterStatus === 'paid' && st !== 'paid' && st !== 'pago') return false;
            if (_finFilterStatus === 'em_atraso' && st !== 'em_atraso') return false;
            if (_finFilterStatus === 'futuro' && st !== 'futuro') return false;
            if (_finFilterStatus === 'a_vencer' && st !== 'a_vencer') return false;
        }
        // Filtro por busca
        if (searchTxt) {
            const aluno = (f._aluno || f.aluno || '').toLowerCase();
            const email = (f._email || f.email || '').toLowerCase();
            const plano = (f._plano || f.plano || '').toLowerCase();
            const curso = (f.curso || '').toLowerCase();
            if (!aluno.includes(searchTxt) && !email.includes(searchTxt) && !plano.includes(searchTxt) && !curso.includes(searchTxt)) return false;
        }
        return true;
    });

    // Badge do filtro de KPI ativo
    if (kpiBadge) {
        if (_finActiveKpi === 'em_atraso') {
            kpiBadge.style.display = 'inline-block';
            kpiBadge.style.background = 'rgba(225,29,72,0.1)';
            kpiBadge.style.color = '#e11d48';
            kpiBadge.style.border = '1px solid rgba(225,29,72,0.25)';
            kpiBadge.textContent = 'Filtro: Em Atraso';
        } else if (_finActiveKpi === 'total_recebido') {
            kpiBadge.style.display = 'inline-block';
            kpiBadge.style.background = 'rgba(5,150,105,0.1)';
            kpiBadge.style.color = '#059669';
            kpiBadge.style.border = '1px solid rgba(5,150,105,0.25)';
            kpiBadge.textContent = 'Filtro: Total Recebido';
        } else if (_finActiveKpi === 'recebido_mes') {
            kpiBadge.style.display = 'inline-block';
            kpiBadge.style.background = 'rgba(2,132,199,0.1)';
            kpiBadge.style.color = '#0284c7';
            kpiBadge.style.border = '1px solid rgba(2,132,199,0.25)';
            kpiBadge.textContent = 'Filtro: Recebido Este Mês';
        } else if (_finActiveKpi === 'projecao_30d') {
            kpiBadge.style.display = 'inline-block';
            kpiBadge.style.background = 'rgba(217,119,6,0.1)';
            kpiBadge.style.color = '#d97706';
            kpiBadge.style.border = '1px solid rgba(217,119,6,0.25)';
            kpiBadge.textContent = 'Filtro: Projeção 30d';
        } else {
            kpiBadge.style.display = 'none';
        }
    }

    if (countEl) {
        let msg = `Exibindo ${faturas.length} fatura(s)`;
        if (_finSelectedMonth) msg += ` · Mês: ${_finSelectedMonth}`;
        if (FILTER && FILTER.curso && FILTER.curso !== 'all') msg += ` · Curso: ${FILTER.curso}`;
        countEl.textContent = msg;
    }

    const fmtMoney = v => 'R$ ' + (Number(v)||0).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});

    // =========================================================================
    // MODO 1: VISÃO POR ALUNO
    // =========================================================================
    if (_finTableViewMode === 'aluno') {
        if (thead) {
            thead.innerHTML = `
              <tr style="border-bottom:2px solid var(--line2); color:var(--muted); font-size:11px; text-transform:uppercase">
                <th style="padding:10px 8px">Aluno</th>
                <th style="padding:10px 8px">Curso / Especialidade</th>
                <th style="padding:10px 8px; text-align:center">Gateway</th>
                <th style="padding:10px 8px; text-align:center">Faturas</th>
                <th style="padding:10px 8px">Total</th>
                <th style="padding:10px 8px">Situação</th>
                <th style="padding:10px 8px; text-align:right">Ações</th>
              </tr>`;
        }

        // Agrupar faturas por aluno (email ou nome)
        const byStudent = {};
        faturas.forEach(f => {
            const email = (f._email || f.email || '').toLowerCase().trim();
            const aluno = f._aluno || f.aluno || 'Aluno';
            const curso = f.curso || 'PLATAFORMA GERAL';
            const key = email || aluno;
            if (!byStudent[key]) {
                byStudent[key] = {
                    aluno: aluno,
                    email: email,
                    curso: curso,
                    gateway: f.gateway || (String(f.id||'').startsWith('pay_') ? 'Asaas' : 'Vindi'),
                    total: 0.0,
                    total_atraso: 0.0,
                    max_dias_atraso: 0,
                    has_atraso: false,
                    faturas: []
                };
            }
            const val = Number(f.valor) || 0;
            byStudent[key].total += val;
            byStudent[key].faturas.push(f);
            if (f.status === 'em_atraso') {
                byStudent[key].has_atraso = true;
                byStudent[key].total_atraso += val;
                byStudent[key].max_dias_atraso = Math.max(byStudent[key].max_dias_atraso, Number(f.dias_atraso) || 0);
            }
        });

        const studentsList = Object.values(byStudent);
        // Ordenar: quem tem mais atraso primeiro, depois por total
        studentsList.sort((a, b) => {
            if (b.total_atraso !== a.total_atraso) return b.total_atraso - a.total_atraso;
            return b.total - a.total;
        });

        if (countEl) {
            countEl.textContent = `Exibindo ${studentsList.length} aluno(s) (${faturas.length} faturas)`;
        }

        if (!studentsList.length) {
            tbody.innerHTML = `<tr><td colspan="7" style="padding:32px; text-align:center; color:var(--muted); font-size:13px">Nenhum aluno encontrado para os filtros selecionados.</td></tr>`;
            return;
        }

        tbody.innerHTML = studentsList.map(st => {
            const isExpanded = _finExpandedStudents.has(st.email);
            const gwBadge = st.gateway === 'Asaas'
                ? `<span style="background:rgba(2,132,199,0.1); color:#0284c7; font-weight:800; padding:2px 6px; border-radius:4px; font-size:10px; border:1px solid rgba(2,132,199,0.25)">Asaas</span>`
                : `<span style="background:rgba(124,58,237,0.1); color:#7c3aed; font-weight:800; padding:2px 6px; border-radius:4px; font-size:10px; border:1px solid rgba(124,58,237,0.25)">Vindi</span>`;

            let situacaoBadge = '';
            if (st.has_atraso) {
                situacaoBadge = `<span style="display:inline-flex; align-items:center; gap:4px; background:rgba(225,29,72,0.1); color:#e11d48; border-radius:6px; padding:2px 8px; font-size:11px; font-weight:700">
                    <span style="width:6px; height:6px; border-radius:50%; background:#e11d48"></span>${st.max_dias_atraso}d em atraso
                </span>`;
            } else {
                situacaoBadge = `<span style="display:inline-flex; align-items:center; gap:4px; background:rgba(5,150,105,0.1); color:#059669; border-radius:6px; padding:2px 8px; font-size:11px; font-weight:700">
                    <span style="width:6px; height:6px; border-radius:50%; background:#059669"></span>Em dia
                </span>`;
            }

            // WhatsApp link
            const studentObj = (CURRENT_DATA?.students || []).find(x => x.email && x.email.toLowerCase().trim() === st.email);
            const tel = studentObj && studentObj.telefone ? studentObj.telefone.replace(/\\D/g, '') : '';
            let waBtn = '';
            if (st.has_atraso) {
                const msg = encodeURIComponent(`Olá, ${st.aluno}! Aqui é da equipe da Pós-Graduação InfectoCast.\\n\\nConstatamos que sua mensalidade no valor de ${fmtMoney(st.total_atraso)} está pendente.\\n\\nCaso precise de ajuda para regularizar, entre em contato conosco por aqui. Um abraço!`);
                const waUrl = tel ? `https://wa.me/55${tel}?text=${msg}` : `https://wa.me/?text=${msg}`;
                waBtn = `<a href="${waUrl}" target="_blank" style="display:inline-flex; align-items:center; gap:4px; font-size:10.5px; color:#25D366; text-decoration:none; font-weight:700; padding:4px 8px; border:1px solid rgba(37,211,102,0.35); border-radius:6px; white-space:nowrap; margin-right:6px">💬 Cobrar WA</a>`;
            }

            const toggleBtn = `<button onclick="_finToggleStudentDetails('${st.email}')" style="border:1px solid var(--line2); background:var(--bg); color:var(--ink); padding:4px 8px; border-radius:6px; font-size:10.5px; font-weight:600; cursor:pointer">
                ${isExpanded ? '▲ Ocultar Faturas' : `▼ Ver ${st.faturas.length} Fatura(s)`}
            </button>`;

            let faturasDetailsRow = '';
            if (isExpanded) {
                faturasDetailsRow = `
                <tr style="background:var(--paper)">
                  <td colspan="7" style="padding:12px 16px">
                    <div style="font-size:11.5px; font-weight:700; color:var(--ink); margin-bottom:8px">Faturas de ${st.aluno}:</div>
                    <table style="width:100%; border-collapse:collapse; font-size:11.5px; background:var(--card); border:1px solid var(--line); border-radius:8px; overflow:hidden">
                      <thead>
                        <tr style="border-bottom:1px solid var(--line2); color:var(--muted); font-size:10.5px; text-transform:uppercase; background:var(--bg)">
                          <th style="padding:6px 8px">ID</th>
                          <th style="padding:6px 8px">Vencimento</th>
                          <th style="padding:6px 8px">Pagamento</th>
                          <th style="padding:6px 8px">Valor</th>
                          <th style="padding:6px 8px">Forma</th>
                          <th style="padding:6px 8px">Status</th>
                          <th style="padding:6px 8px; text-align:right">Link</th>
                        </tr>
                      </thead>
                      <tbody>
                        ${st.faturas.map(f => {
                            const fId = String(f.id || '').replace('proj-', '🔮 Proj.').slice(0, 10);
                            const stFmt = (f.status === 'paid' || f.status === 'pago')
                                ? '<span style="color:#059669; font-weight:700">✅ Pago</span>'
                                : (f.status === 'em_atraso' ? '<span style="color:#e11d48; font-weight:700">🔴 Em Atraso</span>' : `<span style="color:#2563eb">${f.status}</span>`);
                            const linkFatura = f.url ? `<a href="${f.url}" target="_blank" style="font-size:10.5px; color:var(--sky); text-decoration:none; font-weight:600; padding:2px 6px; border:1px solid rgba(62,124,177,0.3); border-radius:4px">🔗 Abrir</a>` : '—';
                            return `
                            <tr style="border-bottom:1px solid var(--line2)">
                              <td style="padding:6px 8px; font-family:monospace">${fId}</td>
                              <td style="padding:6px 8px">${f.vencimento || '—'}</td>
                              <td style="padding:6px 8px; color:var(--muted)">${f.data_pagamento || '—'}</td>
                              <td style="padding:6px 8px; font-weight:700">${fmtMoney(f.valor)}</td>
                              <td style="padding:6px 8px; color:var(--muted)">${f.forma_pagamento || '—'}</td>
                              <td style="padding:6px 8px">${stFmt}</td>
                              <td style="padding:6px 8px; text-align:right">${linkFatura}</td>
                            </tr>`;
                        }).join('')}
                      </tbody>
                    </table>
                  </td>
                </tr>`;
            }

            return `
            <tr style="border-bottom:1px solid var(--line2); transition:background .15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
              <td style="padding:10px 8px; max-width:180px">
                <div style="font-weight:700; font-size:12px; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${st.aluno}">${st.aluno}</div>
                <div style="font-size:10px; color:var(--muted)">${st.email}</div>
              </td>
              <td style="padding:10px 8px; font-size:11.5px; color:var(--muted); max-width:180px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${st.curso}">${st.curso}</td>
              <td style="padding:10px 8px; text-align:center">${gwBadge}</td>
              <td style="padding:10px 8px; text-align:center; font-weight:700; color:var(--ink)">${st.faturas.length}</td>
              <td style="padding:10px 8px; font-weight:800; font-size:12.5px; color:${st.has_atraso ? '#e11d48' : '#059669'}">${fmtMoney(st.has_atraso ? st.total_atraso : st.total)}</td>
              <td style="padding:10px 8px">${situacaoBadge}</td>
              <td style="padding:10px 8px; text-align:right; white-space:nowrap">
                ${waBtn}
                ${toggleBtn}
              </td>
            </tr>
            ${faturasDetailsRow}`;
        }).join('');
        return;
    }

    // =========================================================================
    // MODO 2: VISÃO POR FATURA (LISTA INDIVIDUAL)
    // =========================================================================
    if (thead) {
        thead.innerHTML = `
          <tr style="border-bottom:2px solid var(--line2); color:var(--muted); font-size:11px; text-transform:uppercase">
            <th style="padding:10px 8px">Fatura</th>
            <th style="padding:10px 8px">Gateway</th>
            <th style="padding:10px 8px">Aluno</th>
            <th style="padding:10px 8px">Plano / Curso</th>
            <th style="padding:10px 8px">Vencimento</th>
            <th style="padding:10px 8px">Pagamento</th>
            <th style="padding:10px 8px">Valor</th>
            <th style="padding:10px 8px">Forma</th>
            <th style="padding:10px 8px">Status</th>
            <th style="padding:10px 8px; text-align:right">Ações</th>
          </tr>`;
    }

    if (!faturas.length) {
        tbody.innerHTML = `<tr><td colspan="10" style="padding:32px; text-align:center; color:var(--muted); font-size:13px">Nenhuma fatura encontrada para os filtros selecionados.</td></tr>`;
        return;
    }

    const stConfig = {
        'paid':     { label: 'Pago',          color: '#059669', bg: 'rgba(5,150,105,0.1)' },
        'pago':     { label: 'Pago',          color: '#059669', bg: 'rgba(5,150,105,0.1)' },
        'em_atraso':{ label: 'Em Atraso',     color: '#e11d48', bg: 'rgba(225,29,72,0.1)' },
        'a_vencer': { label: 'A Vencer',      color: '#d97706', bg: 'rgba(217,119,6,0.1)' },
        'futuro':   { label: 'Futuro',        color: '#3B82F6', bg: 'rgba(59,130,246,0.1)' },
        'canceled': { label: 'Cancelado',     color: 'var(--muted)', bg: 'rgba(0,0,0,0.05)' },
        'pending':  { label: 'Pendente',      color: '#d97706', bg: 'rgba(217,119,6,0.1)' },
    };

    tbody.innerHTML = faturas.slice(0, 300).map(f => {
        const st = f.status || '';
        const cfg = stConfig[st] || { label: st || '?', color: 'var(--muted)', bg: 'rgba(0,0,0,0.04)' };
        const aluno = f.aluno || f._aluno || '—';
        const email = f.email || f._email || '';
        const plano = f.plano || f._plano || '—';
        const venc = f.vencimento || '—';
        const pgto = f.data_pagamento || '';
        const valor = f.valor_fmt || (f.valor ? fmtMoney(f.valor) : '—');
        const forma = f.forma_pagamento || '—';
        const url = f.url || '';
        const faturaId = String(f.id || '').replace('proj-', '🔮 Proj.').slice(0, 10);

        let acoes = '';
        if (url && !String(f.id).startsWith('proj-')) {
            acoes += `<a href="${url}" target="_blank" style="display:inline-flex; align-items:center; gap:4px; font-size:10.5px; color:var(--sky); text-decoration:none; font-weight:600; padding:3px 8px; border:1px solid rgba(62,124,177,0.3); border-radius:6px; white-space:nowrap; margin-right:4px">🔗 Abrir Fatura</a>`;
        }
        if (st === 'em_atraso' && email) {
            const s = (CURRENT_DATA?.students||[]).find(x=>x.email===email);
            const tel = s && s.telefone ? s.telefone.replace(/\\D/g,'') : '';
            const msg = encodeURIComponent(`Olá! Aqui é da equipe da Pós-Graduação InfectoCast.\\n\\nSua mensalidade de ${venc} no valor de ${valor} está pendente.\\n\\nCaso precise de ajuda para regularizar, entre em contato conosco. Um abraço!`);
            const waUrl = tel ? `https://wa.me/55${tel}?text=${msg}` : `https://wa.me/?text=${msg}`;
            acoes += `<a href="${waUrl}" target="_blank" style="display:inline-flex; align-items:center; gap:4px; font-size:10.5px; color:#25D366; text-decoration:none; font-weight:600; padding:3px 8px; border:1px solid rgba(37,211,102,0.3); border-radius:6px; white-space:nowrap">💬 WA</a>`;
        }

        const gwName = f.gateway || (String(f.id||'').startsWith('pay_') ? 'Asaas' : 'Vindi');
        const gwBadge = gwName === 'Asaas'
            ? `<span style="background:rgba(2,132,199,0.1); color:#0284c7; font-weight:800; padding:2px 6px; border-radius:4px; font-size:10px; border:1px solid rgba(2,132,199,0.25)">Asaas</span>`
            : `<span style="background:rgba(124,58,237,0.1); color:#7c3aed; font-weight:800; padding:2px 6px; border-radius:4px; font-size:10px; border:1px solid rgba(124,58,237,0.25)">Vindi</span>`;

        return `<tr style="border-bottom:1px solid var(--line2); transition:background .15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
            <td style="padding:8px; font-family:monospace; font-size:11px">${faturaId || '—'}</td>
            <td style="padding:8px">${gwBadge}</td>
            <td style="padding:8px; max-width:160px">
                <div style="font-weight:600; font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${aluno}">${aluno}</div>
                <div style="font-size:10px; color:var(--muted2)">${email}</div>
            </td>
            <td style="padding:8px; font-size:11px; color:var(--muted); max-width:120px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${plano}">${plano}</td>
            <td style="padding:8px; font-size:12px; white-space:nowrap">${venc}</td>
            <td style="padding:8px; font-size:12px; color:var(--muted2); white-space:nowrap">${pgto || '—'}</td>
            <td style="padding:8px; font-weight:700; font-size:12px; white-space:nowrap">${valor}</td>
            <td style="padding:8px; font-size:11px; color:var(--muted)">${forma}</td>
            <td style="padding:8px">
                <span style="display:inline-flex; align-items:center; gap:4px; background:${cfg.bg}; color:${cfg.color}; border-radius:6px; padding:2px 8px; font-size:10.5px; font-weight:700; white-space:nowrap">
                    <span style="width:6px; height:6px; border-radius:50%; background:${cfg.color}; flex:none"></span>${cfg.label}
                </span>
            </td>
            <td style="padding:8px; text-align:right; white-space:nowrap">${acoes || '—'}</td>
        </tr>`;
    }).join('');
}"""

text, n_js = p_fin_js.subn(lambda m: new_fin_js, text)
print(f"2. Financeiro Javascript replaced: {n_js}")

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved template.html successfully!")

with open('C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Locate where the finance block starts (before _getFinData or right before renderFinTable)
idx_render_table = text.find('function renderFinTable()')
assert idx_render_table != -1, "renderFinTable not found!"

# Find start of finance section before renderFinTable
idx_start = text.find('// ============================================================')
# Look for the one before renderFinTable
matches = []
pos = 0
while True:
    p = text.find('// ============================================================', pos)
    if p == -1 or p > idx_render_table:
        break
    matches.append(p)
    pos = p + 1

if matches:
    replace_start = matches[-1]
else:
    replace_start = text.rfind('function _resolveFinCourse', 0, idx_render_table)
    if replace_start == -1:
        replace_start = text.rfind('function _getFinData', 0, idx_render_table)

fin_complete_block = """// ============================================================
// ABA FINANCEIRO — drawFinanceiro() + renderFinTable()
// ============================================================

let _finDrawn = false;
let _finFilterStatus = 'all';
let _finSource = 'all'; // 'all' | 'asaas' | 'vindi'
let _finSelectedMonth = null; // null or 'YYYY-MM'
let _finActiveKpi = null; // null | 'total_recebido' | 'recebido_mes' | 'em_atraso' | 'mrr' | 'projecao_30d' | 'adimplencia'
let _finTableViewMode = 'aluno'; // 'aluno' | 'fatura'
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
        _finActiveKpi = null;
        _finFilterStatus = 'all';
        _finSelectedMonth = null;
    } else {
        _finActiveKpi = key;
        if (key === 'em_atraso') {
            _finFilterStatus = 'em_atraso';
            _finTableViewMode = 'aluno';
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

function _finToggleMonthFilter(mes) {
    if (_finSelectedMonth === mes) {
        _finSelectedMonth = null;
    } else {
        _finSelectedMonth = mes;
    }
    drawFinanceiro(true);
}

function _resolveFinCourse(f) {
    if (!f) return 'PLATAFORMA GERAL';
    if (f.curso && f.curso !== 'PLATAFORMA GERAL' && f.curso !== 'None' && f.curso !== 'SEM CURSO' && !f.curso.startsWith('Fatura Avulsa')) {
        return resolveCanonicalCourse(f.curso);
    }

    const plano = (f.plano || f._plano || f.description || f.descricao || '').toString();
    const textFull = plano.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    if (textFull.includes('ortop') || textFull.includes('partes moles') || textFull.includes('pele') || textFull.includes('musculo')) {
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES';
    }
    if (textFull.includes('imuno') || textFull.includes('inuno') || textFull.includes('transplante')) {
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
    }
    if (textFull.includes('ccih') || textFull.includes('hospitalar') || textFull.includes('prevencao') || textFull.includes('vigilancia')) {
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
    }
    if (textFull.includes('pediat') || textFull.includes('crianca') || textFull.includes('neonat')) {
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
    }
    if (textFull.includes('multi-r') || textFull.includes('multir') || textFull.includes('jornada')) {
        return 'JORNADA MULTI-R';
    }
    if (textFull.includes('fungo') || textFull.includes('antifungico')) {
        return 'DO FUNGO AO ANTIFUNGICO';
    }
    if (textFull.includes('antibiotico') || textFull.includes('s.o.s') || textFull.includes('sos')) {
        return 'S.O.S ANTIBIOTICO';
    }

    const email = (f.email || f._email || '').toString().toLowerCase().trim();
    const aluno = (f.aluno || f._aluno || '').toString().toLowerCase().trim();
    const stList = (CURRENT_DATA && CURRENT_DATA.students) ? CURRENT_DATA.students : (DATA && DATA.students ? DATA.students : []);
    let stMatch = null;
    if (email) {
        stMatch = stList.find(s => s.email && s.email.toLowerCase().trim() === email && s.curso !== 'PLATAFORMA GERAL');
    }
    if (stMatch && stMatch.curso && stMatch.curso !== 'PLATAFORMA GERAL') {
        return resolveCanonicalCourse(stMatch.curso);
    }

    return 'PLATAFORMA GERAL';
}

function _getFinData(src) {
    const finUnified = computeUnifiedFinancialDataset(src);
    const activeCurso = (FILTER && FILTER.curso && FILTER.curso !== 'all') ? resolveCanonicalCourse(FILTER.curso) : null;

    if (activeCurso) {
        const cData = finUnified.courses[activeCurso] || {
            curso: activeCurso,
            fonte: `${src === 'vindi' ? 'Vindi' : (src === 'asaas' ? 'Asaas' : 'Consolidado')} · ${activeCurso}`,
            kpis: { total_recebido: 0, recebido_mes_atual: 0, a_vencer_mes_atual: 0, previsto_mes_vigente: 0, mrr_ativo: 0, projecao_30d: 0, total_em_atraso: 0, qtd_em_atraso: 0, total_faturas_pagas: 0, taxa_adimplencia: 100 },
            historico_mensal: [],
            projecao_mensal: [],
            faturas_tabela: []
        };
        return {
            ...cData,
            fonte: `${src === 'vindi' ? 'Vindi' : (src === 'asaas' ? 'Asaas' : 'Consolidado')} · ${activeCurso}`,
            faturas_tabela: cData.faturas_tabela || []
        };
    }

    return finUnified.global;
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
            return `
            <div class="kpi-card" onclick="_finClickKpi('${d.key}')" style="${bgStyle}; border:${borderStyle}; border-radius:12px; padding:16px 18px; cursor:pointer; transition:all .2s ease; position:relative">
                <div style="display:flex; justify-content:space-between; align-items:flex-start">
                    <span style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">${d.label}</span>
                    <span style="font-size:18px">${d.icon}</span>
                </div>
                <div style="font-size:20px; font-weight:800; color:var(--ink); margin:8px 0 4px">${d.value}</div>
                <div style="font-size:11px; color:var(--muted2)">${d.sub}</div>
                ${isAct ? `<div style="position:absolute; bottom:6px; right:10px; font-size:9.5px; font-weight:700; color:${d.color}">● Filtro Ativo</div>` : ''}
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

    _renderFinKpiCards();
    _drawFinChart(fin);
    _renderFinCursosTable(fin);

    _allFinFaturas = (fin.faturas_tabela || []);

    _updateFinChips();
    _updateFinViewButtons();
    renderFinTable();
}

function _drawFinChart(fin) {
    const container = $('#fin-chart-container');
    if (!container) return;

    const historico = fin.historico_mensal || [];
    const projecao = fin.projecao_mensal || [];

    const allMeses = new Set([...historico.map(h => h.mes), ...projecao.map(p => p.mes)]);
    const sortedMeses = [...allMeses].sort();

    if (!sortedMeses.length) {
        container.innerHTML = '<div style="padding:40px; text-align:center; color:var(--muted)">Sem dados de histórico disponíveis para o filtro selecionado.</div>';
        return;
    }

    const labelsMap = {};
    [...historico, ...projecao].forEach(x => { if (x.mes && x.label) labelsMap[x.mes] = x.label; });

    const histMap = {};
    historico.forEach(h => { histMap[h.mes] = h.pago || 0; });
    const projMap = {};
    projecao.forEach(p => { projMap[p.mes] = p.previsto || 0; });

    const labels = sortedMeses.map(m => labelsMap[m] || m);
    const histVals = sortedMeses.map(m => histMap[m] || 0);
    const projVals = sortedMeses.map(m => projMap[m] || 0);

    const maxVal = Math.max(...histVals, ...projVals, 1);
    const W = container.clientWidth || 800;
    const H = 250;
    const padL = 70, padR = 20, padT = 20, padB = 36;
    const barW = Math.max(8, Math.floor((W - padL - padR) / sortedMeses.length - 6));
    const grpW = barW * 2 + 4;
    const step = (W - padL - padR) / sortedMeses.length;

    const yTicks = 5;
    let ticks = [];
    for (let i = 0; i <= yTicks; i++) ticks.push(Math.round(maxVal * i / yTicks));

    const yScale = v => H - padB - (v / maxVal) * (H - padT - padB);
    const xPos = i => padL + i * step + step / 2;

    const today = new Date().toISOString().slice(0, 7);

    let svg = `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">`;

    ticks.forEach(t => {
        const y = yScale(t);
        const label = t >= 1000 ? `R$${(t/1000).toFixed(0)}k` : `R$${t}`;
        svg += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="var(--line)" stroke-width="1" stroke-dasharray="4,4"/>`;
        svg += `<text x="${padL - 5}" y="${y + 4}" text-anchor="end" font-size="9" fill="var(--muted2)">${label}</text>`;
    });

    sortedMeses.forEach((mes, i) => {
        const cx = xPos(i);
        const hv = histVals[i];
        const pv = projVals[i];
        const isCurrent = (mes === today);
        const isFuture = (mes > today);
        const isSelected = (mes === _finSelectedMonth);
        const hasBoth = (hv > 0 && pv > 0 && (isCurrent || isFuture));

        if (isSelected) {
            svg += `<rect x="${cx - step/2 + 1}" y="${padT}" width="${step - 2}" height="${H - padT - padB + 2}" rx="6" fill="rgba(18,161,122,0.12)" stroke="var(--emerald)" stroke-width="1.5" stroke-dasharray="3,3"/>`;
        }

        if (hv > 0) {
            const bh = Math.max(2, (hv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            const bx = hasBoth ? (cx - grpW / 2) : (cx - barW / 2);
            svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradGreen)" opacity="${isFuture ? 0.4 : 1}" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
                <title>${labelsMap[mes]} - Realizado: R$ ${hv.toLocaleString('pt-BR', {minimumFractionDigits:2})} (Clique para filtrar)</title>
            </rect>`;
        }

        if (pv > 0 && (isCurrent || isFuture)) {
            const bh = Math.max(2, (pv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            const bx = hasBoth ? (cx + 2) : (cx - barW / 2);
            svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradBlue)" opacity="${isCurrent ? 0.95 : 0.75}" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
                <title>${labelsMap[mes]} - Projeção: R$ ${pv.toLocaleString('pt-BR', {minimumFractionDigits:2})} (Clique para filtrar)</title>
            </rect>`;
        }

        svg += `<rect x="${cx - step/2}" y="${padT}" width="${step}" height="${H - padT - padB}" fill="transparent" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
            <title>${labelsMap[mes]}: Clique para filtrar composição por este mês</title>
        </rect>`;

        const labelColor = isSelected ? '#047857' : (isCurrent ? 'var(--emerald)' : 'var(--muted)');
        const labelWeight = (isSelected || isCurrent) ? '800' : '500';
        svg += `<text x="${cx}" y="${H - 4}" text-anchor="middle" font-size="9" fill="${labelColor}" font-weight="${labelWeight}" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">${labelsMap[mes] || mes}</text>`;
    });

    svg += `<defs>
        <linearGradient id="gradGreen" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#12A17A"/>
            <stop offset="100%" stop-color="#0C7D5E"/>
        </linearGradient>
        <linearGradient id="gradBlue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3B82F6"/>
            <stop offset="100%" stop-color="#1D4ED8"/>
        </linearGradient>
    </defs>`;

    svg += '</svg>';
    container.innerHTML = svg;
}

function _renderFinCursosTable(fin) {
    const tbody = $('#fin-cursos-tbody');
    const chipContainer = $('#fin-mes-chip-container');
    const chipTxt = $('#fin-mes-chip-txt');
    const subTxt = $('#fin-curso-sub');
    if (!tbody) return;

    const finUnified = computeUnifiedFinancialDataset(_finSource);
    const labelsMap = {};
    [...(fin.historico_mensal||[]), ...(fin.projecao_mensal||[])].forEach(x => { if (x.mes && x.label) labelsMap[x.mes] = x.label; });

    if (_finSelectedMonth) {
        if (chipContainer) chipContainer.style.display = 'inline-flex';
        if (chipTxt) chipTxt.textContent = labelsMap[_finSelectedMonth] || _finSelectedMonth;
        if (subTxt) subTxt.innerHTML = `Mostrando dados financeiros filtrados especificamente para o mês de <b style="color:var(--emerald-d)">${labelsMap[_finSelectedMonth] || _finSelectedMonth}</b>.`;
    } else {
        if (chipContainer) chipContainer.style.display = 'none';
        if (subTxt) subTxt.textContent = 'Distribuição de faturamento realizado, previsão futura e inadimplência por especialidade acadêmica.';
    }

    const rows = [];
    const coursesList = Object.values(finUnified.courses);

    coursesList.forEach(cm => {
        let pago = 0;
        let previsto = 0;
        let atraso = 0;
        let alunos = cm.alunos_vigentes;

        if (_finSelectedMonth) {
            pago = cm.historico_map[_finSelectedMonth] || 0;
            previsto = cm.projecao_map[_finSelectedMonth] || 0;
            atraso = cm.atraso_map[_finSelectedMonth] || 0;
        } else {
            pago = cm.pago_total;
            previsto = cm.proj_mes_atual;
            atraso = cm.atraso;
        }

        if (pago > 0 || previsto > 0 || atraso > 0 || alunos > 0) {
            rows.push({
                curso: cm.curso,
                alunos: alunos,
                pago: pago,
                previsto: previsto,
                atraso: atraso,
                volume: pago + previsto
            });
        }
    });

    const totalVolume = rows.reduce((acc, r) => acc + r.volume, 0);
    rows.sort((a, b) => b.volume - a.volume);

    const fmt = v => 'R$ ' + (Number(v)||0).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});

    if (!rows.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="padding:24px; text-align:center; color:var(--muted); font-size:12px">Nenhuma receita registrada para este filtro.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map((r, idx) => {
        const pct = totalVolume > 0 ? ((r.volume / totalVolume) * 100).toFixed(1) : '0.0';
        return `<tr style="border-bottom:1px solid var(--line2); transition:background .15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
            <td style="padding:10px 8px; font-weight:700; color:var(--ink)">
                <div style="display:flex; align-items:center; gap:6px">
                    <span style="font-size:11px; color:var(--muted); font-family:monospace">#${idx + 1}</span>
                    <span title="${r.curso}">${r.curso}</span>
                </div>
            </td>
            <td style="padding:10px 8px; text-align:center; font-weight:600; color:var(--muted)">${r.alunos}</td>
            <td style="padding:10px 8px; font-weight:700; color:#059669">${fmt(r.pago)}</td>
            <td style="padding:10px 8px; font-weight:600; color:#2563eb">${fmt(r.previsto)}</td>
            <td style="padding:10px 8px; font-weight:600; color:${r.atraso > 0 ? '#e11d48' : 'var(--muted)'}">${fmt(r.atraso)}</td>
            <td style="padding:10px 8px">
                <div style="display:flex; align-items:center; gap:8px">
                    <div style="flex:1; background:var(--line); height:7px; border-radius:4px; overflow:hidden">
                        <div style="width:${Math.min(100, Math.max(3, parseFloat(pct)))}%; background:linear-gradient(90deg, #12A17A, #3B82F6); height:100%; border-radius:4px"></div>
                    </div>
                    <span style="font-size:11px; font-weight:700; color:var(--ink); min-width:42px; text-align:right">${pct}%</span>
                </div>
            </td>
        </tr>`;
    }).join('');
}

"""

text = text[:replace_start] + fin_complete_block + text[idx_render_table:]

with open('C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('template.html finance block restored completely!')

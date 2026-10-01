// ORIGENS & ATRIBUIÇÃO DE MATRÍCULAS
let origemDrawn = false;
let origemCatFilter = 'all';
let origemSearchQuery = '';

function setOrigemCatFilter(cat) {
    origemCatFilter = cat;
    drawOrigem(true);
    drawFinanceiro(true);
}

function filterOrigemTable() {
    const q = (document.getElementById('origem-search-input')?.value || '').toLowerCase().trim();
    origemSearchQuery = q;
    let baseStudents = DATA.students.filter(s => {
        if (FILTER.curso !== 'all' && s.curso !== FILTER.curso) return false;
        return true;
    });
    const tbody = document.getElementById('origem-table-body');
    if (tbody) tbody.innerHTML = renderOrigemTableRows(baseStudents);
}

function getCategoryColor(cat) {
    if (cat.includes('E-book')) return { bg: 'rgba(56, 189, 248, 0.12)', color: '#0284c7', border: 'rgba(56, 189, 248, 0.3)' };
    if (cat.includes('Evento') || cat.includes('Live')) return { bg: 'rgba(168, 85, 247, 0.12)', color: '#7c3aed', border: 'rgba(168, 85, 247, 0.3)' };
    if (cat.includes('Fale Conosco') || cat.includes('Contato')) return { bg: 'rgba(16, 185, 129, 0.12)', color: '#059669', border: 'rgba(16, 185, 129, 0.3)' };
    if (cat.includes('Lista de Espera') || cat.includes('Grade')) return { bg: 'rgba(245, 158, 11, 0.12)', color: '#d97706', border: 'rgba(245, 158, 11, 0.3)' };
    if (cat.includes('Base') || cat.includes('Comunidade')) return { bg: 'rgba(236, 72, 153, 0.12)', color: '#db2777', border: 'rgba(236, 72, 153, 0.3)' };
    if (cat.includes('Checkout')) return { bg: 'rgba(100, 116, 139, 0.12)', color: '#475569', border: 'rgba(100, 116, 139, 0.3)' };
    return { bg: 'rgba(148, 163, 184, 0.12)', color: '#475569', border: 'rgba(148, 163, 184, 0.3)' };
}

function drawOrigem(force) {
    if (!DATA.students) return;
    if (origemDrawn && !force) return;
    origemDrawn = true;
    
    // 1. Filtrar alunos matriculados usando FILTER.curso
    let baseStudents = DATA.students.filter(s => {
        if (FILTER.curso !== 'all' && s.curso !== FILTER.curso) return false;
        return true;
    });
    
    // 2. Coletar dados
    let countComRD = 0;
    let countComConvAntes = 0;
    let totalPontosContato = 0;
    let maturacaoDiasList = [];
    let origensCount = {};
    let eventsCount = {};
    let eventsCatCount = {};
    
    baseStudents.forEach(s => {
        const rd = s.rd_funnel;
        if (rd) {
            countComRD++;
            const org = rd.origem && rd.origem !== '-' ? rd.origem : 'Desconhecido';
            origensCount[org] = (origensCount[org] || 0) + 1;
            
            const convAntes = rd.conversoes_antes !== undefined ? rd.conversoes_antes : (rd.eventos ? rd.eventos.length : 0);
            if (convAntes > 0) {
                countComConvAntes++;
                totalPontosContato += convAntes;
            }
            
            if (rd.dias_venda !== '' && rd.dias_venda !== null && !isNaN(rd.dias_venda)) {
                maturacaoDiasList.push(Number(rd.dias_venda));
            }
            
            const evs = rd.eventos_detalhados || [];
            const seenInStudent = new Set();
            evs.forEach(ev => {
                const name = ev.evento_clean || ev.evento_raw;
                const cat = ev.categoria || 'Outras Ações';
                if (!seenInStudent.has(name)) {
                    seenInStudent.add(name);
                    if (!eventsCount[name]) {
                        eventsCount[name] = { count: 0, cat: cat };
                    }
                    eventsCount[name].count++;
                    eventsCatCount[cat] = (eventsCatCount[cat] || 0) + 1;
                }
            });
        } else {
            origensCount['Não Rastreou no RD'] = (origensCount['Não Rastreou no RD'] || 0) + 1;
        }
    });
    
    const sortedMaturacao = [...maturacaoDiasList].sort((a,b)=>a-b);
    const mediaMaturacao = maturacaoDiasList.length > 0 
        ? Math.round(maturacaoDiasList.reduce((a,b)=>a+b, 0) / maturacaoDiasList.length) 
        : 0;
    const medianaMaturacao = sortedMaturacao.length > 0
        ? sortedMaturacao[Math.floor(sortedMaturacao.length / 2)]
        : 0;
    const mediaPontos = countComConvAntes > 0 
        ? (totalPontosContato / countComConvAntes).toFixed(1) 
        : '0.0';
    const pctRastreados = baseStudents.length > 0 
        ? ((countComRD / baseStudents.length) * 100).toFixed(0) 
        : 0;
    const pctComConv = baseStudents.length > 0 
        ? ((countComConvAntes / baseStudents.length) * 100).toFixed(0) 
        : 0;

    const container = document.getElementById('origem-metrics');
    if (!container) return;
    
    // Categorias disponíveis
    const catsAvailable = ['all', '📚 E-book / Material', '🎙️ Evento / Live', '💬 Fale Conosco / Contato', '👥 Comunidade / Base Prévia', '⏳ Lista de Espera / Grade', '💳 Checkout / Matrícula'];

    let html = `
    <!-- KPIS ATRIBUIÇÃO -->
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:14px; margin-bottom:20px">
      <div style="background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03)">
        <div style="font-size:11px; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Alunos no Filtro</div>
        <div style="font-size:26px; font-weight:800; color:var(--ink); margin-top:4px">${fmt(baseStudents.length)}</div>
        <div style="font-size:11px; color:var(--muted); margin-top:2px">Alunos matriculados</div>
      </div>
      <div style="background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03)">
        <div style="font-size:11px; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Rastreados na API RD</div>
        <div style="font-size:26px; font-weight:800; color:var(--sky); margin-top:4px">${fmt(countComRD)} <span style="font-size:14px; font-weight:600; color:var(--muted)">(${pctRastreados}%)</span></div>
        <div style="font-size:11px; color:var(--muted); margin-top:2px">Identificados na base oficial</div>
      </div>
      <div style="background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03)">
        <div style="font-size:11px; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Conversões Pré-Matrícula</div>
        <div style="font-size:26px; font-weight:800; color:var(--emerald); margin-top:4px">${fmt(totalPontosContato)} <span style="font-size:14px; font-weight:600; color:var(--muted)">(${pctComConv}% alunos)</span></div>
        <div style="font-size:11px; color:var(--muted); margin-top:2px">Média de <b>${mediaPontos}</b> eventos por aluno</div>
      </div>
      <div style="background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03)">
        <div style="font-size:11px; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Tempo de Maturação</div>
        <div style="font-size:26px; font-weight:800; color:var(--amber); margin-top:4px">${medianaMaturacao} <span style="font-size:14px; font-weight:600; color:var(--muted)">dias (mediana)</span></div>
        <div style="font-size:11px; color:var(--muted); margin-top:2px">Média: <b>${mediaMaturacao} dias</b> até matricular</div>
      </div>
    </div>

    <!-- GRID 2 COLUNAS -->
    <div style="display:grid; grid-template-columns: 1.15fr 0.85fr; gap:20px; margin-bottom:24px">
      
      <!-- COLUNA 1: TOP CONVERSÕES PRÉ-MATRÍCULA -->
      <div class="card" style="padding:18px; display:flex; flex-direction:column">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px">
          <div>
            <h3 style="margin:0; font-size:14px; font-weight:700; color:var(--ink)">Pontos de Contato & Conversões que Geraram Alunos</h3>
            <p style="font-size:11px; color:var(--muted); margin:4px 0 0">Eventos, e-books, lives e formulários acessados <b>antes</b> de matricular.</p>
          </div>
          <span style="background:rgba(0,180,216,0.12); color:#0077b6; font-size:10px; font-weight:700; padding:3px 8px; border-radius:12px; border:1px solid rgba(0,180,216,0.25)">API RD Station</span>
        </div>
        
        <!-- BOTOES DE FILTRO DE CATEGORIA -->
        <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:14px">
          <button onclick="setOrigemCatFilter('all')" style="padding:4px 10px; font-size:11px; font-weight:600; border-radius:16px; border:1px solid var(--line2); cursor:pointer; background:${origemCatFilter==='all'?'var(--ink)':'var(--bg)'}; color:${origemCatFilter==='all'?'#fff':'var(--text)'}">Todas Categorias</button>
          <button onclick="setOrigemCatFilter('Fale Conosco / Contato')" style="padding:4px 10px; font-size:11px; font-weight:600; border-radius:16px; border:1px solid var(--line2); cursor:pointer; background:${origemCatFilter==='Fale Conosco / Contato'?'#059669':'var(--bg)'}; color:${origemCatFilter==='Fale Conosco / Contato'?'#fff':'var(--text)'}">💬 Fale Conosco</button>
          <button onclick="setOrigemCatFilter('E-book / Material')" style="padding:4px 10px; font-size:11px; font-weight:600; border-radius:16px; border:1px solid var(--line2); cursor:pointer; background:${origemCatFilter==='E-book / Material'?'#0284c7':'var(--bg)'}; color:${origemCatFilter==='E-book / Material'?'#fff':'var(--text)'}">📚 E-books</button>
          <button onclick="setOrigemCatFilter('Evento / Live')" style="padding:4px 10px; font-size:11px; font-weight:600; border-radius:16px; border:1px solid var(--line2); cursor:pointer; background:${origemCatFilter==='Evento / Live'?'#7c3aed':'var(--bg)'}; color:${origemCatFilter==='Evento / Live'?'#fff':'var(--text)'}">🎙️ Eventos & Lives</button>
          <button onclick="setOrigemCatFilter('Comunidade / Base Prévia')" style="padding:4px 10px; font-size:11px; font-weight:600; border-radius:16px; border:1px solid var(--line2); cursor:pointer; background:${origemCatFilter==='Comunidade / Base Prévia'?'#db2777':'var(--bg)'}; color:${origemCatFilter==='Comunidade / Base Prévia'?'#fff':'var(--text)'}">👥 Comunidade</button>
          <button onclick="setOrigemCatFilter('Checkout / Matrícula')" style="padding:4px 10px; font-size:11px; font-weight:600; border-radius:16px; border:1px solid var(--line2); cursor:pointer; background:${origemCatFilter==='Checkout / Matrícula'?'#475569':'var(--bg)'}; color:${origemCatFilter==='Checkout / Matrícula'?'#fff':'var(--text)'}">💳 Checkout</button>
        </div>

        <div style="flex:1; display:flex; flex-direction:column; gap:10px" id="origem-events-list">
          ${renderOrigemEventsBars(eventsCount, baseStudents.length)}
        </div>
      </div>

      <!-- COLUNA 2: CANAIS DE ORIGEM / TRÁFEGO -->
      <div class="card" style="padding:18px; display:flex; flex-direction:column">
        <div style="margin-bottom:14px">
          <h3 style="margin:0; font-size:14px; font-weight:700; color:var(--ink)">Canais de Tráfego / Origem RD</h3>
          <p style="font-size:11px; color:var(--muted); margin:4px 0 0">Canal atribuído pelo RD Station na 1ª conversão.</p>
        </div>
        <div style="flex:1; display:flex; flex-direction:column; gap:10px">
          ${renderOrigemCanalBars(origensCount, baseStudents.length)}
        </div>
      </div>

    </div>

    <!-- SEÇÃO 3: TABELA DE ATRIBUIÇÃO POR ALUNO -->
    <div class="card" style="padding:18px">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px">
        <div>
          <h3 style="margin:0; font-size:14px; font-weight:700; color:var(--ink)">Jornada de Atribuição Individual dos Alunos</h3>
          <p style="font-size:11px; color:var(--muted); margin:4px 0 0">Veja as conversões de cada aluno, tempo de decisão e canal de aquisição.</p>
        </div>
        <div style="display:flex; align-items:center; gap:8px">
          <input type="text" id="origem-search-input" value="${origemSearchQuery}" placeholder="Buscar aluno, e-mail ou conversão..." 
            oninput="filterOrigemTable()" 
            style="padding:6px 12px; border:1px solid var(--line2); border-radius:6px; font-size:12px; width:260px; background:var(--bg); color:var(--text)">
          <button onclick="document.getElementById('origem-search-input').value=''; filterOrigemTable()" 
            style="padding:6px 10px; border:1px solid var(--line2); background:transparent; border-radius:6px; font-size:11px; cursor:pointer; color:var(--muted)">Limpar</button>
        </div>
      </div>
      
      <div style="overflow-x:auto">
        <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left">
          <thead>
            <tr style="border-bottom:1px solid var(--line2); color:var(--muted); font-size:11px; text-transform:uppercase">
              <th style="padding:10px 8px">Aluno</th>
              <th style="padding:10px 8px">Curso</th>
              <th style="padding:10px 8px">Inscrição</th>
              <th style="padding:10px 8px">1ª Conversão</th>
              <th style="padding:10px 8px">Pontos de Contato Pré-Matrícula</th>
              <th style="padding:10px 8px">Canal Origem</th>
              <th style="padding:10px 8px; text-align:center">Maturação</th>
              <th style="padding:10px 8px; text-align:center">Ação</th>
            </tr>
          </thead>
          <tbody id="origem-table-body">
            ${renderOrigemTableRows(baseStudents)}
          </tbody>
        </table>
      </div>
    </div>
    `;

    container.innerHTML = html;
}

function renderOrigemEventsBars(eventsCount, totalAlunos) {
    let filtered = Object.entries(eventsCount);
    if (origemCatFilter !== 'all') {
        filtered = filtered.filter(([name, data]) => data.cat === origemCatFilter);
    }
    filtered.sort((a,b) => b[1].count - a[1].count);
    
    if (filtered.length === 0) {
        return '<div style="padding:20px; text-align:center; color:var(--muted); font-size:12px">Nenhuma conversão encontrada para esta categoria.</div>';
    }
    
    const maxVal = filtered[0][1].count;
    
    return filtered.slice(0, 10).map(([name, data]) => {
        const count = data.count;
        const pct = (count / maxVal * 100).toFixed(0);
        const totalPct = totalAlunos > 0 ? (count / totalAlunos * 100).toFixed(1) : 0;
        const style = getCategoryColor(data.cat);
        
        return `
          <div style="display:flex; flex-direction:column; gap:4px; font-size:12px">
            <div style="display:flex; justify-content:space-between; align-items:center">
              <div style="display:flex; align-items:center; gap:6px; overflow:hidden">
                <span style="background:${style.bg}; color:${style.color}; border:1px solid ${style.border}; font-size:10px; font-weight:700; padding:1px 6px; border-radius:4px; white-space:nowrap">${data.cat}</span>
                <span style="font-weight:600; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${name}">${name}</span>
              </div>
              <div style="font-weight:700; color:var(--ink); font-size:12px; white-space:nowrap; margin-left:8px">
                ${count} alunos <span style="font-size:10px; font-weight:400; color:var(--muted)">(${totalPct}%)</span>
              </div>
            </div>
            <div style="background:var(--line); height:10px; border-radius:4px; overflow:hidden; position:relative">
              <div style="position:absolute; left:0; top:0; bottom:0; width:${pct}%; background:${style.color}; border-radius:4px; transition:width 0.5s"></div>
            </div>
          </div>
        `;
    }).join('');
}

function renderOrigemCanalBars(origensCount, totalAlunos) {
    const sorted = Object.entries(origensCount).sort((a,b) => b[1] - a[1]);
    if (sorted.length === 0) return '<div style="padding:20px; text-align:center; color:var(--muted)">Sem origens registradas.</div>';
    
    const maxVal = sorted[0][1];
    
    return sorted.map(([origem, val]) => {
        const pct = (val / maxVal * 100).toFixed(0);
        const totalPct = totalAlunos > 0 ? (val / totalAlunos * 100).toFixed(1) : 0;
        
        return `
          <div style="display:flex; flex-direction:column; gap:4px; font-size:12px">
            <div style="display:flex; justify-content:space-between; align-items:center">
              <span style="font-weight:500; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${origem}">${origem}</span>
              <span style="font-weight:700; color:var(--ink); font-size:12px; white-space:nowrap">
                ${val} alunos <span style="font-size:10px; font-weight:400; color:var(--muted)">(${totalPct}%)</span>
              </span>
            </div>
            <div style="background:var(--line); height:10px; border-radius:4px; overflow:hidden; position:relative">
              <div style="position:absolute; left:0; top:0; bottom:0; width:${pct}%; background:var(--sky); border-radius:4px; transition:width 0.5s"></div>
            </div>
          </div>
        `;
    }).join('');
}

function renderOrigemTableRows(baseStudents) {
    const q = origemSearchQuery.toLowerCase().trim();
    
    const filtered = baseStudents.filter(s => {
        if (!q) return true;
        const nome = (s.nome || '').toLowerCase();
        const email = (s.email || '').toLowerCase();
        const curso = (s.curso || '').toLowerCase();
        const org = (s.rd_funnel?.origem || '').toLowerCase();
        const evs = (s.rd_funnel?.eventos_detalhados || []).map(e => (e.evento_clean || '').toLowerCase()).join(' ');
        return nome.includes(q) || email.includes(q) || curso.includes(q) || org.includes(q) || evs.includes(q);
    });
    
    if (filtered.length === 0) {
        return '<tr><td colspan="8" style="padding:24px; text-align:center; color:var(--muted)">Nenhum aluno encontrado para a busca.</td></tr>';
    }
    
    return filtered.map(s => {
        const rd = s.rd_funnel;
        const org = rd ? (rd.origem && rd.origem !== '-' ? rd.origem : 'Desconhecido') : 'Não Rastreado';
        const pri = rd ? (rd.dt_primeira || '—') : '—';
        const dias = (rd && rd.dias_venda !== '' && rd.dias_venda !== null && rd.dias_venda !== undefined) ? `${rd.dias_venda} dias` : '—';
        const insc = s.data_insc || s.data_inscricao || s.inscricao || '—';
        
        // Renderizar badges dos primeiros 3 eventos
        const evs = rd?.eventos_detalhados || [];
        let evBadges = '';
        if (evs.length > 0) {
            evBadges = evs.slice(0, 3).map(e => {
                const style = getCategoryColor(e.categoria || '');
                return `<span style="display:inline-block; background:${style.bg}; color:${style.color}; border:1px solid ${style.border}; padding:2px 6px; border-radius:4px; font-size:10px; margin:2px 3px 2px 0" title="${e.data} - ${e.evento_clean}">${e.evento_clean}</span>`;
            }).join('');
            if (evs.length > 3) {
                evBadges += `<span style="color:var(--muted); font-size:10px; font-weight:600">+${evs.length - 3} mais</span>`;
            }
        } else {
            evBadges = '<span style="color:var(--muted); font-size:11px">Sem conversões prévias</span>';
        }
        
        return `
          <tr style="border-bottom:1px solid var(--line); transition:background 0.2s" onmouseover="this.style.background='rgba(0,0,0,0.02)'" onmouseout="this.style.background='transparent'">
            <td style="padding:10px 8px">
              <div style="font-weight:600; color:var(--ink)">${s.nome}${getPlatBadge(s.plataforma)}</div>
              <div style="font-size:10.5px; color:var(--muted)">${s.email}</div>
            </td>
            <td style="padding:10px 8px; font-weight:500; color:var(--ink)">${s.curso} ${getCursoBadge(s)}</td>
            <td style="padding:10px 8px; color:var(--text)">${insc}</td>
            <td style="padding:10px 8px; color:var(--text); font-size:11px">${pri}</td>
            <td style="padding:10px 8px; max-width:280px">${evBadges}</td>
            <td style="padding:10px 8px; color:var(--ink); font-size:11px">
              <span style="font-weight:500">${org}</span>
            </td>
            <td style="padding:10px 8px; text-align:center; font-weight:700; color:${dias!=='—'?'var(--amber)':'var(--muted)'}">${dias}</td>
            <td style="padding:10px 8px; text-align:center">
              <button onclick="openStudent('${s.email}')" style="background:var(--sky-w); color:var(--sky-d); border:none; border-radius:6px; padding:4px 8px; font-size:11px; font-weight:600; cursor:pointer">Ver Jornada ↗</button>
            </td>
          </tr>
        `;
    }).join('');
}


// ==================== VISÃO GERAL / HOME ====================
let homeDrawn = false;


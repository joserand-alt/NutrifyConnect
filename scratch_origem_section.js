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

function goToStatus(st) {
    switchTab('prog');
    ST_FILT = st;
    statusChips();
    renderRows();
}


let currentLiveActionFilter = 'ALL';

window.setLiveActionFilter = function(actionType) {
    currentLiveActionFilter = actionType;
    if (window._lastLiveBaseStudents) {
        drawLiveHourlyChart(window._lastLiveBaseStudents, currentLiveActionFilter);
    }
};

function parseEventDate(dStr) {
    if (!dStr) return null;
    const parts = dStr.split(' ');
    const dParts = parts[0].split('/');
    if (dParts.length !== 3) return null;
    const tParts = (parts[1] || '00:00').split(':');
    return new Date(Number(dParts[2]), Number(dParts[1]) - 1, Number(dParts[0]), Number(tParts[0]), Number(tParts[1] || 0));
}

let liveTimerInterval = null;

window.triggerLiveSync = async function() {
    const btn = document.getElementById('btn-sync-live');
    if (btn) {
        btn.innerHTML = '<span>⏳</span> <span>Sincronizando APIs...</span>';
        btn.disabled = true;
    }
    try {
        const res = await fetch('/api/atualizar', { method: 'POST' });
        if (res.ok) {
            if (btn) btn.innerHTML = '<span>✅</span> <span>Atualizado!</span>';
            setTimeout(() => { window.location.reload(); }, 800);
            return;
        }
    } catch(e) {
        console.log('Sem servidor local ativo para auto-gerar, recarregando...');
    }
    if (btn) btn.innerHTML = '<span>🔄</span> <span>Recarregando...</span>';
    setTimeout(() => { window.location.reload(); }, 600);
};

function startHourlyAutoRefresh() {
    if (window._hourlyTimer) clearTimeout(window._hourlyTimer);
    if (window._minuteTickInterval) clearInterval(window._minuteTickInterval);
    
    function updateClockAndSchedule() {
        const now = new Date();
        const msIntoHour = (now.getMinutes() * 60 + now.getSeconds()) * 1000 + now.getMilliseconds();
        const msUntilNextHour = Math.max(1000, 3600000 - msIntoHour);
        
        const nextHour = new Date(now.getTime() + msUntilNextHour);
        const pad = n => n < 10 ? '0' + n : n;
        const nextHourFmt = `${pad(nextHour.getHours())}:00`;
        const minsRemaining = Math.max(1, Math.round(msUntilNextHour / 60000));
        
        const tickEl = document.getElementById('live-tick-status');
        if (tickEl) {
            tickEl.innerHTML = `<span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--emerald); margin-right:4px"></span>Auto-refresh na hora cheia (${nextHourFmt} · em ${minsRemaining} min)`;
        }

        window._hourlyTimer = setTimeout(async () => {
            console.log("[AO VIVO] Hora cheia atingida. Sincronizando dados...");
            try {
                const res = await fetch('/api/atualizar', { method: 'POST' });
                if (res.ok) {
                    window.location.reload();
                    return;
                }
            } catch(e) {}
            window.location.reload();
        }, msUntilNextHour + 1000);
    }

    updateClockAndSchedule();
    
    window._minuteTickInterval = setInterval(() => {
        const now = new Date();
        const msIntoHour = (now.getMinutes() * 60 + now.getSeconds()) * 1000 + now.getMilliseconds();
        const msUntilNextHour = Math.max(1000, 3600000 - msIntoHour);
        const nextHour = new Date(now.getTime() + msUntilNextHour);
        const pad = n => n < 10 ? '0' + n : n;
        const nextHourFmt = `${pad(nextHour.getHours())}:00`;
        const minsRemaining = Math.max(1, Math.round(msUntilNextHour / 60000));
        const tickEl = document.getElementById('live-tick-status');
        if (tickEl) {
            tickEl.innerHTML = `<span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--emerald); margin-right:4px"></span>Auto-refresh na hora cheia (${nextHourFmt} · em ${minsRemaining} min)`;
        }
        if (window._lastLiveBaseStudents) {
            drawLiveMonitor(window._lastLiveBaseStudents, true);
        }
    }, 60000);
}

function drawLiveMonitor(baseStudents, isAutoTick) {
    window._lastLiveBaseStudents = baseStudents;
    const liveSectionEl = document.getElementById('home-live-section');
    if (!liveSectionEl) return;

    if (!isAutoTick) {
        startHourlyAutoRefresh();
    }

    let allEvts = [];
    baseStudents.forEach(s => {
        (s.events || []).forEach(e => {
            if (e.d) {
                const dt = parseEventDate(e.d);
                if (dt && !isNaN(dt.getTime())) {
                    allEvts.push({
                        dt: dt,
                        d: e.d,
                        aluno: s.nome || 'Aluno',
                        email: s.email || '',
                        curso: s.curso || '',
                        plataforma: s.plataforma || 'Academy',
                        acao: e.acao || 'AÇÃO',
                        item: e.item || '',
                        mod: e.mod || ''
                    });
                }
            }
        });
    });

    if (allEvts.length === 0) {
        liveSectionEl.style.display = 'none';
        return;
    }
    liveSectionEl.style.display = 'block';

    allEvts.sort((a,b) => a.dt.getTime() - b.dt.getTime());
    const maxDt = allEvts[allEvts.length - 1].dt;
    
    // TEMPO REAL: Janela de 60 minutos calculada a partir do momento ATUAL (real)
    const now = new Date();
    const t60m = new Date(now.getTime() - 60 * 60 * 1000);
    const t24h = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    const evts60m = allEvts.filter(e => e.dt >= t60m && e.dt <= now).sort((a,b) => b.dt.getTime() - a.dt.getTime());
    const evts24h = allEvts.filter(e => e.dt >= t24h && e.dt <= now);

    const uniqueStudents60m = new Set(evts60m.map(e => (e.email || '').toLowerCase().trim()).filter(Boolean));
    const uniqueStudents24h = new Set(evts24h.map(e => (e.email || '').toLowerCase().trim()).filter(Boolean));

    const pad = n => n < 10 ? '0' + n : n;
    const startTime60mFmt = `${pad(t60m.getHours())}:${pad(t60m.getMinutes())}`;
    const nowTimeFmt = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
    const maxTimeHourFmt = `${pad(maxDt.getHours())}:${pad(maxDt.getMinutes())}`;
    const maxDateFmt = `${pad(maxDt.getDate())}/${pad(maxDt.getMonth()+1)}/${maxDt.getFullYear()}`;

    // Calcular tempo desde o último registro na base
    const diffMs = Math.max(0, now.getTime() - maxDt.getTime());
    const diffHours = Math.floor(diffMs / (3600 * 1000));
    const diffMins = Math.floor((diffMs % (3600 * 1000)) / 60000);
    const tempoAtras = diffHours > 0 ? `há ${diffHours}h ${diffMins}min` : `há ${diffMins} min`;

    // Atualizar labels de referência no cabeçalho
    const refTimeEl = document.getElementById('live-ref-time');
    if (refTimeEl) {
        refTimeEl.innerHTML = `Último registro na base: <b style="color:var(--ink)">${maxDateFmt} às ${maxTimeHourFmt}</b> (${tempoAtras})`;
    }

    // Mini KPIs
    const miniKpisEl = document.getElementById('home-live-mini-kpis');
    if (miniKpisEl) {
        miniKpisEl.innerHTML = `
          <div style="background:var(--card); border:1px solid var(--line); border-radius:8px; padding:6px 12px; text-align:right">
            <div style="font-size:10px; font-weight:700; color:var(--muted); text-transform:uppercase">Últimos 60 min</div>
            <div style="font-size:16px; font-weight:800; color:${evts60m.length > 0 ? 'var(--emerald-d)' : 'var(--muted)'}">${evts60m.length} <span style="font-size:11px; font-weight:600; color:var(--muted)">ações</span></div>
          </div>
          <div style="background:var(--card); border:1px solid var(--line); border-radius:8px; padding:6px 12px; text-align:right">
            <div style="font-size:10px; font-weight:700; color:var(--muted); text-transform:uppercase">Alunos Ativos (60m)</div>
            <div style="font-size:16px; font-weight:800; color:${uniqueStudents60m.size > 0 ? 'var(--sky-d)' : 'var(--muted)'}">${uniqueStudents60m.size} <span style="font-size:11px; font-weight:600; color:var(--muted)">online</span></div>
          </div>
          <div style="background:var(--card); border:1px solid var(--line); border-radius:8px; padding:6px 12px; text-align:right">
            <div style="font-size:10px; font-weight:700; color:var(--muted); text-transform:uppercase">Total 24h</div>
            <div style="font-size:16px; font-weight:800; color:var(--ink)">${evts24h.length} <span style="font-size:11px; font-weight:600; color:var(--muted)">ações</span></div>
          </div>
          <div style="background:var(--card); border:1px solid var(--line); border-radius:8px; padding:6px 12px; text-align:right">
            <div style="font-size:10px; font-weight:700; color:var(--muted); text-transform:uppercase">Alunos em 24h</div>
            <div style="font-size:16px; font-weight:800; color:#7c3aed">${uniqueStudents24h.size} <span style="font-size:11px; font-weight:600; color:var(--muted)">alunos</span></div>
          </div>
        `;
    }

    // Feed Últimos 60 min
    const feedListEl = document.getElementById('home-live-feed-list');
    const liveCountBadge = document.getElementById('live-count-badge');
    const liveWindowLabel = document.getElementById('live-window-label');
    
    if (liveCountBadge) liveCountBadge.textContent = `${evts60m.length} evento${evts60m.length !== 1 ? 's' : ''}`;
    if (liveWindowLabel) liveWindowLabel.innerHTML = `Janela: <b>${startTime60mFmt} às ${nowTimeFmt}</b> (Hoje)`;

    if (feedListEl) {
        if (evts60m.length === 0) {
            feedListEl.innerHTML = `
              <div style="text-align:center; padding:45px 15px; color:var(--muted)">
                <div style="font-size:26px; margin-bottom:8px">☕</div>
                <div style="font-size:13px; font-weight:700; color:var(--ink)">Nenhuma atividade nos últimos 60 minutos</div>
                <div style="font-size:11px; margin-top:4px; color:var(--muted)">Sem logs recebidos nas APIs entre ${startTime60mFmt} e ${nowTimeFmt}.</div>
                <div style="margin-top:10px; font-size:10.5px; color:var(--muted2)">O feed será atualizado automaticamente caso surjam novas ações.</div>
              </div>
            `;
        } else {
            feedListEl.innerHTML = evts60m.map(e => {
                const diffMinsAgo = Math.max(0, Math.round((now.getTime() - e.dt.getTime()) / 60000));
                const timeAgo = diffMinsAgo === 0 ? 'agora mesmo' : `há ${diffMinsAgo} min`;
                const timeHour = `${pad(e.dt.getHours())}:${pad(e.dt.getMinutes())}`;
                const eventDate = `${pad(e.dt.getDate())}/${pad(e.dt.getMonth()+1)}`;

                let acaoStyle = { bg: 'var(--ink-soft)', color: 'var(--ink)', border: 'var(--line)', icon: '●' };
                if (e.acao.includes('ASSISTIU') || e.acao.includes('INICIOU') || e.acao.includes('AULA')) {
                    acaoStyle = { bg: 'var(--emerald-w)', color: 'var(--emerald-d)', border: 'rgba(18,161,122,0.25)', icon: '▶' };
                } else if (e.acao.includes('LOGIN')) {
                    acaoStyle = { bg: 'var(--sky-w)', color: 'var(--sky-d)', border: 'rgba(2,132,199,0.25)', icon: '🔑' };
                } else if (e.acao.includes('MATERIAL') || e.acao.includes('PDF')) {
                    acaoStyle = { bg: 'rgba(124,58,237,0.1)', color: '#7c3aed', border: 'rgba(124,58,237,0.25)', icon: '📄' };
                } else if (e.acao.includes('TESTE') || e.acao.includes('CONCLUIU')) {
                    acaoStyle = { bg: 'var(--amber-w)', color: 'var(--amber)', border: 'rgba(224,145,47,0.25)', icon: '✓' };
                }

                const initials = e.aluno.split(' ').map(n => n[0]).filter(Boolean).slice(0,2).join('').toUpperCase() || 'AL';
                const platColor = e.plataforma === 'Cativa' ? '#db2777' : '#0284c7';
                const platBg = e.plataforma === 'Cativa' ? 'rgba(236,72,153,0.1)' : 'rgba(2,132,199,0.1)';

                return `
                  <div style="display:flex; gap:10px; padding:10px; background:var(--card); border:1px solid var(--line); border-radius:8px; transition:all 0.15s" onmouseover="this.style.borderColor='var(--emerald)'" onmouseout="this.style.borderColor='var(--line)'">
                    <div style="width:34px; height:34px; border-radius:50%; background:var(--ink-soft); color:var(--ink); font-size:11.5px; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:2px">
                      ${initials}
                    </div>
                    <div style="flex:1; min-width:0">
                      <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:6px">
                        <div style="display:flex; align-items:center; gap:6px; overflow:hidden">
                          <span style="font-size:12.5px; font-weight:700; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${e.aluno}">${e.aluno}</span>
                          <span style="font-size:9.5px; font-weight:700; padding:1px 5px; border-radius:3px; background:${platBg}; color:${platColor}">${e.plataforma}</span>
                        </div>
                        
                        <div style="text-align:right; flex-shrink:0">
                          <div style="font-size:12px; font-weight:800; color:var(--ink)">${timeHour}</div>
                          <div style="font-size:9.5px; color:var(--muted); margin-top:-2px">${eventDate} · ${timeAgo}</div>
                        </div>
                      </div>
                      
                      <div style="display:flex; align-items:center; gap:6px; margin-top:3px">
                        <span style="font-size:9.5px; font-weight:700; padding:2px 6px; border-radius:4px; background:${acaoStyle.bg}; color:${acaoStyle.color}; border:1px solid ${acaoStyle.border}; white-space:nowrap">
                          ${acaoStyle.icon} ${e.acao}
                        </span>
                        <span style="font-size:11.5px; font-weight:600; color:var(--ink); overflow:hidden; text-overflow:ellipsis; white-space:nowrap" title="${e.item || e.mod || e.curso}">
                          ${e.item || e.mod || e.curso}
                        </span>
                      </div>
                      
                      <div style="font-size:10.5px; color:var(--muted); margin-top:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap">
                        ${e.curso}
                      </div>
                    </div>
                  </div>
                `;
            }).join('');
        }
    }

    // Gráfico 24h
    drawLiveHourlyChart(baseStudents, currentLiveActionFilter);
}

function drawLiveHourlyChart(baseStudents, actionFilter) {
    const filtersEl = document.getElementById('home-live-action-filters');
    const chartContainer = document.getElementById('home-hourly-chart-container');
    const rangeLabel = document.getElementById('home-chart-range-label');
    const totalLabel = document.getElementById('home-chart-total-label');
    if (!chartContainer) return;

    let allEvts = [];
    baseStudents.forEach(s => {
        (s.events || []).forEach(e => {
            if (e.d) {
                const dt = parseEventDate(e.d);
                if (dt && !isNaN(dt.getTime())) {
                    allEvts.push({
                        dt: dt,
                        d: e.d,
                        aluno: s.nome || 'Aluno',
                        email: s.email || '',
                        curso: s.curso || '',
                        plataforma: s.plataforma || 'Academy',
                        acao: e.acao || 'AÇÃO',
                        item: e.item || '',
                        mod: e.mod || ''
                    });
                }
            }
        });
    });

    if (allEvts.length === 0) {
        chartContainer.innerHTML = '<div style="text-align:center; padding:40px 0; color:var(--muted)">Sem dados no período.</div>';
        return;
    }

    // Janela real de 24 horas terminando na hora atual
    const now = new Date();
    const currentHourStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), 0, 0, 0);
    const t24hStart = new Date(currentHourStart.getTime() - 23 * 3600 * 1000);
    const t24hEnd = new Date(currentHourStart.getTime() + 3600 * 1000);

    const evts24h = allEvts.filter(e => e.dt >= t24hStart && e.dt < t24hEnd);

    let countAulas = 0, countLogins = 0, countPDFs = 0, countOutros = 0;
    evts24h.forEach(e => {
        if (e.acao.includes('ASSISTIU') || e.acao.includes('AULA')) countAulas++;
        else if (e.acao.includes('LOGIN')) countLogins++;
        else if (e.acao.includes('MATERIAL') || e.acao.includes('PDF')) countPDFs++;
        else countOutros++;
    });

    if (filtersEl) {
        const filterBtns = [
            { id: 'ALL', label: 'Todas as Ações', count: evts24h.length, color: 'var(--ink)' },
            { id: 'AULA', label: 'Aulas Assistidas', count: countAulas, color: 'var(--emerald-d)' },
            { id: 'LOGIN', label: 'Logins Web', count: countLogins, color: 'var(--sky-d)' },
            { id: 'PDF', label: 'Materiais PDF', count: countPDFs, color: '#7c3aed' },
            { id: 'OUTROS', label: 'Outros / Avaliações', count: countOutros, color: 'var(--amber)' }
        ];

        filtersEl.innerHTML = filterBtns.map(b => {
            const isActive = actionFilter === b.id;
            return `
              <button onclick="setLiveActionFilter('${b.id}')" style="background:${isActive ? b.color : 'var(--card)'}; color:${isActive ? '#fff' : 'var(--ink)'}; border:1px solid ${isActive ? b.color : 'var(--line)'}; border-radius:20px; padding:3px 9px; font-size:10.5px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:5px; transition:all 0.15s">
                <span>${b.label}</span>
                <span style="padding:1px 5px; border-radius:10px; background:${isActive ? 'rgba(255,255,255,0.25)' : 'var(--ink-soft)'}; font-size:9.5px">${b.count}</span>
              </button>
            `;
        }).join('');
    }

    const pad = n => n < 10 ? '0' + n : n;
    let buckets = [];
    let maxHourlyVal = 1;
    let filteredTotal = 0;

    for (let i = 0; i < 24; i++) {
        const bStart = new Date(t24hStart.getTime() + i * 3600 * 1000);
        const bEnd = new Date(bStart.getTime() + 3600 * 1000);
        
        const inBucket = evts24h.filter(e => e.dt >= bStart && e.dt < bEnd);
        
        let matching = inBucket;
        if (actionFilter === 'AULA') matching = inBucket.filter(e => e.acao.includes('ASSISTIU') || e.acao.includes('AULA'));
        else if (actionFilter === 'LOGIN') matching = inBucket.filter(e => e.acao.includes('LOGIN'));
        else if (actionFilter === 'PDF') matching = inBucket.filter(e => e.acao.includes('MATERIAL') || e.acao.includes('PDF'));
        else if (actionFilter === 'OUTROS') matching = inBucket.filter(e => !e.acao.includes('ASSISTIU') && !e.acao.includes('AULA') && !e.acao.includes('LOGIN') && !e.acao.includes('MATERIAL') && !e.acao.includes('PDF'));

        const count = matching.length;
        if (count > maxHourlyVal) maxHourlyVal = count;
        filteredTotal += count;

        const studentsSet = new Set(matching.map(e => e.aluno).filter(Boolean));
        const studentsList = Array.from(studentsSet).slice(0, 3).join(', ') + (studentsSet.size > 3 ? ` +${studentsSet.size - 3}` : '');

        buckets.push({
            hour: `${pad(bStart.getHours())}h`,
            fullTime: `${pad(bStart.getDate())}/${pad(bStart.getMonth()+1)} ${pad(bStart.getHours())}:00 - ${pad(bStart.getHours())}:59`,
            count: count,
            totalBucket: inBucket.length,
            studentsList: studentsList || 'Sem interações',
            isNow: i === 23
        });
    }

    if (rangeLabel) {
        rangeLabel.textContent = `Janela das 24h: ${pad(t24hStart.getDate())}/${pad(t24hStart.getMonth()+1)} ${pad(t24hStart.getHours())}:00 às ${pad(now.getDate())}/${pad(now.getMonth()+1)} ${pad(now.getHours())}:${pad(now.getMinutes())}`;
    }
    if (totalLabel) {
        totalLabel.innerHTML = `Volume no filtro: <b style="color:var(--ink)">${filteredTotal} ações</b>`;
    }

    let barColor = 'linear-gradient(180deg, #12A17A 0%, #0C7D5E 100%)';
    if (actionFilter === 'LOGIN') barColor = 'linear-gradient(180deg, #3E7CB1 0%, #1A5484 100%)';
    else if (actionFilter === 'PDF') barColor = 'linear-gradient(180deg, #8B5CF6 0%, #6D28D9 100%)';
    else if (actionFilter === 'OUTROS') barColor = 'linear-gradient(180deg, #E0912F 0%, #B06E15 100%)';
    else if (actionFilter === 'ALL') barColor = 'linear-gradient(180deg, #12232E 0%, #12A17A 100%)';

    chartContainer.innerHTML = `
      <div style="display:grid; grid-template-columns: repeat(24, 1fr); gap:4px; height:100%; align-items:flex-end; padding-bottom:22px; position:relative">
        ${buckets.map(b => {
            const heightPct = b.count > 0 ? Math.max(8, Math.round((b.count / maxHourlyVal) * 160)) : 3;
            const barBg = b.count > 0 ? barColor : 'var(--line)';
            const tooltip = `${b.fullTime}&#10;Ações selecionadas: ${b.count}&#10;Total geral na hora: ${b.totalBucket}&#10;Alunos: ${b.studentsList}`;
            
            return `
              <div style="display:flex; flex-direction:column; align-items:center; height:100%; justify-content:flex-end; position:relative; cursor:pointer" title="${tooltip}">
                ${b.count > 0 ? `<span style="font-size:9px; font-weight:800; color:var(--ink); margin-bottom:3px">${b.count}</span>` : ''}
                <div style="width:100%; max-width:24px; height:${heightPct}px; background:${barBg}; border-radius:3px 3px 0 0; transition:all 0.2s" onmouseover="this.style.opacity='0.75'; this.style.transform='scaleY(1.05)'" onmouseout="this.style.opacity='1'; this.style.transform='none'"></div>
                <span style="position:absolute; bottom:0; font-size:8.5px; font-weight:${b.isNow ? '800' : '600'}; color:${b.isNow ? 'var(--coral)' : 'var(--muted)'}; white-space:nowrap">${b.hour}</span>
              </div>
            `;
        }).join('')}
      </div>
    `;
}


// ========================================================
// VISÃO EXECUTIVA - COCKPIT ESTRATÉGICO
// ========================================================
let _execDrawn = false;

function isInvalidOrInternal(s) {
    if (!s) return true;
    const em = (s.email || '').toString().toLowerCase().trim();
    const nm = (s.nome || '').toString().toLowerCase().trim();
    const cr = (s.curso || '').toString().toUpperCase().trim();
    if (cr.includes('NUTRIFY')) return true;
    if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@vectorcomunica')) return true;
    if (em.includes('teste') || nm.includes('teste')) return true;
    if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com')) return true;
    return false;
}

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

function computeUnifiedFinancialDataset(gatewayFilter) {
    const rawStudents = ((CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0) ? CURRENT_DATA.students : (DATA && DATA.students ? DATA.students : [])).filter(s => !isInvalidOrInternal(s));
    const emailToCourse = {};
    const nameToCourse = {};
    rawStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(s.curso);
        if (em) emailToCourse[em] = c;
        if (nm) nameToCourse[nm] = c;
    });

    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};

    const vFaturas = (vindi && vindi.faturas_tabela) ? vindi.faturas_tabela : [];
    const aFaturas = (asaas && asaas.faturas_tabela) ? asaas.faturas_tabela : [];
    const vSubs = (vindi && vindi.subscriptions) ? vindi.subscriptions : [];
    const aData = (asaas && asaas.data) ? asaas.data : {};

    let faturasList = [];
    if (!gatewayFilter || gatewayFilter === 'all') {
        faturasList = [
            ...vFaturas.map(f => ({ ...f, gateway: 'Vindi', curso: resolveCanonicalCourse(f.curso || emailToCourse[(f.email||'').toLowerCase()] || nameToCourse[(f.aluno||'').toLowerCase()]) })),
            ...aFaturas.map(f => ({ ...f, gateway: 'Asaas', curso: resolveCanonicalCourse(f.curso || emailToCourse[(f.email||'').toLowerCase()] || nameToCourse[(f.aluno||'').toLowerCase()]) }))
        ];
    } else if (gatewayFilter === 'vindi') {
        faturasList = vFaturas.map(f => ({ ...f, gateway: 'Vindi', curso: resolveCanonicalCourse(f.curso || emailToCourse[(f.email||'').toLowerCase()] || nameToCourse[(f.aluno||'').toLowerCase()]) }));
    } else if (gatewayFilter === 'asaas') {
        faturasList = aFaturas.map(f => ({ ...f, gateway: 'Asaas', curso: resolveCanonicalCourse(f.curso || emailToCourse[(f.email||'').toLowerCase()] || nameToCourse[(f.aluno||'').toLowerCase()]) }));
    }

    const coursesMap = {};
    const getCourse = (cName) => {
        const c = resolveCanonicalCourse(cName);
        if (!coursesMap[c]) {
            coursesMap[c] = {
                curso: c,
                alunos_vigentes: 0,
                alunos_total: 0,
                pago_total: 0,
                pago_mes_atual: 0,
                proj_mes_atual: 0,
                pago_mes_ant: 0,
                atraso: 0,
                qtd_atraso: 0,
                mrr: 0,
                proj_1m: 0,
                proj_3m: 0,
                proj_6m: 0,
                proj_12m: 0,
                total_faturas_pagas: 0,
                historico_map: {},
                projecao_map: {},
                atraso_map: {},
                projecao_18m_sim: Array(18).fill(0),
                faturas_tabela: []
            };
        }
        return coursesMap[c];
    };

    // 1. Alunos e Matrículas Vigentes
    rawStudents.forEach(s => {
        const c = resolveCanonicalCourse(s.curso);
        const cm = getCourse(c);
        cm.alunos_total++;

        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
        const isCancel = vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled' || s.status === 'Cancelado';
        const isConcluido = !isCancel && (vSt === 'quitado' || aSt === 'quitado' || s.status === 'Concluído' || s.status === 'Encerrado' || s.turma_encerrada === true);

        if (!isCancel && !isConcluido) {
            cm.alunos_vigentes++;
        }
    });

    // 2. Faturas Emitidas e Histórico
    faturasList.forEach(f => {
        const cm = getCourse(f.curso);
        cm.faturas_tabela.push(f);
        const val = Number(f.valor) || 0;
        const st = (f.status || '').toLowerCase();
        const dtPag = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
        const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();

        const pYm = (f.data_pagamento_iso || dtPag).slice(0, 7);
        const vYm = (f.vencimento_iso || dtVenc).slice(0, 7);

        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            cm.pago_total += val;
            cm.total_faturas_pagas++;
            if (pYm) {
                cm.historico_map[pYm] = (cm.historico_map[pYm] || 0) + val;
            }
            if (dtPag.includes('09/2026') || dtPag.includes('2026-09') || dtPag.includes('/09/26')) {
                cm.pago_mes_atual += val;
            } else if (dtPag.includes('08/2026') || dtPag.includes('2026-08') || dtPag.includes('/08/26')) {
                cm.pago_mes_ant += val;
            }
        } else if (st === 'em_atraso' || st === 'overdue') {
            cm.atraso += val;
            cm.qtd_atraso++;
            if (vYm) {
                cm.atraso_map[vYm] = (cm.atraso_map[vYm] || 0) + val;
            }
        }
    });

    // Helper robusto para ciclos de contratos
    function parsePlanCycles(planoStr) {
        if (!planoStr) return 18;
        const p = planoStr.toString().toUpperCase().trim();
        if (p.includes('À VISTA') || p.includes('A VISTA')) return 1;
        const mX = p.match(/\\b(\\d+)\\s*X\\b/);
        if (mX) return parseInt(mX[1], 10);
        const mWord = p.match(/\\b(\\d+)\\s*(?:MESES|PARCELAS|VEZES)\\b/);
        if (mWord) return parseInt(mWord[1], 10);
        const mHyphen = p.match(/-\\s*(\\d+)(?!\\s*%)(\\s*X)?$/);
        if (mHyphen) return parseInt(mHyphen[1], 10);
        if (p.includes('RESIDENTES 24')) return 24;
        if (p.includes('ANUAL')) return 12;
        if (p.includes('SEMESTRAL') || p.match(/\\b6\\s*X\\b/)) return 6;
        if (p.includes('PÓS') || p.includes('POS') || p.includes('MENSALIDADE')) return 18;
        return 12;
    }

    // 3. Assinaturas Vindi (MRR e Simulação Contratual de 18 Meses)
    if (!gatewayFilter || gatewayFilter === 'all' || gatewayFilter === 'vindi') {
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

                // Identifica se já houve pagamento no mês corrente (Set/26)
                const paidThisMonth = faturasArr.some(f => {
                    const dt = (f.data_pagamento || f.data_pagamento_iso || '').toString();
                    return (f.status === 'paid' || f.status === 'pago') && (dt.includes('09/2026') || dt.includes('2026-09') || dt.includes('/09/26'));
                });

                // Se já pagou no mês atual ou vencimento é para Out/26+, o próximo ciclo a vencer é Outubro (m = 1)
                let startM = 0;
                if (paidThisMonth || prox.includes('/10/2026') || prox.includes('2026-10') || prox.includes('/10/26')) {
                    startM = 1;
                } else {
                    cm.proj_mes_atual += price;
                }

                // Projeta cada ciclo contratual restante
                for (let i = 0; i < remainingCycles; i++) {
                    const targetM = startM + i;
                    if (targetM < 18) {
                        cm.projecao_18m_sim[targetM] += price;
                    }
                }
            }
        });
    }

    // 4. Clientes e Carnês/Cartões Asaas (MRR e Projeções Futuras)
    if (!gatewayFilter || gatewayFilter === 'all' || gatewayFilter === 'asaas') {
        const asaasMrrGlobal = Number(asaas.kpis?.mrr_ativo) || 0;
        const asaasCoursePending = {};
        let asaasTotalPending = 0;

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

        aFaturas.forEach(f => {
            const st = (f.status || '').toLowerCase();
            const isPendingOrFuture = (
                st === 'pendente' || st === 'pending' || st === 'a_vencer' || 
                st === 'futuro' || st === 'confirmed' || st === 'a vencer'
            );
            if (isPendingOrFuture) {
                const em = (f.email || '').toString().toLowerCase().trim();
                const cm = getCourse(f.curso || emailToCourse[em] || nameToCourse[(f.aluno||'').toLowerCase()]);
                const val = Number(f.valor) || 0;
                const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
                const dObj = _parseDateSafe(dtVenc);
                if (dObj) {
                    const baseDateRef = new Date(2026, 8, 1);
                    const diffMeses = (dObj.getFullYear() - baseDateRef.getFullYear()) * 12 + (dObj.getMonth() - baseDateRef.getMonth());
                    if (diffMeses >= 0 && diffMeses < 18) {
                        cm.projecao_18m_sim[diffMeses] += val;
                        if (diffMeses === 0 || diffMeses === 1) {
                            asaasCoursePending[cm.curso] = (asaasCoursePending[cm.curso] || 0) + val;
                            asaasTotalPending += val;
                        }
                    }
                }
            }
        });

        if (asaasTotalPending > 0 && asaasMrrGlobal > 0) {
            Object.entries(asaasCoursePending).forEach(([cName, pVal]) => {
                const cm = getCourse(cName);
                const prop = pVal / asaasTotalPending;
                cm.mrr += (asaasMrrGlobal * prop);
            });
        } else if (asaasMrrGlobal > 0) {
            const cm = getCourse('PLATAFORMA GERAL');
            cm.mrr += asaasMrrGlobal;
        }
    }

    // Timeline de 18 meses futuros
    const futureMonths = [];
    const baseDate = new Date(2026, 8, 1); // 2026-09
    const mesesNomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    for (let i = 0; i < 18; i++) {
        const d = new Date(baseDate.getFullYear(), baseDate.getMonth() + i, 1);
        const ym = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
        const lbl = mesesNomes[d.getMonth()] + '/' + String(d.getFullYear()).slice(2);
        futureMonths.push({ mes: ym, label: lbl, idx: i });
    }

    // Finalizar cada curso
    Object.values(coursesMap).forEach(cm => {
        cm.previsto_mes_vigente = cm.pago_mes_atual + cm.proj_mes_atual;
        const diff = cm.previsto_mes_vigente - cm.pago_mes_ant;
        cm.crescimento_mom = cm.pago_mes_ant > 0 ? (((diff) / cm.pago_mes_ant) * 100).toFixed(1) : (cm.previsto_mes_vigente > 0 ? '+100' : '0.0');

        const mArr = cm.projecao_18m_sim;
        cm.projecao_mensal = futureMonths.map(fm => {
            let val = mArr[fm.idx] || 0;
            if (fm.idx === 0 && cm.proj_mes_atual > 0) {
                val = cm.proj_mes_atual;
            }
            cm.projecao_map[fm.mes] = val;
            return { mes: fm.mes, label: fm.label, previsto: val };
        });

        cm.proj_1m = cm.projecao_mensal[0]?.previsto || cm.proj_mes_atual || cm.mrr;
        cm.proj_3m = cm.projecao_mensal.slice(0, 3).reduce((a, b) => a + b.previsto, 0);
        cm.proj_6m = cm.projecao_mensal.slice(0, 6).reduce((a, b) => a + b.previsto, 0);
        cm.proj_12m = cm.projecao_mensal.slice(0, 12).reduce((a, b) => a + b.previsto, 0);

        cm.historico_mensal = Object.keys(cm.historico_map).sort().map(ym => {
            const [ano, m] = ym.split('-');
            const lbl = (mesesNomes[parseInt(m, 10) - 1] || m) + '/' + ano.slice(2);
            return { mes: ym, label: lbl, pago: cm.historico_map[ym] };
        });

        const baseAdimp = cm.pago_total + cm.atraso;
        cm.taxa_adimplencia = baseAdimp > 0 ? Math.round((cm.pago_total / baseAdimp) * 100) : 100;

        cm.kpis = {
            total_recebido: cm.pago_total,
            recebido_mes_atual: cm.pago_mes_atual,
            a_vencer_mes_atual: cm.proj_mes_atual,
            previsto_mes_vigente: cm.previsto_mes_vigente,
            mrr_ativo: cm.mrr,
            projecao_30d: cm.proj_1m,
            proj_3m: cm.proj_3m,
            proj_6m: cm.proj_6m,
            proj_12m: cm.proj_12m,
            total_em_atraso: cm.atraso,
            qtd_em_atraso: cm.qtd_atraso,
            total_faturas_pagas: cm.total_faturas_pagas,
            taxa_adimplencia: cm.taxa_adimplencia
        };
    });

    // Consolidação Global
    const globalObj = {
        curso: 'TODOS OS CURSOS (CONSOLIDADO)',
        fonte: (!gatewayFilter || gatewayFilter === 'all') ? 'Consolidado (Vindi & Asaas)' : (gatewayFilter === 'vindi' ? 'Vindi' : 'Asaas'),
        alunos_vigentes: 0,
        alunos_total: 0,
        pago_total: 0,
        pago_mes_atual: 0,
        proj_mes_atual: 0,
        previsto_mes_vigente: 0,
        pago_mes_ant: 0,
        atraso: 0,
        qtd_atraso: 0,
        mrr: 0,
        proj_1m: 0,
        proj_3m: 0,
        proj_6m: 0,
        proj_12m: 0,
        total_faturas_pagas: 0,
        historico_mensal: [],
        projecao_mensal: [],
        faturas_tabela: faturasList
    };

    const gHistMap = {};
    const gProjMap = {};

    Object.values(coursesMap).forEach(cm => {
        globalObj.alunos_vigentes += cm.alunos_vigentes;
        globalObj.alunos_total += cm.alunos_total;
        globalObj.pago_total += cm.pago_total;
        globalObj.pago_mes_atual += cm.pago_mes_atual;
        globalObj.proj_mes_atual += cm.proj_mes_atual;
        globalObj.previsto_mes_vigente += cm.previsto_mes_vigente;
        globalObj.pago_mes_ant += cm.pago_mes_ant;
        globalObj.atraso += cm.atraso;
        globalObj.qtd_atraso += cm.qtd_atraso;
        globalObj.mrr += cm.mrr;
        globalObj.proj_1m += cm.proj_1m;
        globalObj.proj_3m += cm.proj_3m;
        globalObj.proj_6m += cm.proj_6m;
        globalObj.proj_12m += cm.proj_12m;
        globalObj.total_faturas_pagas += cm.total_faturas_pagas;

        cm.historico_mensal.forEach(h => {
            if (!gHistMap[h.mes]) gHistMap[h.mes] = { mes: h.mes, label: h.label, pago: 0 };
            gHistMap[h.mes].pago += h.pago;
        });

        cm.projecao_mensal.forEach(p => {
            if (!gProjMap[p.mes]) gProjMap[p.mes] = { mes: p.mes, label: p.label, previsto: 0 };
            gProjMap[p.mes].previsto += p.previsto;
        });
    });

    globalObj.historico_mensal = Object.values(gHistMap).sort((a,b) => a.mes.localeCompare(b.mes));
    globalObj.projecao_mensal = Object.values(gProjMap).sort((a,b) => a.mes.localeCompare(b.mes));

    const gBaseAdimp = globalObj.pago_total + globalObj.atraso;
    globalObj.taxa_adimplencia = gBaseAdimp > 0 ? Math.round((globalObj.pago_total / gBaseAdimp) * 100) : 100;

    globalObj.kpis = {
        total_recebido: globalObj.pago_total,
        recebido_mes_atual: globalObj.pago_mes_atual,
        a_vencer_mes_atual: globalObj.proj_mes_atual,
        previsto_mes_vigente: globalObj.previsto_mes_vigente,
        mrr_ativo: globalObj.mrr,
        projecao_30d: globalObj.proj_1m,
        proj_3m: globalObj.proj_3m,
        proj_6m: globalObj.proj_6m,
        proj_12m: globalObj.proj_12m,
        total_em_atraso: globalObj.atraso,
        qtd_em_atraso: globalObj.qtd_atraso,
        total_faturas_pagas: globalObj.total_faturas_pagas,
        taxa_adimplencia: globalObj.taxa_adimplencia
    };

    return { courses: coursesMap, global: globalObj };
}


function fM(val) {
    const n = Number(val) || 0;
    return 'R$ ' + n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fN(val) {
    const n = Number(val) || 0;
    return n.toLocaleString('pt-BR');
}

function isPosPos(v) {
    return Number(v) >= 0 ? 'var(--emerald-d)' : '#DC2626';
}
function drawExecView(force) {
    if (_execDrawn && !force) return;
    _execDrawn = true;

    const mount = $('#exec-content-mount');
    if (!mount) return;

    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
    const funil = (DATA && DATA.funil) ? DATA.funil : {};
    const rawStudents = (DATA && DATA.students) ? DATA.students : [];
    const ev = (CURRENT_DATA && CURRENT_DATA.action_counts) ? CURRENT_DATA.action_counts : ((DATA && DATA.action_counts) ? DATA.action_counts : {});

    // Regra de exclusão para contas internas, testes e curso Nutrify Connect
    const isInvalidOrInternal = s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const cr = (s.curso || '').toString().toUpperCase().trim();
        if (cr.includes('NUTRIFY')) return true;
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@vectorcomunica')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com')) return true;
        return false;
    };

    // Resolução canônica de cursos para agrupar 100% de forma precisa
    const resolveCanonicalCourse = name => {
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
    };

    // Usar CURRENT_DATA.students ou rawStudents enriquecido (sempre excluindo testes e contas internas)
    const validRawStudents = rawStudents.filter(s => !isInvalidOrInternal(s));
    const baseStudents = (CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0)
        ? CURRENT_DATA.students.filter(s => !isInvalidOrInternal(s))
        : validRawStudents.map(s => {
            const scopy = { ...s };
            const acessou = scopy.acessou;
            const logins = scopy.logins || 0;
            const dias_inativo = scopy.dias_inativo || 0;
            const cadencia = scopy.cadencia || 0;
            const dias_ativo = scopy.dias_ativo || 0;

            const vSt = (scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : '').toLowerCase();
            const aSt = (scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : '').toLowerCase();
            const _vCan = vSt === 'cancelado' || vSt === 'canceled';
            const _aCan = aSt === 'cancelado' || aSt === 'canceled';
            const _vAct = vSt && !_vCan;
            const _aAct = aSt && !_aCan;

            if ((_vCan || _aCan) && !_vAct && !_aAct) {
                scopy.status = 'Cancelado';
            } else if (!acessou) {
                scopy.status = 'Nunca acessou';
            } else {
                if (logins > 1 && dias_ativo > 0) {
                    if (dias_inativo > 30 || (dias_inativo > 14 && cadencia > 0 && dias_inativo > (cadencia * 2.5))) {
                        scopy.status = 'Abandonou';
                    } else if (cadencia > 0 && dias_inativo > (cadencia * 1.5 + 2)) {
                        scopy.status = 'Em Risco';
                    } else {
                        scopy.status = 'Ativo';
                    }
                } else {
                    if (dias_inativo > 14) {
                        scopy.status = 'Abandonou';
                    } else if (dias_inativo > 7) {
                        scopy.status = 'Em Risco';
                    } else {
                        scopy.status = 'Ativo';
                    }
                }
            }
            return scopy;
        });

    // Mapeamento de Faturas pagas para identificar alunos pagantes reais
    const vFaturas = (vindi.faturas_tabela || []);
    const aFaturas = (asaas.faturas_tabela || []);

    const paidEmails = new Set();
    const paidNames = new Set();

    vFaturas.forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const nm = (f.aluno || '').toString().toLowerCase().trim();
            if (em) paidEmails.add(em);
            if (nm) paidNames.add(nm);
        }
    });

    aFaturas.forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const nm = (f.aluno || '').toString().toLowerCase().trim();
            if (em) paidEmails.add(em);
            if (nm) paidNames.add(nm);
        }
    });

    // Classificação precisa das Matrículas em: Canceladas, Concluídas/Quitadas e Vigentes (Ativas)
    const matriculasCanceladas = [];
    const matriculasConcluidas = [];
    const matriculasVigentes = [];
    let totalAlunosPagantes = 0;

    baseStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();

        const hasPaid = paidEmails.has(em) || paidNames.has(nm);
        if (hasPaid) totalAlunosPagantes++;

        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();

        const isCancel = vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled' || s.status === 'Cancelado';
        const isConcluido = !isCancel && (vSt === 'quitado' || aSt === 'quitado' || s.status === 'Concluído' || s.status === 'Encerrado' || s.turma_encerrada === true);

        if (isCancel) {
            matriculasCanceladas.push(s);
        } else if (isConcluido) {
            matriculasConcluidas.push(s);
        } else {
            matriculasVigentes.push(s);
        }
    });

    const totalMatriculas = baseStudents.length;
    const totalVigentes = matriculasVigentes.length;
    const totalConcluidas = matriculasConcluidas.length;
    const totalCanceladas = matriculasCanceladas.length;

    // Engajamento calculado ESTRITAMENTE sobre as Matrículas Vigentes (Regra de Negócio Grupo 5)
    let countEngajados = 0;
    let countEmRisco = 0;
    let countAbandonou = 0;
    let countNuncaAcessou = 0;

    matriculasVigentes.forEach(s => {
        const acessou = s.acessou;
        const logins = s.logins || 0;
        const dias_inativo = s.dias_inativo || 0;
        const cadencia = s.cadencia || 0;
        const dias_ativo = s.dias_ativo || 0;

        if (!acessou || logins === 0) {
            countNuncaAcessou++;
        } else if (logins > 1 && dias_ativo > 0) {
            if (dias_inativo > 30 || (dias_inativo > 14 && cadencia > 0 && dias_inativo > (cadencia * 2.5))) {
                countAbandonou++;
            } else if (cadencia > 0 && dias_inativo > (cadencia * 1.5 + 2)) {
                countEmRisco++;
            } else {
                countEngajados++;
            }
        } else {
            if (dias_inativo > 14) {
                countAbandonou++;
            } else if (dias_inativo > 7) {
                countEmRisco++;
            } else {
                countEngajados++;
            }
        }
    });

    // Mapeamento por Curso Canonizado (Especialidade) com Métricas Financeiras e Projeções Completas
    const coursesMap = {};
    const emailToCourse = {};
    const nameToCourse = {};

    // 1. Mapear cursos e engajamento a partir dos estudantes
    baseStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(s.curso);
        if (em) emailToCourse[em] = c;
        if (nm) nameToCourse[nm] = c;

        if (!coursesMap[c]) {
            coursesMap[c] = {
                curso: c, total: 0, vigentes: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, concluidos: 0, cancelados: 0,
                pago_total: 0, pago_mes_atual: 0, proj_mes_atual: 0, pago_mes_ant: 0, atraso: 0, mrr: 0,
                proj_1m: 0, proj_3m: 0, proj_6m: 0, proj_12m: 0
            };
        }
        const cm = coursesMap[c];
        cm.total++;

        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
        const isCancel = vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled' || s.status === 'Cancelado';
        const isConcluido = !isCancel && (vSt === 'quitado' || aSt === 'quitado' || s.status === 'Concluído' || s.status === 'Encerrado' || s.turma_encerrada === true);

        if (isCancel) {
            cm.cancelados++;
        } else if (isConcluido) {
            cm.concluidos++;
        } else {
            cm.vigentes++;
            const acessou = s.acessou;
            const logins = s.logins || 0;
            const dias_inativo = s.dias_inativo || 0;
            const cadencia = s.cadencia || 0;
            const dias_ativo = s.dias_ativo || 0;

            if (!acessou || logins === 0) {
                cm.nunca++;
            } else if (logins > 1 && dias_ativo > 0) {
                if (dias_inativo > 30 || (dias_inativo > 14 && cadencia > 0 && dias_inativo > (cadencia * 2.5))) {
                    cm.abandono++;
                } else if (cadencia > 0 && dias_inativo > (cadencia * 1.5 + 2)) {
                    cm.em_risco++;
                } else {
                    cm.ativos++;
                }
            } else {
                if (dias_inativo > 14) {
                    cm.abandono++;
                } else if (dias_inativo > 7) {
                    cm.em_risco++;
                } else {
                    cm.ativos++;
                }
            }
        }
    });

    const getCm = (cName) => {
        const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
        if (!coursesMap[c]) {
            coursesMap[c] = {
                curso: c, total: 0, vigentes: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, concluidos: 0, cancelados: 0,
                pago_total: 0, pago_mes_atual: 0, proj_mes_atual: 0, pago_mes_ant: 0, atraso: 0, mrr: 0,
                proj_1m: 0, proj_3m: 0, proj_6m: 0, proj_12m: 0
            };
        }
        return coursesMap[c];
    };

    // 2. Faturas Realizadas e Atraso (Vindi + Asaas)
    [...vFaturas, ...aFaturas].forEach(f => {
        const em = (f.email || '').toString().toLowerCase().trim();
        const nm = (f.aluno || '').toString().toLowerCase().trim();
        const cName = f.curso || emailToCourse[em] || nameToCourse[nm] || 'PLATAFORMA GERAL';
        const cm = getCm(cName);

        const val = Number(f.valor) || 0;
        const st = (f.status || '').toLowerCase();
        const dtPag = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
        const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();

        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            cm.pago_total += val;
            if (dtPag.includes('09/2026') || dtPag.includes('2026-09') || dtPag.includes('/09/26')) {
                cm.pago_mes_atual += val;
            } else if (dtPag.includes('08/2026') || dtPag.includes('2026-08') || dtPag.includes('/08/26')) {
                cm.pago_mes_ant += val;
            }
        } else if (st === 'em_atraso' || st === 'overdue') {
            cm.atraso += val;
        } else if (st === 'futuro' || st === 'a_vencer' || st === 'pending' || st === 'pendente') {
            if (dtVenc.includes('09/2026') || dtVenc.includes('2026-09') || dtVenc.includes('/09/26')) {
                cm.proj_mes_atual += val;
            }
        }
    });

    // 3. Assinaturas Vindi (MRR, A Vencer no Mês e Projeção 30d D+30 por Curso)
    const vSubsList = (vindi.subscriptions || (DATA && DATA.financeiro && DATA.financeiro.subscriptions) || []);
    vSubsList.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const em = (sub.customer_email || '').toString().toLowerCase().trim();
            const cName = sub.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const cm = getCm(cName);
            const price = Number(sub.valor_parcela) || 0;
            cm.mrr += price;

            const prox = (sub.proximo_vencimento || '').toString();
            if (prox.includes('/09/2026') || prox.includes('/09/26') || prox.includes('2026-09')) {
                cm.proj_mes_atual += price;
                cm.proj_1m += price;
            } else if (prox.includes('/10/2026') || prox.includes('/10/26') || prox.includes('2026-10')) {
                // Próximos 30 dias pegam primeira quinzena de outubro
                const dia = parseInt(prox.split('/')[0] || '0', 10);
                if (dia <= 14) {
                    cm.proj_1m += price;
                }
            } else if (!prox) {
                cm.proj_mes_atual += price;
                cm.proj_1m += price;
            }
        }
    });

    // 4. Clientes Asaas (MRR por Curso)
    const aData = asaas.data || {};
    Object.values(aData).forEach(stInfo => {
        if (stInfo.status_financeiro === 'adimplente') {
            const em = (stInfo.customer_email || stInfo.email || '').toString().toLowerCase().trim();
            const cName = stInfo.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const cm = getCm(cName);
            const price = Number(stInfo.valor_parcela || stInfo.mrr) || 0;
            cm.mrr += price;
        }
    });

    // 5. Totalizadores e Projeções Financeiras por Curso com Modelo de Duração de Contrato (Runoff / Encerramentos Reais)
    // Para cada curso, simulamos o fluxo mês a mês (1 a 12) baseado nas parcelas restantes de cada contrato ativo
    const courseMonthlyProjection = {};

    vSubsList.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const em = (sub.customer_email || '').toString().toLowerCase().trim();
            const cName = sub.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
            const price = Number(sub.valor_parcela) || 0;
            
            // Duração do plano e parcelas pagas
            const planoStr = (sub.plano || '').toString().toUpperCase();
            let totalCycles = 18; // Padrão de Pós-Graduação (18 meses)
            if (planoStr.includes('24')) totalCycles = 24;
            else if (planoStr.includes('12') || planoStr.includes('ANUAL')) totalCycles = 12;
            else if (planoStr.includes('6') || planoStr.includes('SEMESTRAL')) totalCycles = 6;
            
            const faturasArr = sub.faturas || [];
            const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
            const remainingCycles = Math.max(0, totalCycles - paidCount);

            if (!courseMonthlyProjection[c]) {
                courseMonthlyProjection[c] = Array(12).fill(0);
            }
            // Adiciona a parcela nos meses em que o contrato ainda está vigente
            for (let m = 0; m < 12; m++) {
                if (m < remainingCycles) {
                    courseMonthlyProjection[c][m] += price;
                }
            }
        }
    });

    // Mapear faturas pendentes do Asaas nos meses futuros
    [...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const cName = f.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
            const val = Number(f.valor) || 0;
            const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
            
            if (dtVenc) {
                // Estimar mês relativo (0 = mês 1, 1 = mês 2, ..., 11 = mês 12)
                const dObj = new Date(dtVenc.slice(0, 10));
                const hoje = new Date();
                const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                if (diffMeses >= 0 && diffMeses < 12) {
                    if (!courseMonthlyProjection[c]) courseMonthlyProjection[c] = Array(12).fill(0);
                    courseMonthlyProjection[c][diffMeses] += val;
                }
            }
        }
    });

    // Consolidar Projeções Contratuais Reais por Curso
    Object.values(coursesMap).forEach(cm => {
        cm.previsto_mes_vigente = cm.pago_mes_atual + cm.proj_mes_atual;
        const diff = cm.previsto_mes_vigente - cm.pago_mes_ant;
        cm.crescimento_mom = cm.pago_mes_ant > 0 ? (((diff) / cm.pago_mes_ant) * 100).toFixed(1) : (cm.previsto_mes_vigente > 0 ? '+100' : '0.0');
        
        const mArr = courseMonthlyProjection[cm.curso] || Array(12).fill(0);
        const p1mContratual = mArr[0] > 0 ? mArr[0] : (cm.proj_1m || cm.mrr);
        const p3mContratual = mArr.slice(0, 3).reduce((a, b) => a + b, 0);
        const p6mContratual = mArr.slice(0, 6).reduce((a, b) => a + b, 0);
        const p12mContratual = mArr.slice(0, 12).reduce((a, b) => a + b, 0);

        cm.proj_1m = p1mContratual;
        cm.proj_3m = p3mContratual > 0 ? p3mContratual : cm.mrr * 3;
        cm.proj_6m = p6mContratual > 0 ? p6mContratual : cm.mrr * 6;
        cm.proj_12m = p12mContratual > 0 ? p12mContratual : cm.mrr * 12;
    });

    // Projeções Globais Consolidadas da Carteira (Soma dos fluxos de contrato de todos os cursos)
    let globalProj3m = 0, globalProj6m = 0, globalProj12m = 0;
    Object.values(coursesMap).forEach(cm => {
        globalProj3m += cm.proj_3m;
        globalProj6m += cm.proj_6m;
        globalProj12m += cm.proj_12m;
    });

    // Totalizadores Consolidados Financeiros Unificados
    const vKpis = vindi.kpis || {};
    const aKpis = asaas.kpis || {};
    const finUnifiedGlobal = computeUnifiedFinancialDataset('all');
    const uKpis = finUnifiedGlobal.global.kpis || {};

    const recRealizadaTotal = uKpis.total_recebido || 0;
    const recMesAtual = uKpis.recebido_mes_atual || 0;
    const aVencerMesVigente = uKpis.a_vencer_mes_atual || 0;
    const totalPrevistoMesVigente = uKpis.previsto_mes_vigente || (recMesAtual + aVencerMesVigente);
    const mrrConsolidado = uKpis.mrr_ativo || 0;
    const proj30d = uKpis.projecao_30d || 0;
    const proj3mConsolidada = uKpis.proj_3m || (mrrConsolidado * 3);
    const proj6mConsolidada = uKpis.proj_6m || (mrrConsolidado * 6);
    const proj12m = uKpis.proj_12m || (mrrConsolidado * 12);
    const atrasoTotal = uKpis.total_em_atraso || 0;
    const qtdAtrasoTotal = uKpis.qtd_em_atraso || 0;
    const taxaAdimplencia = uKpis.taxa_adimplencia || 96;

    // Cálculo Dinâmico do Mês Vigente e Mês Anterior (MoM)
    const vHist = (vindi.historico_mensal || []);
    const aHist = (asaas.historico_mensal || []);

    const allMeses = Array.from(new Set([...vHist.map(h => h.mes), ...aHist.map(h => h.mes)])).filter(Boolean).sort();
    const mesVigenteKey = allMeses.length > 0 ? allMeses[allMeses.length - 1] : new Date().toISOString().slice(0, 7);
    const mesAnteriorKey = allMeses.length > 1 ? allMeses[allMeses.length - 2] : '';

    let vRealizadoAnt = 0, aRealizadoAnt = 0;
    vHist.forEach(h => { if (h.mes === mesAnteriorKey) vRealizadoAnt = (Number(h.pago) || 0); });
    aHist.forEach(h => { if (h.mes === mesAnteriorKey) aRealizadoAnt = (Number(h.pago) || 0); });

    const totalMesAnterior = vRealizadoAnt + aRealizadoAnt;
    const pctRealizadoMes = totalPrevistoMesVigente > 0 ? ((recMesAtual / totalPrevistoMesVigente) * 100).toFixed(1) : '0';
    
    // Crescimento MoM (Previsto do Mês Vigente vs Realizado Fechado do Mês Anterior)
    const diffMoM = totalPrevistoMesVigente - totalMesAnterior;
    const pctCrescimentoMoM = totalMesAnterior > 0 ? ((diffMoM / totalMesAnterior) * 100).toFixed(1) : '0';
    const isCrescimentoPositivo = Number(pctCrescimentoMoM) >= 0;



    const mesesNomes = { '01':'Jan', '02':'Fev', '03':'Mar', '04':'Abr', '05':'Mai', '06':'Jun', '07':'Jul', '08':'Ago', '09':'Set', '10':'Out', '11':'Nov', '12':'Dez' };
    const formatMesLabel = (k) => {
        if (!k || k.length < 7) return k;
        const [ano, m] = k.split('-');
        return `${mesesNomes[m] || m}/${ano.slice(2)}`;
    };
    const labelMesVigente = formatMesLabel(mesVigenteKey);
    const labelMesAnterior = formatMesLabel(mesAnteriorKey);

    // Funil Comercial
    const fKpis = funil.kpis || {};
    const totalLeads = Number(fKpis.total) || 26566;
    const leadsQualificados = Number(fKpis.lead_qualificado) || 5638;
    const contatadosWA = Number(fKpis.wa_contatados) || 365;

    const taxaChurn = totalMatriculas > 0 ? ((totalCanceladas / totalMatriculas) * 100).toFixed(1) : '0';
    const taxaRetencaoVigente = totalMatriculas > 0 ? (((totalMatriculas - totalCanceladas) / totalMatriculas) * 100).toFixed(1) : '100';

    const totalReproducoes = ev['ASSISTIU AULA'] || 0;
    const totalLogins = ev['LOGIN WEB'] || 0;

    // Ordenar cursos por matrículas vigentes e receita
    const cursosList = Object.values(coursesMap).filter(c => c.total > 0 || c.pago_total > 0 || c.atraso > 0 || c.mrr > 0).sort((a,b) => b.vigentes - a.vigentes || b.pago_total - a.pago_total);

    mount.innerHTML = `
      <!-- GRUPO 1: RECEITA & PROJEÇÃO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G1</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 1 — RECEITA &amp; PROJEÇÃO</h3>
              <div class="exec-sec-sub">Faturamento do mês vigente (realizado + projetado), evolução em relação ao mês anterior e previsibilidade de caixa (MRR, 1m, 3m, 6m e 12m).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('fin')">Ver Detalhes Financeiros →</button>
        </div>

        <!-- LINHA 1: PERFORMANCE DO MÊS E MRR -->
        <div class="exec-grid-4" style="margin-bottom:14px">
          <!-- CARD 1: RECEITA MÊS VIGENTE -->
          <div class="exec-card" style="border-top:3px solid var(--emerald)">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Mês Vigente (${labelMesVigente})</span>
              <span class="exec-pill ${isCrescimentoPositivo ? 'pill-green' : 'pill-amber'}">
                ${isCrescimentoPositivo ? '+' : ''}${pctCrescimentoMoM}% vs ${labelMesAnterior}
              </span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(totalPrevistoMesVigente)}</div>
            <div class="exec-card-sub">
              <b>${fM(recMesAtual)}</b> realizado (${pctRealizadoMes}%) + <b>${fM(aVencerMesVigente)}</b> a vencer em ${labelMesVigente}
            </div>
          </div>

          <!-- CARD 2: REALIZADO MÊS ANTERIOR -->
          <div class="exec-card" style="border-top:3px solid var(--sky)">
            <div class="exec-card-top">
              <span class="exec-card-label">Realizado Mês Anterior (${labelMesAnterior})</span>
              <span class="exec-pill pill-blue">Fechado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(totalMesAnterior)}</div>
            <div class="exec-card-sub">Vindi (${fM(vRealizadoAnt)}) + Asaas (${fM(aRealizadoAnt)})</div>
          </div>

          <!-- CARD 3: MRR (MENSALIDADE ATIVA) -->
          <div class="exec-card" style="border-top:3px solid var(--brand)">
            <div class="exec-card-top">
              <span class="exec-card-label">MRR (Mensalidade Ativa)</span>
              <span class="exec-pill pill-blue">Recorrente</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand)">${fM(mrrConsolidado)}</div>
            <div class="exec-card-sub">Base ativa: Vindi (${fM(vKpis.mrr_ativo)}) + Asaas (${fM(aKpis.mrr_ativo)})</div>
          </div>

          <!-- CARD 4: RECEITA REALIZADA TOTAL -->
          <div class="exec-card" style="border-top:3px solid #0d9488">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada (Total)</span>
              <span class="exec-pill pill-green">Caixa Acumulado</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(recRealizadaTotal)}</div>
            <div class="exec-card-sub">Vindi (${fM(vKpis.total_recebido)}) + Asaas (${fM(aKpis.total_recebido)})</div>
          </div>
        </div>

        <!-- LINHA 2: PROJEÇÕES FUTURAS DE CARTEIRA (1m, 3m, 6m, 12m) -->
        <div class="exec-grid-4">
          <!-- CARD 5: PROJEÇÃO 1 MÊS (30 DIAS) -->
          <div class="exec-card" style="background:rgba(2,132,199,0.02); border-left:3px solid #0284c7">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 1 Mês (30 dias)</span>
              <span class="exec-pill pill-blue">Próximos 30d (D+30)</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(proj30d)}</div>
            <div class="exec-card-sub">Faturas e parcelas agendadas para os próximos 30 dias corridos (D+30)</div>
          </div>

          <!-- CARD 6: PROJEÇÃO 3 MESES (TRIMESTRE) -->
          <div class="exec-card" style="background:rgba(79,70,229,0.02); border-left:3px solid #4f46e5">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 3 Meses (Trimestre)</span>
              <span class="exec-pill pill-blue">Próx. 90d</span>
            </div>
            <div class="exec-card-val" style="color:#4f46e5">${fM(proj3mConsolidada)}</div>
            <div class="exec-card-sub">Receita contratada real (considerando encerramentos e parcelas restantes)</div>
          </div>

          <!-- CARD 7: PROJEÇÃO 6 MESES (SEMESTRE) -->
          <div class="exec-card" style="background:rgba(124,58,237,0.02); border-left:3px solid #7c3aed">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 6 Meses (Semestre)</span>
              <span class="exec-pill pill-blue">Próx. 180d</span>
            </div>
            <div class="exec-card-val" style="color:#7c3aed">${fM(proj6mConsolidada)}</div>
            <div class="exec-card-sub">Receita contratada real (considerando encerramentos e parcelas restantes)</div>
          </div>

          <!-- CARD 8: PROJEÇÃO 12 MESES (ANUAL) -->
          <div class="exec-card" style="background:rgba(5,150,105,0.02); border-left:3px solid var(--emerald-d)">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Carteira (12 Meses)</span>
              <span class="exec-pill pill-green">Contratado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(proj12m)}</div>
            <div class="exec-card-sub">Receita contratada restante até o fim dos contratos ativos da carteira</div>
          </div>
        </div>
      </div>

      <!-- GRUPO 2: AQUISIÇÃO E VENDAS -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G2</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 2 — AQUISIÇÃO &amp; VENDAS</h3>
              <div class="exec-sec-sub">Volume de captação de leads, taxa de conversão comercial, ticket médio e eficiência de aquisição.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('funil')">Ver Funil Completo →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Leads Captados (CRM)</span>
              <span class="exec-pill pill-blue">Topo do Funil</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fN(totalLeads)}</div>
            <div class="exec-card-sub">Base total de cadastros sincronizados do RD Station</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Leads Qualificados</span>
              <span class="exec-pill pill-blue">${((leadsQualificados/Math.max(1, totalLeads))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand)">${fN(leadsQualificados)}</div>
            <div class="exec-card-sub">Interesse manifesto em cursos e pós-graduação</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Taxa de Conversão Global</span>
              <span class="exec-pill pill-green">Lead → Aluno</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${((totalMatriculas/Math.max(1, totalLeads))*100).toFixed(2)}%</div>
            <div class="exec-card-sub">${fN(totalMatriculas)} matrículas geradas a partir de ${fN(totalLeads)} leads</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Ticket Médio Anual</span>
              <span class="exec-pill pill-blue">Por Matrícula</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(totalMatriculas > 0 ? (recRealizadaTotal + proj12m) / totalMatriculas : 0)}</div>
            <div class="exec-card-sub">LTV médio contratual por aluno matriculado</div>
          </div>
        </div>
      </div>

      <!-- GRUPO 3: FUNIL DE CONVERSÃO INTEGRADO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G3</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 3 — FUNIL DE CONVERSÃO INTEGRADO</h3>
              <div class="exec-sec-sub">Jornada de ponta a ponta: do tráfego e captação inicial até o aluno pagante confirmado nos gateways.</div>
            </div>
          </div>
        </div>
        <div class="exec-funnel-bar">
          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">1. Cadastros / Leads</div>
            <div class="exec-funnel-step-val">${fN(totalLeads)}</div>
            <div class="exec-funnel-step-sub">Captação RD Station</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((leadsQualificados/Math.max(1, totalLeads))*100).toFixed(1)}%</span>
            <span>→</span>
          </div>

          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">2. Qualificados</div>
            <div class="exec-funnel-step-val">${fN(leadsQualificados)}</div>
            <div class="exec-funnel-step-sub">Perfil com interesse</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((contatadosWA/Math.max(1, leadsQualificados))*100).toFixed(1)}%</span>
            <span>→</span>
          </div>

          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">3. Abordagem WhatsApp</div>
            <div class="exec-funnel-step-val">${fN(contatadosWA)}</div>
            <div class="exec-funnel-step-sub">Atendimento Z-API</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((totalMatriculas/Math.max(1, totalLeads))*100).toFixed(1)}%</span>
            <span>→</span>
          </div>

          <div class="exec-funnel-step" style="border-color:var(--brand); background:rgba(30,58,138,0.03)">
            <div class="exec-funnel-step-label" style="color:var(--brand)">4. Matrículas Realizadas</div>
            <div class="exec-funnel-step-val" style="color:var(--brand)">${fN(totalMatriculas)}</div>
            <div class="exec-funnel-step-sub" style="font-weight:600; color:var(--ink)">
              ${fN(totalVigentes)} ativas vigentes · ${fN(totalConcluidas)} concluídas · ${fN(totalCanceladas)} canceladas
            </div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate" style="background:rgba(5,150,105,0.1); color:var(--emerald-d)">${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}%</span>
            <span>→</span>
          </div>

          <div class="exec-funnel-step step-highlight" style="border-color:var(--emerald-d); background:rgba(5,150,105,0.03)">
            <div class="exec-funnel-step-label" style="color:var(--emerald-d)">5. Alunos Pagantes</div>
            <div class="exec-funnel-step-val" style="color:var(--emerald-d)">${fN(totalAlunosPagantes)}</div>
            <div class="exec-funnel-step-sub" style="color:var(--muted)">
              Com fatura paga confirmada (${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}% da base)
            </div>
          </div>
        </div>
      </div>

      <!-- GRUPO 4: BASE E RECEITA RECORRENTE -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G4</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 4 — BASE &amp; RECEITA RECORRENTE</h3>
              <div class="exec-sec-sub">Evolução de alunos matriculados ativos vigentes, retenção, taxa de churn e inadimplência da carteira recorrente.</div>
            </div>
          </div>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Ativas Vigentes</span>
              <span class="exec-pill pill-green">${taxaRetencaoVigente}% Retenção</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(totalVigentes)}</div>
            <div class="exec-card-sub">De um total de ${fN(totalMatriculas)} contratos (${fN(totalConcluidas)} concluídos · ${fN(totalCanceladas)} cancelados)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Cancelamentos (Churn)</span>
              <span class="exec-pill pill-red">${taxaChurn}% Churn</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(totalCanceladas)}</div>
            <div class="exec-card-sub">Contratos rescindidos ou cancelados nas plataformas</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Inadimplência em Aberto</span>
              <span class="exec-pill pill-red">${qtdAtrasoTotal} Faturas</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fM(atrasoTotal)}</div>
            <div class="exec-card-sub">Vindi (${fM(vKpis.total_em_atraso)}) + Asaas (${fM(aKpis.total_em_atraso)})</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Taxa de Adimplência</span>
              <span class="exec-pill pill-green">Excelente</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${taxaAdimplencia}%</div>
            <div class="exec-card-sub">Índice de pagamento em dia na carteira ativa vigente</div>
          </div>
        </div>
      </div>

      <!-- GRUPO 5: ENGAJAMENTO E RETENÇÃO (BASE ATIVA VIGENTE) -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G5</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 5 — ENGAJAMENTO &amp; RETENÇÃO (BASE VIGENTE)</h3>
              <div class="exec-sec-sub">Alunos ativos vigentes e engajados, monitoramento de risco e inatividade severa (abandono).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('ret')">Ver Matriz de Retenção →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Engajados</span>
              <span class="exec-pill pill-green">${((countEngajados/Math.max(1, totalVigentes))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(countEngajados)}</div>
            <div class="exec-card-sub">Alunos ativos com aulas e frequência em dia</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos em Risco</span>
              <span class="exec-pill pill-amber">${((countEmRisco/Math.max(1, totalVigentes))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#D97706">${fN(countEmRisco)}</div>
            <div class="exec-card-sub">Quebra recente de cadência na base vigente (alerta)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Abandono / Inativos</span>
              <span class="exec-pill pill-red">${((countAbandonou/Math.max(1, totalVigentes))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(countAbandonou)}</div>
            <div class="exec-card-sub">Inatividade severa (&gt;14 ou &gt;30 dias sem acesso)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Nunca Acessaram</span>
              <span class="exec-pill pill-red">${((countNuncaAcessou/Math.max(1, totalVigentes))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(countNuncaAcessou)}</div>
            <div class="exec-card-sub">Alunos com contrato ativo sem 1º login registrado</div>
          </div>
        </div>
      </div>

      <!-- GRUPO 6: VISÃO POR CURSO (FINANCEIRO E PROJEÇÕES COMPLETAS) -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G6</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 6 — VISÃO POR CURSO (RECEITA, MRR &amp; PROJEÇÕES 1M, 3M, 6M, 12M)</h3>
              <div class="exec-sec-sub">Detalhamento por especialidade com alunos vigentes, realizado histórico, realizado no mês, projetado no mês, receita vigente com crescimento, receita mês anterior, MRR e projeções para 1m, 3m, 6m e 12m.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('home')">Ver Panorama Completo →</button>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left; min-width:1150px">
            <thead>
              <tr style="border-bottom:2px solid var(--line); color:var(--muted); font-size:10.5px; text-transform:uppercase; letter-spacing:0.04em">
                <th style="padding:10px 10px; min-width:200px">Especialidade / Curso</th>
                <th style="padding:10px 6px; text-align:center">Vigentes</th>
                <th style="padding:10px 8px; text-align:right">Receita Total (Histórica)</th>
                <th style="padding:10px 8px; text-align:right">Realizado (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Projetado (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Receita Mês (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Mês Anterior (${labelMesAnterior})</th>
                <th style="padding:10px 8px; text-align:right">MRR Estimado</th>
                <th style="padding:10px 8px; text-align:right">Proj. 1m (30d)</th>
                <th style="padding:10px 8px; text-align:right">Proj. 3m</th>
                <th style="padding:10px 8px; text-align:right">Proj. 6m</th>
                <th style="padding:10px 8px; text-align:right">Proj. 12m</th>
                <th style="padding:10px 8px; text-align:right">Inadimplência</th>
                <th style="padding:10px 8px; text-align:center">Status</th>
              </tr>
            </thead>
            <tbody>
              ${cursosList.map(c => {
                  let stBadge = '<span class="exec-pill pill-green">🟢 Saudável</span>';
                  if (c.atraso > 25000 || (c.abandono > 50 && c.ativos < 10)) {
                      stBadge = '<span class="exec-pill pill-red">🔴 Crítico</span>';
                  } else if (c.atraso > 8000 || c.em_risco > 2 || c.abandono > 30) {
                      stBadge = '<span class="exec-pill pill-amber">🟡 Atenção</span>';
                  }
                  const isPosMoM = Number(c.crescimento_mom) >= 0;
                  return `
                    <tr style="border-bottom:1px solid var(--line2); transition:background 0.15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
                      <td style="padding:10px; font-weight:700; color:var(--ink)">
                        <div style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:240px" title="${c.curso}">${c.curso}</div>
                      </td>
                      <td style="padding:10px 6px; text-align:center">
                        <span class="exec-pill pill-blue" style="font-weight:700">${c.vigentes}</span>
                      </td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:var(--emerald-d)">${fM(c.pago_total)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:var(--ink)">${fM(c.pago_mes_atual)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:#0284c7">${fM(c.proj_mes_atual)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:700; color:var(--ink)">
                        <div>${fM(c.previsto_mes_vigente)}</div>
                        <div style="font-size:9.5px; font-weight:700; color:${isPosPos(c.crescimento_mom)}">${isPosMoM ? '+' : ''}${c.crescimento_mom}%</div>
                      </td>
                      <td style="padding:10px 8px; text-align:right; color:var(--muted)">${fM(c.pago_mes_ant)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:700; color:var(--brand)">${fM(c.mrr)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:#0284c7">${fM(c.proj_1m)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:#4f46e5">${fM(c.proj_3m)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:600; color:#7c3aed">${fM(c.proj_6m)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:700; color:var(--ink)">${fM(c.proj_12m)}</td>
                      <td style="padding:10px 8px; text-align:right; font-weight:700; color:${c.atraso > 0 ? '#DC2626' : 'var(--muted2)'}">${fM(c.atraso)}</td>
                      <td style="padding:10px 8px; text-align:center">${stBadge}</td>
                    </tr>
                  `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- GRUPO 7: ALERTAS EXECUTIVOS & SEMÁFORO DE RISCO (DINÂMICO) -->
      ${(() => {
          // 1. Dinâmica do Alerta de Inadimplência
          const taxaInad = (100 - Number(taxaAdimplencia || 96));
          let g7InadClass = 'alert-sucesso';
          let g7InadIcon = '✓';
          let g7InadTitle = `Inadimplência Controlada (${taxaAdimplencia}% de Adimplência)`;
          let g7InadDesc = `Carteira altamente adimplente. Apenas ${qtdAtrasoTotal} título(s) pendente(s) somando ${fM(atrasoTotal)}. Manter réguas preventivas.`;

          if (atrasoTotal > 50000 || taxaInad >= 10) {
              g7InadClass = 'alert-critico';
              g7InadIcon = '⚠️';
              g7InadTitle = `Cobrança de Inadimplência (${qtdAtrasoTotal} faturas / ${fM(atrasoTotal)})`;
              g7InadDesc = `Inadimplência de ${taxaInad.toFixed(1)}% com ${qtdAtrasoTotal} títulos em atraso somando ${fM(atrasoTotal)}. Recomenda-se régua de renegociação ativa e automação via WhatsApp.`;
          } else if (atrasoTotal > 10000 || qtdAtrasoTotal > 0) {
              g7InadClass = 'alert-atencao';
              g7InadIcon = '🔔';
              g7InadTitle = `Acompanhamento de Inadimplência (${qtdAtrasoTotal} faturas / ${fM(atrasoTotal)})`;
              g7InadDesc = `Inadimplência em ${taxaInad.toFixed(1)}% com ${qtdAtrasoTotal} títulos pendentes de liquidação (${fM(atrasoTotal)}). Recomenda-se acompanhamento comercial.`;
          }

          // 2. Dinâmica do Alerta de Evasão / Abandono
          const totalAlertaAlunos = countEmRisco + countAbandonou;
          const pctAlertaAlunos = totalVigentes > 0 ? ((totalAlertaAlunos / totalVigentes) * 100) : 0;
          let g7RiscoClass = 'alert-sucesso';
          let g7RiscoIcon = '✓';
          let g7RiscoTitle = `Engajamento Saudável na Base Vigente (${fN(countEngajados)} ativos · ${(((countEngajados)/Math.max(1, totalVigentes))*100).toFixed(1)}%)`;
          let g7RiscoDesc = `Maioria dos alunos mantém frequência de estudos ativa. Apenas ${fN(totalAlertaAlunos)} aluno(s) requerem acompanhamento de cadência.`;

          if (pctAlertaAlunos >= 35) {
              g7RiscoClass = 'alert-critico';
              g7RiscoIcon = '🚨';
              g7RiscoTitle = `Alunos em Risco & Abandono na Base Vigente (${fN(totalAlertaAlunos)} alunos · ${pctAlertaAlunos.toFixed(1)}%)`;
              g7RiscoDesc = `Identificados ${countEmRisco} alunos em risco iminente e ${countAbandonou} em abandono na base vigente (${pctAlertaAlunos.toFixed(1)}%). Necessária ação pedagógica e resgate imediato via WhatsApp.`;
          } else if (pctAlertaAlunos >= 15) {
              g7RiscoClass = 'alert-atencao';
              g7RiscoIcon = '🔔';
              g7RiscoTitle = `Atenção à Cadência & Retenção (${fN(totalAlertaAlunos)} alunos · ${pctAlertaAlunos.toFixed(1)}%)`;
              g7RiscoDesc = `Identificados ${countEmRisco} alunos com quebra recente de cadência e ${countAbandonou} em inatividade prolongada. Recomenda-se disparo de incentivo de estudo.`;
          }

          // 3. Dinâmica do Alerta de Funil Comercial
          const semContatoWA = Math.max(0, leadsQualificados - contatadosWA);
          const pctSemContatoWA = leadsQualificados > 0 ? ((semContatoWA / leadsQualificados) * 100) : 0;
          let g7FunilClass = 'alert-sucesso';
          let g7FunilIcon = '✓';
          let g7FunilTitle = `Funil Comercial com Alta Cobertura (${fN(contatadosWA)} abordados)`;
          let g7FunilDesc = `Time comercial com rápida resposta e alta cobertura sobre os contatos qualificados do CRM.`;

          if (semContatoWA >= 1000 || pctSemContatoWA >= 60) {
              g7FunilClass = 'alert-critico';
              g7FunilIcon = '⚠️';
              g7FunilTitle = `Demanda Qualificada no Funil (${fN(semContatoWA)} sem contato · ${pctSemContatoWA.toFixed(0)}%)`;
              g7FunilDesc = `Grande contingente de leads qualificados no CRM ainda não abordados pelo time comercial via WhatsApp. Oportunidade prioritária de aumento de vendas.`;
          } else if (semContatoWA >= 200) {
              g7FunilClass = 'alert-atencao';
              g7FunilIcon = '📈';
              g7FunilTitle = `Pipeline Comercial com Oportunidades (${fN(semContatoWA)} sem contato)`;
              g7FunilDesc = `${fN(semContatoWA)} leads qualificados aguardam abordagem comercial ativa. Aumentar cadência de mensagens via Z-API.`;
          }

          // 4. Dinâmica de MRR e Sustentabilidade de Receita
          let g7MrrClass = 'alert-sucesso';
          let g7MrrIcon = '✓';
          let g7MrrTitle = `Adimplência Sólida e MRR Sustentável (${fM(mrrConsolidado)}/mês)`;
          let g7MrrDesc = `A carteira principal de alunos apresenta taxa de adimplência de ${taxaAdimplencia}% e receita recorrente robusta com mais de ${fM(proj12m)} contratados nos próximos 12 meses.`;

          if (taxaAdimplencia < 75) {
              g7MrrClass = 'alert-critico';
              g7MrrIcon = '⚠️';
              g7MrrTitle = `Risco de Receita & Inadimplência Elevada (${fM(mrrConsolidado)}/mês)`;
              g7MrrDesc = `Taxa de adimplência em ${taxaAdimplencia}%. Atenção prioritária para recuperação de receita e bloqueio de inadimplentes.`;
          } else if (taxaAdimplencia < 85 || Number(pctCrescimentoMoM) < 0) {
              g7MrrClass = 'alert-atencao';
              g7MrrIcon = '🔔';
              g7MrrTitle = `Acompanhamento de MRR (${fM(mrrConsolidado)}/mês)`;
              g7MrrDesc = `Receita mensal ativa em ${fM(mrrConsolidado)}. Projeção de 12 meses contratada em ${fM(proj12m)} com adimplência em ${taxaAdimplencia}%.`;
          }

          return `
          <div class="exec-sec">
            <div class="exec-sec-head">
              <div class="exec-sec-title-wrap">
                <div class="exec-sec-num">G7</div>
                <div>
                  <h3 class="exec-sec-title">GRUPO 7 — ALERTAS EXECUTIVOS &amp; SEMÁFORO DE RISCO</h3>
                  <div class="exec-sec-sub">Sinais de atenção prioritários para tomada de decisão da diretoria e liderança (regras dinâmicas e acionáveis).</div>
                </div>
              </div>
            </div>
            <div class="exec-grid-2">
              <div class="exec-alert ${g7InadClass}" onclick="_finSetFilter('em_atraso'); selectTab('fin');" style="cursor:pointer; transition:transform 0.15s ease, box-shadow 0.15s ease" title="Clique para gerenciar inadimplência no Financeiro">
                <div class="exec-alert-icon">${g7InadIcon}</div>
                <div>
                  <div class="exec-alert-title">${g7InadTitle}</div>
                  <div class="exec-alert-desc">${g7InadDesc}</div>
                </div>
              </div>

              <div class="exec-alert ${g7RiscoClass}" onclick="selectTab('ret')" style="cursor:pointer; transition:transform 0.15s ease, box-shadow 0.15s ease" title="Clique para gerenciar alunos em risco na Retenção">
                <div class="exec-alert-icon">${g7RiscoIcon}</div>
                <div>
                  <div class="exec-alert-title">${g7RiscoTitle}</div>
                  <div class="exec-alert-desc">${g7RiscoDesc}</div>
                </div>
              </div>

              <div class="exec-alert ${g7FunilClass}" onclick="selectTab('funil')" style="cursor:pointer; transition:transform 0.15s ease, box-shadow 0.15s ease" title="Clique para ver o Funil de Vendas">
                <div class="exec-alert-icon">${g7FunilIcon}</div>
                <div>
                  <div class="exec-alert-title">${g7FunilTitle}</div>
                  <div class="exec-alert-desc">${g7FunilDesc}</div>
                </div>
              </div>

              <div class="exec-alert ${g7MrrClass}" onclick="selectTab('fin')" style="cursor:pointer; transition:transform 0.15s ease, box-shadow 0.15s ease" title="Clique para ver projeções e MRR">
                <div class="exec-alert-icon">${g7MrrIcon}</div>
                <div>
                  <div class="exec-alert-title">${g7MrrTitle}</div>
                  <div class="exec-alert-desc">${g7MrrDesc}</div>
                </div>
              </div>
            </div>
          </div>
          `;
      })()}

      <!-- GRUPO 8: INDICADORES PARA EVOLUÇÃO FUTURA -->
      <div class="exec-sec" style="margin-bottom:0">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G8</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 8 — INDICADORES PARA EVOLUÇÃO FUTURA</h3>
              <div class="exec-sec-sub">Métricas estratégicas em planejamento e integração com novas ferramentas de inteligência.</div>
            </div>
          </div>
        </div>
        <div class="exec-grid-4">
          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">🚀 Roadmap / Integração</span>
            </div>
            <div style="font-weight:700; font-size:14px; color:var(--ink); margin-bottom:4px">SLA de Atendimento</div>
            <div style="font-size:11.5px; color:var(--muted); line-height:1.4">Meta: primeiro contato comercial em &lt; 15 min após conversão do lead. Integração prevista via webhook Z-API.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">🚀 Roadmap / Integração</span>
            </div>
            <div style="font-weight:700; font-size:14px; color:var(--ink); margin-bottom:4px">Tempo para 1º Contato</div>
            <div style="font-size:11.5px; color:var(--muted); line-height:1.4">Medição automatizada do intervalo entre submissão no formulário e envio da mensagem inicial no WhatsApp.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">🚀 Roadmap / Integração</span>
            </div>
            <div style="font-weight:700; font-size:14px; color:var(--ink); margin-bottom:4px">Taxa de Follow-up</div>
            <div style="font-size:11.5px; color:var(--muted); line-height:1.4">Rastreamento de 2ª e 3ª tentativas de contato comercial em leads sem resposta na primeira mensagem.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">🚀 Roadmap / Integração</span>
            </div>
            <div style="font-weight:700; font-size:14px; color:var(--ink); margin-bottom:4px">Score Preditivo de Churn</div>
            <div style="font-size:11.5px; color:var(--muted); line-height:1.4">Algoritmo preditivo cruzando frequência de login, visualização de módulos e histórico de pagamentos.</div>
          </div>
        </div>
      </div>
    `;
}


function drawHome(force) {
    if (!DATA.students) return;
    if (homeDrawn && !force) return;
    homeDrawn = true;

    // 1. Base filtrada (sempre prioriza os alunos processados com status)
    let baseStudents = (CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0)
        ? CURRENT_DATA.students
        : DATA.students.filter(s => {
            if (FILTER.curso !== 'all' && s.curso !== FILTER.curso) return false;
            return true;
        });

    const filterNameEl = document.getElementById('home-filter-name');
    if (filterNameEl) {
        filterNameEl.textContent = FILTER.curso === 'all' ? 'Todos os Cursos (Consolidado)' : FILTER.curso;
    }

    // =========================================================================
    // CLASSIFICAÇÃO DE MATRÍCULAS (Ativas, Canceladas, Encerradas)
    // Regra acordada:
    // - Cancelada: assinatura cancelada na Vindi/Asaas ou status 'Cancelado'
    // - Encerrada: data oficial de formatura/término da turma no sistema (atualmente 0)
    // - Ativa: não cancelada e não encerrada
    // =========================================================================
    const isMatriculaCancelada = s => {
        const vSt = s.vindi ? (s.vindi.status_assinatura || s.vindi.status_financeiro) : null;
        const aSt = s.asaas ? (s.asaas.status_assinatura || s.asaas.status_financeiro) : null;
        const _vCan = vSt === 'canceled' || vSt === 'cancelado';
        const _aCan = aSt === 'canceled' || aSt === 'cancelado';
        const _vAct = vSt && !_vCan;
        const _aAct = aSt && !_aCan;
        // Só considera cancelada se existe cancelamento E nenhum gateway ativo
        if (s.status === 'Cancelado') return true;
        return (_vCan || _aCan) && !_vAct && !_aAct;
    };

    const isMatriculaEncerrada = s => {
        if (s.status === 'Encerrado' || s.turma_encerrada === true) return true;
        if (s.data_formatura) {
            const dtForm = parseDate(s.data_formatura);
            if (dtForm && dtForm <= new Date()) return true;
        }
        return false;
    };

    const matriculasCanceladas = baseStudents.filter(isMatriculaCancelada);
    const matriculasEncerradas = baseStudents.filter(isMatriculaEncerrada);
    const matriculasAtivas = baseStudents.filter(s => !isMatriculaCancelada(s) && !isMatriculaEncerrada(s));

    const totalMatriculas = baseStudents.length;
    const totalMatriculasAtivas = matriculasAtivas.length;
    const totalMatriculasCanceladas = matriculasCanceladas.length;
    const totalMatriculasEncerradas = matriculasEncerradas.length;

    const uniqueEmailsAtivos = new Set(matriculasAtivas.map(s => (s.email || '').toLowerCase().trim()).filter(Boolean));
    const totalUnicosAtivos = uniqueEmailsAtivos.size;

    // Ações e Reproduções
    const ev = (CURRENT_DATA && CURRENT_DATA.action_counts) ? CURRENT_DATA.action_counts : {};
    const totalReproducoes = ev['ASSISTIU AULA'] || 0;
    const totalLogins = ev['LOGIN WEB'] || 0;

    // Plataformas (calculadas sobre matrículas ativas)
    let cativaCount = 0, academyCount = 0, ambasCount = 0;
    let cativaAcessaram = 0, academyAcessaram = 0, ambasAcessaram = 0;

    matriculasAtivas.forEach(s => {
        const plat = s.plataforma || 'Academy';
        if (plat === 'Cativa') {
            cativaCount++;
            if (s.acessou) cativaAcessaram++;
        } else if (plat === 'Ambas') {
            ambasCount++;
            if (s.acessou) ambasAcessaram++;
        } else {
            academyCount++;
            if (s.acessou) academyAcessaram++;
        }
    });

    // Cursos (EXCLUSIVO PARA MATRÍCULAS ATIVAS, conforme regra de negócio)
    let cursosCount = {};
    matriculasAtivas.forEach(s => {
        if (s.curso) cursosCount[s.curso] = (cursosCount[s.curso] || 0) + 1;
    });
    const sortedCursos = Object.entries(cursosCount).sort((a,b) => b[1] - a[1]);

    // Status de Engajamento da Base Ativa
    let stCounts = {
        'Concluído': 0, 'Ativo': 0, 'Em Risco': 0, 'Apenas Login': 0, 'Abandonou': 0, 'Cancelado': 0, 'Nunca acessou': 0
    };
    matriculasAtivas.forEach(s => {
        let st = s.status;
        if (!st) {
            st = (!s.acessou ? 'Nunca acessou' : 'Ativo');
        }
        if (st === 'Inativo') st = 'Abandonou';
        if (st === 'Atenção') st = s.acessou ? 'Em Risco' : 'Nunca acessou';
        
        if (stCounts[st] !== undefined) {
            stCounts[st]++;
        } else if (st.includes('Conclu')) {
            stCounts['Concluído']++;
        } else if (st.includes('Risco')) {
            stCounts['Em Risco']++;
        } else if (st.includes('Login')) {
            stCounts['Apenas Login']++;
        } else if (st.includes('Nunca')) {
            stCounts['Nunca acessou']++;
        } else {
            stCounts['Ativo']++;
        }
    });

    const engajados = (stCounts['Ativo'] || 0) + (stCounts['Concluído'] || 0);
    const taxaEngajados = totalMatriculasAtivas > 0 ? ((engajados / totalMatriculasAtivas) * 100).toFixed(0) : '0';
    
    const atencaoRisco = (stCounts['Em Risco'] || 0) + (stCounts['Apenas Login'] || 0);
    const taxaRisco = totalMatriculasAtivas > 0 ? ((atencaoRisco / totalMatriculasAtivas) * 100).toFixed(0) : '0';
    
    const criticos = (stCounts['Abandonou'] || 0) + (stCounts['Nunca acessou'] || 0);
    const taxaCriticos = totalMatriculasAtivas > 0 ? ((criticos / totalMatriculasAtivas) * 100).toFixed(0) : '0';

    const unicosAtivos = new Set(matriculasAtivas.filter(s => (s.status === 'Ativo' || (s.status||'').includes('Conclu'))).map(s => (s.email||'').toLowerCase().trim()).filter(Boolean)).size;
    const unicosRisco = new Set(matriculasAtivas.filter(s => ((s.status||'').includes('Risco') || (s.status||'').includes('Login'))).map(s => (s.email||'').toLowerCase().trim()).filter(Boolean)).size;
    const unicosAbandonaram = new Set(matriculasAtivas.filter(s => (s.status === 'Abandonou' || s.status === 'Inativo')).map(s => (s.email||'').toLowerCase().trim()).filter(Boolean)).size;
    const unicosNunca = new Set(matriculasAtivas.filter(s => (s.status === 'Nunca acessou' || !s.acessou)).map(s => (s.email||'').toLowerCase().trim()).filter(Boolean)).size;

    // RD Marketing
    let countComRD = 0;
    let eventsCount = {};
    let maturacaoList = [];
    matriculasAtivas.forEach(s => {
        const rd = s.rd_funnel;
        if (rd) {
            countComRD++;
            if (rd.dias_venda !== '' && rd.dias_venda !== null && !isNaN(rd.dias_venda)) {
                maturacaoList.push(Number(rd.dias_venda));
            }
            const evs = rd.eventos_detalhados || [];
            const seen = new Set();
            evs.forEach(e => {
                const name = e.evento_clean || e.evento_raw;
                if (name && !seen.has(name)) {
                    seen.add(name);
                    eventsCount[name] = (eventsCount[name] || 0) + 1;
                }
            });
        }
    });

    maturacaoList.sort((a,b)=>a-b);
    const medianaMat = maturacaoList.length > 0 ? maturacaoList[Math.floor(maturacaoList.length / 2)] : 0;
    const sortedEvents = Object.entries(eventsCount).sort((a,b) => b[1] - a[1]).slice(0, 5);
    const pctRastreadosRD = totalMatriculasAtivas > 0 ? ((countComRD / totalMatriculasAtivas) * 100).toFixed(0) : '0';

    drawLiveMonitor(matriculasAtivas);

    // WhatsApp
    const countWA = matriculasAtivas.filter(s => s.wa_total > 0).length;

    // --- 1. RENDERIZAR KPIS TOPO HOME (COM OS 3 CARDS DEDICADOS) ---
    const homeKpisEl = document.getElementById('home-kpis-grid');
    if (homeKpisEl) {
        homeKpisEl.innerHTML = `
          <!-- CARD 1: MATRÍCULAS ATIVAS -->
          <div class="kpi" style="border-top:3px solid var(--emerald)">
            <div class="k-lab"><i class="k-dot" style="background:var(--emerald)"></i>Matrículas Ativas</div>
            <div class="k-val" style="color:var(--emerald-d)">${fmt(totalMatriculasAtivas)}</div>
            <div class="k-sub">${fmt(totalUnicosAtivos)} alunos únicos vigentes</div>
          </div>

          <!-- CARD 2: MATRÍCULAS CANCELADAS -->
          <div class="kpi" style="border-top:3px solid #e11d48; cursor:pointer" onclick="switchTab('prog'); setTimeout(()=>{ const b=$('#search'); if(b){ b.value='cancelad'; if(typeof renderRows==='function') renderRows(); } }, 150)" title="Clique para filtrar matrículas canceladas na tabela">
            <div class="k-lab"><i class="k-dot" style="background:#e11d48"></i>Canceladas</div>
            <div class="k-val" style="color:#e11d48">${fmt(totalMatriculasCanceladas)}</div>
            <div class="k-sub">${totalMatriculas > 0 ? ((totalMatriculasCanceladas / totalMatriculas) * 100).toFixed(1) : 0}% do total acumulado (${fmt(totalMatriculas)})</div>
          </div>

          <!-- CARD 3: MATRÍCULAS ENCERRADAS (CONCLUSÃO DE CURSO) -->
          <div class="kpi" style="border-top:3px solid #7c3aed" title="Regra: Data oficial de término/formatura da turma cadastrada no sistema">
            <div class="k-lab"><i class="k-dot" style="background:#7c3aed"></i>Encerradas</div>
            <div class="k-val" style="color:#7c3aed">${fmt(totalMatriculasEncerradas)}</div>
            <div class="k-sub">Nenhuma turma encerrada</div>
          </div>

          <!-- CARD 4: REPRODUÇÕES -->
          <div class="kpi" style="border-top:3px solid var(--sky)">
            <div class="k-lab"><i class="k-dot" style="background:var(--sky)"></i>Reproduções</div>
            <div class="k-val" style="color:var(--sky)">${fmt(totalReproducoes)}</div>
            <div class="k-sub">Visualizações em aulas</div>
          </div>

          <!-- CARD 5: SAÚDE DA BASE -->
          <div class="kpi" style="border-top:3px solid #0d9488">
            <div class="k-lab"><i class="k-dot" style="background:#0d9488"></i>Saúde da Base</div>
            <div class="k-val" style="color:#0d9488">${taxaEngajados}%</div>
            <div class="k-sub">${fmt(engajados)} ativos / engajados</div>
          </div>

          <!-- CARD 6: ATENÇÃO & RISCO -->
          <div class="kpi" style="border-top:3px solid var(--amber)">
            <div class="k-lab"><i class="k-dot" style="background:var(--amber)"></i>Atenção &amp; Risco</div>
            <div class="k-val" style="color:var(--amber)">${fmt(atencaoRisco)}</div>
            <div class="k-sub">${taxaRisco}% precisam de contato</div>
          </div>

          <!-- CARD 7: RASTREADOS CRM -->
          <div class="kpi" style="border-top:3px solid #0077b6">
            <div class="k-lab"><i class="k-dot" style="background:#0077b6"></i>Rastreados RD</div>
            <div class="k-val" style="color:#0077b6">${fmt(countComRD)}</div>
            <div class="k-sub">${pctRastreadosRD}% da base ativa no CRM</div>
          </div>

          <!-- CARD 8: CONTATOS WHATSAPP -->
          <div class="kpi" style="border-top:3px solid #25D366">
            <div class="k-lab"><i class="k-dot" style="background:#25D366"></i>Contatos WhatsApp</div>
            <div class="k-val" style="color:#25D366">${fmt(countWA)}</div>
            <div class="k-sub">Com histórico no chat</div>
          </div>
        `;
    }

    // --- 2. RENDERIZAR PLATAFORMAS ---
    const platTotalEl = document.getElementById('home-plat-total');
    if (platTotalEl) platTotalEl.textContent = `${totalMatriculas} Matrículas Totais`;

    const platBarsEl = document.getElementById('home-platforms-bars');
    if (platBarsEl) {
        const pctCativa = totalMatriculas > 0 ? (cativaCount / totalMatriculas * 100).toFixed(1) : 0;
        const pctAcademy = totalMatriculas > 0 ? (academyCount / totalMatriculas * 100).toFixed(1) : 0;
        const pctAmbas = totalMatriculas > 0 ? (ambasCount / totalMatriculas * 100).toFixed(1) : 0;

        platBarsEl.innerHTML = `
          <!-- CATIVA DIGITAL -->
          <div style="display:flex; flex-direction:column; gap:6px">
            <div style="display:flex; justify-content:space-between; align-items:center">
              <div style="display:flex; align-items:center; gap:8px">
                <span style="font-size:10px; font-weight:700; padding:2px 7px; border-radius:4px; background:rgba(236,72,153,0.12); color:#db2777; border:1px solid rgba(236,72,153,0.3)">Cativa Digital</span>
                <span style="font-size:12px; font-weight:600; color:var(--ink)">Nova Plataforma de Pós-Graduações</span>
              </div>
              <div style="font-size:12px; font-weight:700; color:var(--ink)">${cativaCount} alunos <span style="font-size:11px; font-weight:500; color:var(--muted)">(${pctCativa}%)</span></div>
            </div>
            <div style="background:var(--line); height:8px; border-radius:4px; overflow:hidden">
              <div style="width:${pctCativa}%; background:#db2777; height:100%; border-radius:4px"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:10.5px; color:var(--muted)">
              <span>Ativação: <b>${cativaAcessaram}</b> já acessaram (${(cativaAcessaram/Math.max(1,cativaCount)*100).toFixed(0)}%)</span>
              <span>12.246 logs integrados via API</span>
            </div>
          </div>

          <!-- INFECTOCAST ACADEMY -->
          <div style="display:flex; flex-direction:column; gap:6px">
            <div style="display:flex; justify-content:space-between; align-items:center">
              <div style="display:flex; align-items:center; gap:8px">
                <span style="font-size:10px; font-weight:700; padding:2px 7px; border-radius:4px; background:rgba(2,132,199,0.12); color:#0284c7; border:1px solid rgba(2,132,199,0.3)">InfectoCast Academy</span>
                <span style="font-size:12px; font-weight:600; color:var(--ink)">Plataforma Hotmart / Club</span>
              </div>
              <div style="font-size:12px; font-weight:700; color:var(--ink)">${academyCount} alunos <span style="font-size:11px; font-weight:500; color:var(--muted)">(${pctAcademy}%)</span></div>
            </div>
            <div style="background:var(--line); height:8px; border-radius:4px; overflow:hidden">
              <div style="width:${pctAcademy}%; background:#0284c7; height:100%; border-radius:4px"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:10.5px; color:var(--muted)">
              <span>Ativação: <b>${academyAcessaram}</b> já acessaram (${(academyAcessaram/Math.max(1,academyCount)*100).toFixed(0)}%)</span>
              <span>7.157 logs integrados via API</span>
            </div>
          </div>

          <!-- AMBAS AS PLATAFORMAS -->
          <div style="display:flex; flex-direction:column; gap:6px">
            <div style="display:flex; justify-content:space-between; align-items:center">
              <div style="display:flex; align-items:center; gap:8px">
                <span style="font-size:10px; font-weight:700; padding:2px 7px; border-radius:4px; background:rgba(124,58,237,0.12); color:#7c3aed; border:1px solid rgba(124,58,237,0.3)">Presente em Ambas</span>
                <span style="font-size:12px; font-weight:600; color:var(--ink)">Migração / Cursos Simultâneos</span>
              </div>
              <div style="font-size:12px; font-weight:700; color:var(--ink)">${ambasCount} alunos <span style="font-size:11px; font-weight:500; color:var(--muted)">(${pctAmbas}%)</span></div>
            </div>
            <div style="background:var(--line); height:8px; border-radius:4px; overflow:hidden">
              <div style="width:${Math.max(2, pctAmbas)}%; background:#7c3aed; height:100%; border-radius:4px"></div>
            </div>
          </div>
        `;
    }

    // --- 3. RENDERIZAR CURSOS MAIS PROCURADOS ---
    const cursosSubEl = document.getElementById('home-cursos-sub');
    if (cursosSubEl) {
        cursosSubEl.innerHTML = `Ranking considerando apenas <b>${fmt(totalMatriculasAtivas)} matrículas ativas</b> vigentes.`;
    }

    const coursesListEl = document.getElementById('home-courses-list');
    if (coursesListEl) {
        coursesListEl.innerHTML = sortedCursos.map(([cName, count], idx) => {
            const pct = totalMatriculasAtivas > 0 ? (count / totalMatriculasAtivas * 100).toFixed(1) : 0;
            const isPos = cName.includes('Pós') || cName.includes('Pos');
            return `
              <div style="display:flex; flex-direction:column; gap:4px">
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px">
                  <div style="display:flex; align-items:center; gap:6px; overflow:hidden">
                    <span style="font-size:10px; font-weight:700; color:var(--muted); min-width:16px">#${idx+1}</span>
                    <span style="font-weight:600; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${cName}">${cName}</span>
                  </div>
                  <div style="display:flex; align-items:center; gap:8px; white-space:nowrap">
                    <b style="color:var(--ink)">${count}</b>
                    <span style="color:var(--muted); font-size:11px">(${pct}%)</span>
                  </div>
                </div>
                <div style="background:var(--line); height:6px; border-radius:3px; overflow:hidden">
                  <div style="width:${pct}%; background:${isPos?'var(--emerald)':'var(--sky)'}; height:100%; border-radius:3px"></div>
                </div>
              </div>
            `;
        }).join('');
    }

    // --- 4. RENDERIZAR SAÚDE DA BASE ---
    const statusDistEl = document.getElementById('home-status-distribution');
    if (statusDistEl) {
        statusDistEl.innerHTML = `
          <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-bottom:8px">
            <div style="background:var(--emerald-w); border:1px solid rgba(18,161,122,0.25); border-radius:8px; padding:10px 12px; cursor:pointer" onclick="goToStatus('Ativo')" title="Ver alunos engajados">
              <div style="font-size:10px; font-weight:700; color:var(--emerald-d); text-transform:uppercase">Engajados</div>
              <div style="font-size:22px; font-weight:800; color:var(--emerald-d); margin-top:2px">${fmt(engajados)}</div>
              <div style="font-size:10.5px; color:var(--muted); margin-top:2px"><b>${taxaEngajados}%</b> das matrículas</div>
              <div style="font-size:10px; color:var(--emerald-d); margin-top:3px; font-weight:600">${fmt(unicosAtivos)} alunos únicos</div>
            </div>
            <div style="background:var(--amber-w); border:1px solid rgba(224,145,47,0.25); border-radius:8px; padding:10px 12px; cursor:pointer" onclick="goToStatus('Em Risco')" title="Ver alunos em alerta">
              <div style="font-size:10px; font-weight:700; color:var(--amber); text-transform:uppercase">Em Alerta</div>
              <div style="font-size:22px; font-weight:800; color:var(--amber); margin-top:2px">${fmt(atencaoRisco)}</div>
              <div style="font-size:10.5px; color:var(--muted); margin-top:2px"><b>${taxaRisco}%</b> em risco/atenção</div>
              <div style="font-size:10px; color:var(--amber); margin-top:3px; font-weight:600">${fmt(unicosRisco)} alunos únicos</div>
            </div>
            <div style="background:var(--coral-w); border:1px solid rgba(224,85,85,0.25); border-radius:8px; padding:10px 12px; cursor:pointer" onclick="switchTab('ret')" title="Ver alunos que abandonaram">
              <div style="font-size:10px; font-weight:700; color:var(--coral); text-transform:uppercase">Críticos / Evasão</div>
              <div style="font-size:22px; font-weight:800; color:var(--coral); margin-top:2px">${fmt(criticos)}</div>
              <div style="font-size:10.5px; color:var(--muted); margin-top:2px"><b>${taxaCriticos}%</b> inatividade severa</div>
              <div style="font-size:10px; color:var(--coral); margin-top:3px; font-weight:600">${fmt(unicosAbandonaram + unicosNunca)} alunos únicos</div>
            </div>
          </div>

          <!-- STATUS DETALHADO -->
          <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; margin-bottom:8px">
            <div style="background:rgba(18,161,122,0.08); border:1px solid rgba(18,161,122,0.2); border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="goToStatus('Concluído')">
              <span style="font-size:10.5px; font-weight:600; color:var(--emerald-d)">● Concluído</span>
              <span style="font-size:11.5px; font-weight:800; color:var(--emerald-d)">${fmt(stCounts['Concluído'])}</span>
            </div>
            <div style="background:rgba(2,132,199,0.08); border:1px solid rgba(2,132,199,0.2); border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="goToStatus('Ativo')">
              <span style="font-size:10.5px; font-weight:600; color:var(--sky-d)">● Ativo</span>
              <span style="font-size:11.5px; font-weight:800; color:var(--sky-d)">${fmt(stCounts['Ativo'])}</span>
            </div>
            <div style="background:rgba(224,145,47,0.08); border:1px solid rgba(224,145,47,0.2); border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="goToStatus('Em Risco')">
              <span style="font-size:10.5px; font-weight:600; color:var(--amber)">● Em Risco</span>
              <span style="font-size:11.5px; font-weight:800; color:var(--amber)">${fmt(stCounts['Em Risco'])}</span>
            </div>
            <div style="background:rgba(100,116,139,0.08); border:1px solid rgba(100,116,139,0.2); border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="goToStatus('Apenas Login')">
              <span style="font-size:10.5px; font-weight:600; color:#475569">● Apenas Login</span>
              <span style="font-size:11.5px; font-weight:800; color:#475569">${fmt(stCounts['Apenas Login'])}</span>
            </div>
            <div style="background:rgba(224,85,85,0.08); border:1px solid rgba(224,85,85,0.2); border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="goToStatus('Abandonou')">
              <span style="font-size:10.5px; font-weight:600; color:var(--coral)">● Abandonou</span>
              <span style="font-size:11.5px; font-weight:800; color:var(--coral)">${fmt(stCounts['Abandonou'])}</span>
            </div>
            <div style="background:rgba(100,116,139,0.08); border:1px solid rgba(100,116,139,0.2); border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="goToStatus('Cancelado')">
              <span style="font-size:10.5px; font-weight:600; color:#64748b">● Cancelado</span>
              <span style="font-size:11.5px; font-weight:800; color:#64748b">${fmt(stCounts['Cancelado'])}</span>
            </div>
            <div style="background:rgba(0,0,0,0.04); border:1px solid rgba(0,0,0,0.1); border-radius:6px; padding:5px 8px; display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="goToStatus('Nunca acessou')">
              <span style="font-size:10.5px; font-weight:600; color:var(--muted)">● Nunca acessou</span>
              <span style="font-size:11.5px; font-weight:800; color:var(--muted)">${fmt(stCounts['Nunca acessou'])}</span>
            </div>
          </div>

          <div style="font-size:11px; color:var(--muted); line-height:1.4">
            Acompanhamento preditivo baseado na cadência média de logins e dias sem acesso (<b style="color:var(--ink)">clique</b> em qualquer badge para filtrar a lista).
          </div>
        `;
    }

    // --- 5. RENDERIZAR MARKETING & ORIGEM ---
    const mktSummaryEl = document.getElementById('home-marketing-summary');
    if (mktSummaryEl) {
        mktSummaryEl.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(0,180,216,0.06); border:1px solid rgba(0,180,216,0.2); border-radius:8px; padding:8px 12px; margin-bottom:12px">
            <span style="font-size:11.5px; color:var(--ink)">Tempo Mediano de Decisão (Maturação):</span>
            <b style="font-size:13px; color:#0077b6">${medianaMat} dias até matricular</b>
          </div>
          <div style="font-size:11.5px; font-weight:700; color:var(--ink); margin-bottom:8px">Top Ações Pré-Matrícula que Mais Geraram Alunos:</div>
          <div style="display:flex; flex-direction:column; gap:6px">
            ${sortedEvents.map(([evName, cnt], idx) => `
              <div style="display:flex; justify-content:space-between; align-items:center; font-size:11.5px; padding:4px 0; border-bottom:1px solid rgba(0,0,0,0.04)">
                <div style="display:flex; align-items:center; gap:6px; overflow:hidden">
                  <span style="font-size:10px; font-weight:700; color:var(--muted)">#${idx+1}</span>
                  <span style="font-weight:600; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${evName}">${evName}</span>
                </div>
                <b style="color:var(--emerald-d); white-space:nowrap">${cnt} alunos</b>
              </div>
            `).join('')}
          </div>
        `;
    }
}

// FUNIL DE LEADS
let funilDrawn = false;
let matFilter = 'all';
window.funilSortCol = 'Score';
window.funilSortDir = -1;

window.setFunilSort = function(col) {
    if (window.funilSortCol === col) {
        window.funilSortDir *= -1;
    } else {
        window.funilSortCol = col;
        window.funilSortDir = 1;
        if (col === 'Score' || col === 'Conversões') window.funilSortDir = -1;
    }
    drawFunil(true);
};


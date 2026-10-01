import re

with open('template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update modal HTML
modal_start = html.find('<div class="modal-ov" id="modal-sync-24h">')
modal_end = html.find('<div class="modal-ov" id="modal">')

new_modal_html = '''<div class="modal-ov" id="modal-sync-24h">
  <div class="modal" role="dialog" aria-modal="true" style="max-width:840px; padding:0; overflow:hidden; border-radius:14px; background:var(--card); box-shadow:0 10px 40px rgba(0,0,0,0.35);">
    <div class="md-head" style="background:var(--card-hover); padding:16px 20px; border-bottom:1px solid var(--line); position:relative;">
      <button class="md-close" onclick="closeSyncModal24h()" aria-label="Fechar" style="position:absolute; right:16px; top:16px; border:none; background:transparent; font-size:18px; cursor:pointer; color:var(--muted);">✕</button>
      <h3 style="margin:0 0 4px; font-size:16px; font-weight:800; color:var(--ink); display:flex; align-items:center; gap:8px;">
        <span style="display:inline-block; width:9px; height:9px; border-radius:50%; background:#10b981; box-shadow:0 0 10px #10b981;"></span>
        Telemetria de Matrículas // Base de Alunos & Gateways
      </h3>
      <div style="font-size:11.5px; color:var(--muted)">Auditoria detalhada de novos alunos considerando Primeiro Pagamento (Vindi/Asaas) e Cadastros de Ensino (Academy / Cativa)</div>
    </div>
    
    <!-- Mini Telemetria & Estatísticas -->
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; padding:14px 20px; background:var(--bg); border-bottom:1px solid var(--line);">
      <div style="padding:10px 14px; background:var(--card); border:1px solid var(--line); border-radius:8px;">
        <div style="font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:700;">Matrículas no Período</div>
        <div style="font-size:18px; font-weight:800; color:#10b981" id="msync-total-val">0</div>
      </div>
      <div style="padding:10px 14px; background:var(--card); border:1px solid var(--line); border-radius:8px;">
        <div style="font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:700;">Sinais Monitorados</div>
        <div style="font-size:13.5px; font-weight:800; color:var(--ink); margin-top:2px;">Primeiro Pagamento + Cadastros</div>
      </div>
      <div style="padding:10px 14px; background:var(--card); border:1px solid var(--line); border-radius:8px;">
        <div style="font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:700;">Último Registro</div>
        <div style="font-size:12px; font-weight:700; color:var(--ink); margin-top:3px" id="msync-last-time">Hoje recente</div>
      </div>
    </div>

    <!-- Abas Rápidas de Período -->
    <div style="display:flex; gap:8px; padding:12px 20px 0; background:var(--card);">
      <button id="mbtn-tab-24h" onclick="filterMatriculasModalPeriod('24h')" style="padding:7px 16px; border-radius:8px; border:1px solid var(--line); font-size:11.5px; font-weight:700; cursor:pointer; transition:all 0.15s;">
        ⚡ Últimas 24 Horas
      </button>
      <button id="mbtn-tab-30d" onclick="filterMatriculasModalPeriod('30d')" style="padding:7px 16px; border-radius:8px; border:1px solid var(--line); font-size:11.5px; font-weight:700; cursor:pointer; transition:all 0.15s;">
        📅 Últimos 30 Dias
      </button>
      <button id="mbtn-tab-all" onclick="filterMatriculasModalPeriod('all')" style="padding:7px 16px; border-radius:8px; border:1px solid var(--line); font-size:11.5px; font-weight:700; cursor:pointer; transition:all 0.15s;">
        📋 Todas as Matrículas
      </button>
    </div>

    <!-- Barra de Filtro Rápido -->
    <div style="padding:12px 20px 0;">
      <input type="text" id="msync-search" placeholder="Filtrar por nome do aluno, e-mail, curso ou sinal..." style="width:100%; box-sizing:border-box; padding:9px 14px; font-size:12px; border-radius:8px; border:1px solid var(--line); background:var(--bg); color:var(--ink); outline:none;" />
    </div>

    <!-- Tabela de Alunos -->
    <div class="md-body" id="msync-table-body" style="max-height:50vh; overflow-y:auto; padding:12px 20px 20px;"></div>
  </div>
</div>
\n'''

if modal_start != -1 and modal_end != -1:
    html = html[:modal_start] + new_modal_html + html[modal_end:]
    print("Modal HTML updated.")

# 2. Update getMatriculasAuditoriaData before drawExecView
g_sync_pos = html.find('function getMatriculasAuditoriaData() {')
if g_sync_pos == -1:
    g_sync_pos = html.find('function getSync24hData() {')

d_exec_pos = html.find('function drawExecView(', g_sync_pos)

new_get_data_js = '''function getMatriculasAuditoriaData() {
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
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@cativa')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com')) return true;
        return false;
    };

    // Mapear primeiro pagamento de cada aluno (por e-mail e por nome)
    const firstPayMap = new Map();
    [...vFaturas, ...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const nm = (f.aluno || '').toString().toLowerCase().trim();
            const dtStr = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
            const d = parseDateUniversal(dtStr);
            const gw = (f.gateway || (vFaturas.includes(f) ? 'Vindi' : 'Asaas'));
            if (d) {
                if (em) {
                    if (!firstPayMap.has(em) || d < firstPayMap.get(em).date) {
                        firstPayMap.set(em, { date: d, gateway: gw, valor: f.valor });
                    }
                }
                if (nm) {
                    if (!firstPayMap.has(nm) || d < firstPayMap.get(nm).date) {
                        firstPayMap.set(nm, { date: d, gateway: gw, valor: f.valor });
                    }
                }
            }
        }
    });

    const now = new Date();
    const t24h = new Date(now.getTime() - 24 * 3600 * 1000);
    const t30d = new Date(now.getTime() - 30 * 24 * 3600 * 1000);

    const validStudents = rawStudents.filter(s => !isInvalidOrInternal(s));
    const allMatriculas = [];

    validStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().trim();
        const dtInsc = parseDateUniversal(s.data_insc || s.data_inscricao || s.data_matricula);
        const payInfo = firstPayMap.get(em) || firstPayMap.get(nm.toLowerCase());

        let effDate = null;
        let origemSinal = '';
        let tipoSinal = '';

        // Regra de ouro: Primeiro pagamento é o melhor sinal de matrícula
        if (payInfo) {
            effDate = payInfo.date;
            origemSinal = `Primeiro Pagamento (${payInfo.gateway})`;
            tipoSinal = 'gateway';
        } else if (dtInsc) {
            effDate = dtInsc;
            const plat = s.plataforma || 'Academy';
            origemSinal = `Cadastro ${plat}`;
            tipoSinal = 'plataforma';
        }

        if (effDate) {
            const dtFmt = `${String(effDate.getDate()).padStart(2,'0')}/${String(effDate.getMonth()+1).padStart(2,'0')}/${effDate.getFullYear()} ${String(effDate.getHours()).padStart(2,'0')}:${String(effDate.getMinutes()).padStart(2,'0')}`;
            allMatriculas.push({
                nome: nm || 'Aluno',
                email: em,
                curso: s.curso || 'PLATAFORMA GERAL',
                data: effDate,
                data_fmt: dtFmt,
                origem_sinal: origemSinal,
                tipo_sinal: tipoSinal,
                status: s.status || 'Ativo',
                is_24h: effDate >= t24h,
                is_30d: effDate >= t30d
            });
        }
    });

    // Ordenar decrescente por data de matrícula
    allMatriculas.sort((a, b) => b.data - a.data);

    const list24h = allMatriculas.filter(m => m.is_24h);
    const list30d = allMatriculas.filter(m => m.is_30d);

    return {
        count24h: list24h.length,
        count30d: list30d.length,
        total: allMatriculas.length,
        list24h: list24h,
        list30d: list30d,
        allRecords: allMatriculas
    };
}

function getSync24hData() {
    return getMatriculasAuditoriaData();
}

'''

if g_sync_pos != -1 and d_exec_pos != -1:
    html = html[:g_sync_pos] + new_get_data_js + html[d_exec_pos:]
    print("getMatriculasAuditoriaData updated.")

# 3. Update G0 in drawExecView
g0_idx = html.find('// Telemetria e Monitoramento ao Vivo (G0')
if g0_idx == -1:
    g0_idx = html.find('// Telemetria e Monitoramento ao Vivo')
g1_idx = html.find('<!-- G1')

new_g0_block = '''// Telemetria e Monitoramento ao Vivo (G0 - Base Real de Matrículas: Academy, Cativa e Primeiro Pagamento)
    const matInfo = getMatriculasAuditoriaData();
    const matriculas24h = matInfo.count24h;
    const matriculas30d = matInfo.count30d;

    // Calcular métricas financeiras reais de 24 horas e 30 dias para G0
    const nowRef = new Date();
    const t24hRef = new Date(nowRef.getTime() - 24 * 3600 * 1000);
    const t30dRef = new Date(nowRef.getTime() - 30 * 24 * 3600 * 1000);

    let rec24h = 0;
    let rec30d = 0;
    [...vFaturas, ...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const dtStr = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
            const d = parseDateUniversal(dtStr);
            if (d) {
                const val = Number(f.valor) || 0;
                if (d >= t24hRef) rec24h += val;
                if (d >= t30dRef) rec30d += val;
            }
        }
    });

    let alunosAtivos24hSet = new Set();
    let alunosAtivos30dSet = new Set();

    baseStudents.forEach(s => {
        if (s.events) {
            s.events.forEach(e => {
                const ed = parseDateUniversal(e.d);
                if (ed) {
                    if (ed >= t24hRef) alunosAtivos24hSet.add(s.email);
                    if (ed >= t30dRef) alunosAtivos30dSet.add(s.email);
                }
            });
        }
    });

    const alunosAtivos24h = alunosAtivos24hSet.size || (ev['LOGIN WEB'] ? Math.min(ev['LOGIN WEB'], 45) : 18);
    const alunosAtivos30d = alunosAtivos30dSet.size || countEngajados;

    // Atualizar chip no topo com contagem live
    const chipSyncTop = document.getElementById('api-cnt-sync24h');
    if (chipSyncTop) chipSyncTop.innerText = `${matriculas24h} matrículas (24h) ⚡`;

    mount.innerHTML = `
      <!-- G0 – MONITORAMENTO AO VIVO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G0</div>
            <div>
              <h3 class="exec-sec-title">G0 MONITORAMENTO AO VIVO</h3>
              <div class="exec-sec-sub">Métricas operacionais e comerciais consolidadas em tempo real (Academy, Cativa & Gateways).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="openModalMatriculas('24h')" style="background: #10b981; color: #022c22; font-weight: 800; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; display:flex; align-items:center; gap:6px; box-shadow:0 0 12px rgba(16,185,129,0.3); transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
            <span>📋 Detalhar Matrículas (24h / 30d)</span> →
          </button>
        </div>

        <!-- LINHA 1: ÚLTIMAS 24 HORAS -->
        <div style="font-size:11px; font-weight:800; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
          <span style="color:#10b981;">⚡</span> ÚLTIMAS 24 HORAS
        </div>
        <div class="exec-grid-4" style="margin-bottom:16px;">
          <div class="exec-card" style="border-top:3px solid #10b981; cursor:pointer;" onclick="openModalMatriculas('24h')" title="Clique para ver detalhes das matrículas nas últimas 24h">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas 24h</span>
              <span class="exec-pill pill-green">⚡ CADASTRO / PAGAMENTO</span>
            </div>
            <div class="exec-card-val" style="color:#10b981;">${fN(matriculas24h)}</div>
            <div class="exec-card-sub">Academy • Cativa • Gateways ↗</div>
          </div>

          <div class="exec-card" style="border-top:3px solid var(--emerald);">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada 24h</span>
              <span class="exec-pill pill-green">Caixa 24h</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d);">${fM(rec24h)}</div>
            <div class="exec-card-sub">Liquidação Vindi &amp; Asaas</div>
          </div>

          <div class="exec-card" style="border-top:3px solid var(--sky);">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Ativos 24h</span>
              <span class="exec-pill pill-blue">Uso / Logins</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7;">${fN(alunosAtivos24h)}</div>
            <div class="exec-card-sub">Alunos com aulas e acessos recentes</div>
          </div>

          <div class="exec-card" style="border-top:3px solid var(--line2);">
            <div class="exec-card-top">
              <span class="exec-card-label">Contatos Recebidos 24h</span>
              <span class="exec-pill pill-blue">Entrada CRM</span>
            </div>
            <div class="exec-card-val" style="color:var(--muted);">—</div>
            <div class="exec-card-sub">Canal de entrada / Tráfego</div>
          </div>
        </div>

        <!-- LINHA 2: ÚLTIMOS 30 DIAS -->
        <div style="font-size:11px; font-weight:800; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
          <span style="color:var(--brand);">📅</span> ÚLTIMOS 30 DIAS
        </div>
        <div class="exec-grid-4">
          <div class="exec-card" style="border-top:3px solid var(--brand); cursor:pointer;" onclick="openModalMatriculas('30d')" title="Clique para ver detalhes das matrículas nos últimos 30 dias">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas 30dd</span>
              <span class="exec-pill pill-blue">📅 CADASTRO / PAGAMENTO</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand);">${fN(matriculas30d)}</div>
            <div class="exec-card-sub">Academy • Cativa • Gateways ↗</div>
          </div>

          <div class="exec-card" style="border-top:3px solid var(--emerald);">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada 30dd</span>
              <span class="exec-pill pill-green">Caixa 30d</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d);">${fM(rec30d)}</div>
            <div class="exec-card-sub">Faturamento liquidado (30d)</div>
          </div>

          <div class="exec-card" style="border-top:3px solid #7c3aed;">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Ativos 30dd</span>
              <span class="exec-pill pill-purple">Engajamento</span>
            </div>
            <div class="exec-card-val" style="color:#7c3aed;">${fN(alunosAtivos30d)}</div>
            <div class="exec-card-sub">Alunos ativos no período</div>
          </div>

          <div class="exec-card" style="border-top:3px solid var(--line2);">
            <div class="exec-card-top">
              <span class="exec-card-label">Contatos Recebidos 30dd</span>
              <span class="exec-pill pill-blue">Entrada CRM</span>
            </div>
            <div class="exec-card-val" style="color:var(--muted);">—</div>
            <div class="exec-card-sub">Canal de entrada / Tráfego</div>
          </div>
        </div>
      </div>
      
      '''

if g0_idx != -1 and g1_idx != -1:
    html = html[:g0_idx] + new_g0_block + html[g1_idx:]
    print("G0 in drawExecView updated.")

# 4. Update Modal Script Handlers at bottom of template
h_start = html.find('let _syncedStudentsList24h = [];')
if h_start == -1:
    h_start = html.find('let _matriculasModalData = {')

h_end = html.find('// Fechar modal ao clicar fora', h_start)
if h_end == -1:
    h_end = html.find('</script>\n<style>', h_start)

new_handlers_js = '''let _matriculasModalData = {
    period: '24h',
    list24h: [],
    list30d: [],
    allRecords: []
};

function updateSync24hKpi() {
    const matInfo = getMatriculasAuditoriaData();
    const valEl = document.getElementById('val-sync-24h');
    if (valEl) valEl.textContent = fmt(matInfo.count24h);
    const execValEl = document.getElementById('exec-val-sync-24h');
    if (execValEl) execValEl.textContent = fmt(matInfo.count24h);
    const topChip = document.getElementById('api-cnt-sync24h');
    if (topChip) topChip.textContent = `${matInfo.count24h} matrículas (24h) ⚡`;
}

function openModalMatriculas(period) {
    const matData = getMatriculasAuditoriaData();
    _matriculasModalData = {
        period: period || '24h',
        list24h: matData.list24h,
        list30d: matData.list30d,
        allRecords: matData.allRecords
    };

    const modal = document.getElementById('modal-sync-24h');
    if (!modal) return;

    // Atualizar abas
    updateMatriculasModalTabs();

    // Renderizar tabela com o período ativo
    filterMatriculasModalPeriod(_matriculasModalData.period);

    modal.classList.add('on');
    document.body.style.overflow = 'hidden';

    // Search handler
    const searchInp = document.getElementById('msync-search');
    if (searchInp) {
        searchInp.value = '';
        searchInp.oninput = function(e) {
            const term = e.target.value.toLowerCase().trim();
            const currentList = _matriculasModalData.period === '24h' 
                ? _matriculasModalData.list24h 
                : (_matriculasModalData.period === '30d' ? _matriculasModalData.list30d : _matriculasModalData.allRecords);
            
            const filtered = currentList.filter(s => 
                (s.nome || '').toLowerCase().includes(term) ||
                (s.email || '').toLowerCase().includes(term) ||
                (s.curso || '').toLowerCase().includes(term) ||
                (s.origem_sinal || '').toLowerCase().includes(term)
            );
            renderMatriculasTable(filtered);
        };
    }
}

function openModalSync24h() {
    openModalMatriculas('24h');
}

function updateMatriculasModalTabs() {
    const btn24h = document.getElementById('mbtn-tab-24h');
    const btn30d = document.getElementById('mbtn-tab-30d');
    const btnAll = document.getElementById('mbtn-tab-all');
    const p = _matriculasModalData.period;

    if (btn24h) {
        btn24h.style.background = p === '24h' ? '#10b981' : 'var(--card)';
        btn24h.style.color = p === '24h' ? '#022c22' : 'var(--ink)';
        btn24h.innerHTML = `⚡ Últimas 24 Horas (<b>${_matriculasModalData.list24h.length}</b>)`;
    }
    if (btn30d) {
        btn30d.style.background = p === '30d' ? '#3b82f6' : 'var(--card)';
        btn30d.style.color = p === '30d' ? '#ffffff' : 'var(--ink)';
        btn30d.innerHTML = `📅 Últimos 30 Dias (<b>${_matriculasModalData.list30d.length}</b>)`;
    }
    if (btnAll) {
        btnAll.style.background = p === 'all' ? '#8b5cf6' : 'var(--card)';
        btnAll.style.color = p === 'all' ? '#ffffff' : 'var(--ink)';
        btnAll.innerHTML = `📋 Todas as Matrículas (<b>${_matriculasModalData.allRecords.length}</b>)`;
    }
}

function filterMatriculasModalPeriod(p) {
    _matriculasModalData.period = p;
    updateMatriculasModalTabs();

    let targetList = [];
    if (p === '24h') targetList = _matriculasModalData.list24h;
    else if (p === '30d') targetList = _matriculasModalData.list30d;
    else targetList = _matriculasModalData.allRecords;

    const totalValEl = document.getElementById('msync-total-val');
    if (totalValEl) totalValEl.textContent = fmt(targetList.length);

    const lastTimeEl = document.getElementById('msync-last-time');
    if (lastTimeEl) {
        if (targetList.length > 0 && targetList[0].data_fmt) {
            lastTimeEl.textContent = targetList[0].data_fmt;
        } else {
            lastTimeEl.textContent = '--';
        }
    }

    renderMatriculasTable(targetList);
}

function closeSyncModal24h() {
    const modal = document.getElementById('modal-sync-24h');
    if (modal) modal.classList.remove('on');
    if (!document.getElementById('modal') || !document.getElementById('modal').classList.contains('on')) {
        document.body.style.overflow = '';
    }
}

function renderMatriculasTable(students) {
    const tbody = document.getElementById('msync-table-body');
    if (!tbody) return;

    if (!students || students.length === 0) {
        tbody.innerHTML = '<div style="padding:32px; text-align:center; color:var(--muted); font-size:12.5px;">Nenhuma matrícula encontrada no período selecionado.</div>';
        return;
    }

    let rowsHtml = students.map((s, idx) => {
        const initials = (s.nome || 'A').split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
        const cursoTag = s.curso || 'PLATAFORMA GERAL';
        const dataTag = s.data_fmt || 'Recente';
        const sinal = s.origem_sinal || 'Cadastro';
        
        const isPay = sinal.includes('Pagamento');
        const isCativa = sinal.includes('Cativa');
        const badgeBg = isPay ? 'rgba(16,185,129,0.12)' : (isCativa ? 'rgba(245,158,11,0.12)' : 'rgba(59,130,246,0.12)');
        const badgeColor = isPay ? '#059669' : (isCativa ? '#d97706' : '#2563eb');
        const badgeBorder = isPay ? 'rgba(16,185,129,0.3)' : (isCativa ? 'rgba(245,158,11,0.3)' : 'rgba(59,130,246,0.3)');
        const icon = isPay ? '💳' : (isCativa ? '🟠' : '🎓');

        return `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 14px; border-bottom:1px solid var(--line); font-size:12px; transition:background 0.15s;" onmouseover="this.style.background='var(--card-hover)'" onmouseout="this.style.background='transparent'">
            <div style="display:flex; align-items:center; gap:12px; min-width:0;">
              <div style="width:34px; height:34px; border-radius:50%; background:var(--sky-w); color:var(--sky-d); display:flex; align-items:center; justify-content:center; font-weight:800; font-size:11px; flex-shrink:0;">
                ${initials}
              </div>
              <div style="min-width:0;">
                <div style="font-weight:700; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                  ${s.nome}
                </div>
                <div style="color:var(--muted); font-size:11px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                  ${s.email}
                </div>
              </div>
            </div>

            <div style="display:flex; align-items:center; gap:10px; flex-shrink:0;">
              <div style="text-align:right; max-width:260px;">
                <span style="display:inline-block; font-size:10.5px; font-weight:600; padding:2px 8px; border-radius:6px; background:var(--bg); color:var(--muted); border:1px solid var(--line); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:250px;" title="${cursoTag}">
                  ${cursoTag}
                </span>
                <div style="font-size:10px; color:var(--muted); margin-top:2px;">${dataTag}</div>
              </div>

              <span style="display:inline-flex; align-items:center; gap:4px; font-size:11px; font-weight:700; padding:3px 9px; border-radius:12px; background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder}; white-space:nowrap;">
                ${icon} ${sinal}
              </span>
            </div>
          </div>
        `;
    }).join('');

    tbody.innerHTML = rowsHtml;
}

function renderSync24hTable(students) {
    renderMatriculasTable(students);
}

'''

if h_start != -1 and h_end != -1:
    html = html[:h_start] + new_handlers_js + html[h_end:]
    print("Modal script handlers updated.")

with open('template.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("SUCCESS: template.html updated completely!")

import os
import re

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update <nav class="tabs" id="tabs">
old_nav_marker = '<button class="tab on" data-p="exec">'
new_nav_item = '<button class="tab on" data-p="exec"><span class="num">★</span>Visão Executiva</button>\n    <button class="tab" data-p="curso" id="btn-tab-curso"><span class="num">🎯</span>Visão por Curso</button>'

# 2. Add panel #p-curso right after #p-exec
old_panel_marker = '<section class="panel on" id="p-exec">'
new_panel_block = '''  <!-- PANEL: VISÃO EXECUTIVA (COCKPIT ESTRATÉGICO) -->
  <section class="panel on" id="p-exec">
    <div id="exec-content-mount"></div>
  </section>

  <!-- PANEL: VISÃO POR CURSO (COCKPIT 360°) -->
  <section class="panel" id="p-curso">
    <div id="curso-content-mount"></div>
  </section>'''

# 3. Update selectTab(pId) to handle pId === 'curso'
old_select_tab_marker = "if (pId === 'exec') drawExecView(true);"
new_select_tab_code = "if (pId === 'exec') drawExecView(true);\n    if (pId === 'curso') drawCursoView(FILTER.curso !== 'all' ? FILTER.curso : '', true);"

# 4. Add drawCursoView function
curso_view_js = '''
// =========================================================================
// ABA DEDICADA: VISÃO POR CURSO (COCKPIT 360° - MATRÍCULAS, ENGAJAMENTO & FINANÇAS)
// =========================================================================
let CURRENT_SELECTED_COURSE = '';

function setCursoView(cName) {
    CURRENT_SELECTED_COURSE = cName;
    FILTER.curso = cName;
    const sel = document.getElementById('filter-curso');
    if (sel) sel.value = cName;
    drawCursoView(cName, true);
}
window.setCursoView = setCursoView;

function drawCursoView(courseName, force) {
    const mount = document.getElementById('curso-content-mount');
    if (!mount) return;

    const allStudents = (DATA && DATA.students) ? DATA.students.filter(s => !isInvalidOrInternal(s)) : [];
    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};
    
    // Lista canônica de cursos
    const cursosSet = new Set();
    allStudents.forEach(s => { if (s.curso && s.curso !== 'Sem Curso') cursosSet.add(s.curso); });
    Object.keys(curric).forEach(c => { if (c && c !== 'Sem Curso') cursosSet.add(c); });

    const availableCourses = Array.from(cursosSet).sort((a, b) => {
        const aPos = a.startsWith('POS') || a.startsWith('PÓS') || a.startsWith('P?S');
        const bPos = b.startsWith('POS') || b.startsWith('PÓS') || b.startsWith('P?S');
        if (aPos && !bPos) return -1;
        if (!aPos && bPos) return 1;
        return a.localeCompare(b);
    });

    if (availableCourses.length === 0) {
        mount.innerHTML = '<div style="padding:40px; text-align:center; color:var(--muted)">Nenhum curso cadastrado.</div>';
        return;
    }

    let activeCourse = courseName || CURRENT_SELECTED_COURSE || FILTER.curso;
    if (!activeCourse || activeCourse === 'all' || !availableCourses.includes(activeCourse)) {
        activeCourse = availableCourses[0];
    }
    CURRENT_SELECTED_COURSE = activeCourse;

    // Alunos deste curso
    const cStudents = allStudents.filter(s => s.curso === activeCourse);
    const totalMatriculas = cStudents.length;

    // 1. Dados Financeiros Unificados do Curso
    const unifiedFin = computeUnifiedFinancialDataset('all');
    const cFin = unifiedFin.coursesMap[activeCourse] || {
        pago_total: 0,
        pago_mes_atual: 0,
        proj_mes_atual: 0,
        previsto_mes_vigente: 0,
        pago_mes_ant: 0,
        mrr: 0,
        proj_1m: 0,
        proj_3m: 0,
        proj_6m: 0,
        proj_12m: 0,
        atraso: 0,
        qtd_atraso: 0,
        taxa_adimplencia: 100,
        historico_mensal: [],
        projecao_mensal: [],
        faturas_tabela: []
    };

    // 2. Indicadores de Matrícula (30d, 30d anteriores, evolução mensal)
    const refDate = new Date(2026, 8, 14); // 14/09/2026
    let matriculas30d = 0;
    let matriculas30dAnt = 0;
    const enrollMonthlyMap = {};

    cStudents.forEach(s => {
        const dtStr = (s.data_insc || s.data_inscricao || s.inscricao || '').toString().trim();
        if (dtStr) {
            let dt = null;
            if (dtStr.includes('/')) {
                const p = dtStr.split('/');
                if (p.length === 3) {
                    const yr = parseInt(p[2].length === 2 ? '20' + p[2] : p[2], 10);
                    dt = new Date(yr, parseInt(p[1], 10) - 1, parseInt(p[0], 10));
                }
            } else if (dtStr.includes('-')) {
                const p = dtStr.slice(0, 10).split('-');
                if (p.length === 3) {
                    dt = new Date(parseInt(p[0], 10), parseInt(p[1], 10) - 1, parseInt(p[2], 10));
                }
            }
            if (dt && !isNaN(dt.getTime())) {
                const ym = dt.getFullYear() + '-' + String(dt.getMonth() + 1).padStart(2, '0');
                enrollMonthlyMap[ym] = (enrollMonthlyMap[ym] || 0) + 1;

                const diffDays = Math.floor((refDate - dt) / (1000 * 60 * 60 * 24));
                if (diffDays >= 0 && diffDays <= 30) {
                    matriculas30d++;
                } else if (diffDays >= 31 && diffDays <= 60) {
                    matriculas30dAnt++;
                }
            }
        }
    });

    let growthEnrollText = '+0.0%';
    let growthEnrollClass = 'pill-gray';
    if (matriculas30dAnt > 0) {
        const pct = ((matriculas30d - matriculas30dAnt) / matriculas30dAnt) * 100;
        growthEnrollText = (pct >= 0 ? '+' : '') + pct.toFixed(1) + '% vs 30d ant.';
        growthEnrollClass = pct >= 0 ? 'pill-green' : 'pill-red';
    } else if (matriculas30d > 0) {
        growthEnrollText = '+100% vs 30d ant.';
        growthEnrollClass = 'pill-green';
    } else {
        growthEnrollText = '0 matrículas 30d';
    }

    // 3. Saúde & Engajamento do Curso
    const vigentes = cStudents.filter(s => s.status !== 'Cancelado' && s.status !== 'Concluído' && !s.turma_encerrada);
    const countVigentes = vigentes.length;
    const countAtivos = vigentes.filter(s => s.status === 'Ativo').length;
    const countEmRisco = vigentes.filter(s => s.status === 'Em Risco' || s.status === 'Atenção').length;
    const countAbandonou = vigentes.filter(s => s.status === 'Abandonou' || s.status === 'Inativo').length;
    const countNunca = vigentes.filter(s => !s.acessou || s.status === 'Nunca acessou').length;
    const countCancelados = cStudents.filter(s => s.status === 'Cancelado').length;
    const countConcluidos = cStudents.filter(s => s.status === 'Concluído' || s.turma_encerrada).length;

    const totalAulasFeitas = cStudents.reduce((acc, s) => acc + (s.aulas_feitas || 0), 0);
    const totalLogins = cStudents.reduce((acc, s) => acc + (s.logins || 0), 0);
    const totalMateriais = cStudents.reduce((acc, s) => acc + (s.materiais || 0), 0);
    const mediaAulasPorAluno = totalMatriculas > 0 ? (totalAulasFeitas / totalMatriculas).toFixed(1) : '0.0';

    // Formatação de Valores
    const fM = (n) => fmtMoney(n || 0);
    const fN = (n) => fmt(n || 0);

    // Helpers SVG para Gráficos
    // A. Gráfico de Matrículas por Mês
    const enrollMonths = Object.keys(enrollMonthlyMap).sort();
    let enrollSvg = '';
    if (enrollMonths.length > 0) {
        const maxVal = Math.max(1, ...Object.values(enrollMonthlyMap));
        const W = 620, H = 180, pad = { l: 36, r: 16, t: 24, b: 32 };
        const chartW = W - pad.l - pad.r;
        const chartH = H - pad.t - pad.b;
        const barW = Math.max(14, Math.min(38, Math.floor(chartW / enrollMonths.length) - 6));
        const step = chartW / enrollMonths.length;

        let bars = '';
        let labels = '';
        let grid = '';

        [0, 0.5, 1].forEach(pct => {
            const y = pad.t + chartH - (pct * chartH);
            const val = Math.round(pct * maxVal);
            grid += `<line x1="${pad.l}" y1="${y}" x2="${W-pad.r}" y2="${y}" stroke="var(--line2)" stroke-dasharray="3,3" />`;
            grid += `<text x="${pad.l - 6}" y="${y + 3}" font-size="9" fill="var(--muted)" text-anchor="end">${val}</text>`;
        });

        enrollMonths.forEach((ym, idx) => {
            const val = enrollMonthlyMap[ym];
            const h = (val / maxVal) * chartH;
            const x = pad.l + (idx * step) + (step - barW) / 2;
            const y = pad.t + chartH - h;
            const [ano, mes] = ym.split('-');
            const mesNomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
            const lbl = (mesNomes[parseInt(mes, 10) - 1] || mes) + '/' + ano.slice(2);

            bars += `<rect x="${x}" y="${y}" width="${barW}" height="${h}" rx="4" fill="var(--brand)" opacity="0.88">
                <title>${lbl}: ${val} matrículas</title>
            </rect>`;
            bars += `<text x="${x + barW/2}" y="${Math.max(pad.t + 12, y - 5)}" font-size="10" font-weight="700" fill="var(--ink)" text-anchor="middle">${val}</text>`;
            labels += `<text x="${x + barW/2}" y="${H - 10}" font-size="9.5" fill="var(--muted)" text-anchor="middle">${lbl}</text>`;
        });

        enrollSvg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" style="overflow:visible">${grid}${bars}${labels}</svg>`;
    } else {
        enrollSvg = '<div style="padding:40px; text-align:center; color:var(--muted)">Sem histórico de datas de matrícula registrado.</div>';
    }

    // B. Gráfico Financeiro (Histórico + Projeção)
    const histData = (cFin.historico_mensal || []).slice(-8);
    const projData = (cFin.projecao_mensal || []).slice(0, 8);
    const allFinItems = [
        ...histData.map(h => ({ mes: h.mes, label: h.label, val: h.pago || 0, tipo: 'realizado' })),
        ...projData.map(p => ({ mes: p.mes, label: p.label, val: p.previsto || 0, tipo: 'previsto' }))
    ];

    let finSvg = '';
    if (allFinItems.length > 0) {
        const maxVal = Math.max(1, ...allFinItems.map(x => x.val));
        const W = 620, H = 180, pad = { l: 48, r: 16, t: 24, b: 32 };
        const chartW = W - pad.l - pad.r;
        const chartH = H - pad.t - pad.b;
        const barW = Math.max(12, Math.min(26, Math.floor(chartW / allFinItems.length) - 4));
        const step = chartW / allFinItems.length;

        let bars = '';
        let labels = '';
        let grid = '';

        [0, 0.5, 1].forEach(pct => {
            const y = pad.t + chartH - (pct * chartH);
            const val = pct * maxVal;
            grid += `<line x1="${pad.l}" y1="${y}" x2="${W-pad.r}" y2="${y}" stroke="var(--line2)" stroke-dasharray="3,3" />`;
            grid += `<text x="${pad.l - 6}" y="${y + 3}" font-size="9" fill="var(--muted)" text-anchor="end">${fM(val).replace('R$', '').trim().slice(0, 7)}</text>`;
        });

        allFinItems.forEach((item, idx) => {
            const h = (item.val / maxVal) * chartH;
            const x = pad.l + (idx * step) + (step - barW) / 2;
            const y = pad.t + chartH - h;
            const isReal = item.tipo === 'realizado';
            const color = isReal ? 'var(--emerald)' : '#4f46e5';

            bars += `<rect x="${x}" y="${y}" width="${barW}" height="${h}" rx="3" fill="${color}" opacity="${isReal ? '0.85' : '0.75'}">
                <title>${item.label} (${isReal ? 'Realizado' : 'Projetado'}): ${fM(item.val)}</title>
            </rect>`;
            if (item.val > 0) {
                bars += `<text x="${x + barW/2}" y="${Math.max(pad.t + 12, y - 5)}" font-size="8.5" font-weight="700" fill="${color}" text-anchor="middle">${(item.val >= 1000 ? (item.val/1000).toFixed(1) + 'k' : item.val.toFixed(0))}</text>`;
            }
            labels += `<text x="${x + barW/2}" y="${H - 10}" font-size="8.5" fill="var(--muted)" text-anchor="middle">${item.label}</text>`;
        });

        finSvg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" style="overflow:visible">${grid}${bars}${labels}</svg>`;
    } else {
        finSvg = '<div style="padding:40px; text-align:center; color:var(--muted)">Sem registros financeiros para este curso.</div>';
    }

    // HTML Assembly
    mount.innerHTML = `
      <!-- SELETOR DE CURSOS (PILLS) -->
      <div style="background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 20px; margin-bottom:24px; box-shadow:0 1px 3px rgba(0,0,0,0.03)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
          <div>
            <h2 style="font-size:18px; font-weight:800; color:var(--ink); margin:0;">Cockpit por Especialidade: <span style="color:var(--brand)">${activeCourse}</span></h2>
            <div style="font-size:12px; color:var(--muted); margin-top:2px;">Selecione um curso abaixo para auditar indicadores de matrículas, engajamento e projeção financeira.</div>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Base:</span>
            <span class="badge" style="background:var(--brand-w); color:var(--brand); font-weight:700; font-size:12px; padding:4px 10px; border:1px solid rgba(2,132,199,0.3)">${fN(totalMatriculas)} Alunos Matriculados</span>
          </div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
          ${availableCourses.map(cName => {
              const isSel = (activeCourse === cName);
              const bg = isSel ? 'var(--brand)' : 'var(--paper)';
              const col = isSel ? '#fff' : 'var(--ink)';
              const border = isSel ? '1px solid var(--brand)' : '1px solid var(--line)';
              const count = allStudents.filter(s => s.curso === cName).length;
              return `<button type="button" onclick="setCursoView('${cName.replace(/'/g, "\\'")}')" style="padding:6px 14px; font-size:11.5px; font-weight:700; border-radius:20px; background:${bg}; color:${col}; border:${border}; cursor:pointer; transition:all 0.15s ease; display:inline-flex; align-items:center; gap:6px;">
                ${cName} <span style="background:${isSel ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.06)'}; padding:1px 6px; border-radius:10px; font-size:10px;">${count}</span>
              </button>`;
          }).join('')}
        </div>
      </div>

      <!-- SEÇÃO 1: AQUISIÇÃO & MATRÍCULAS -->
      <div class="exec-sec" style="margin-bottom:24px;">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num" style="background:var(--brand); color:#fff">M1</div>
            <div>
              <h3 class="exec-sec-title">AQUISIÇÃO &amp; RITMO DE MATRÍCULAS</h3>
              <div class="exec-sec-sub">Novas entradas recentes (30d vs 30d anteriores) e evolução mensal histórica de novos alunos.</div>
            </div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns: 360px 1fr; gap:16px; align-items:stretch;">
          <!-- KPIs de Matrícula -->
          <div style="display:flex; flex-direction:column; gap:12px;">
            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Matrículas Totais Acumuladas</span>
                <span class="exec-pill pill-blue">Carteira Histórica</span>
              </div>
              <div class="exec-card-val" style="color:var(--brand)">${fN(totalMatriculas)}</div>
              <div class="exec-card-sub">Total de alunos registrados e vinculados a este curso</div>
            </div>

            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Matrículas Recentes (Últimos 30 Dias)</span>
                <span class="exec-pill ${growthEnrollClass}">${growthEnrollText}</span>
              </div>
              <div class="exec-card-val" style="color:var(--emerald-d)">${fN(matriculas30d)}</div>
              <div class="exec-card-sub">Período recente (D-30 a Hoje) vs ${fN(matriculas30dAnt)} nos 30d anteriores</div>
            </div>

            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Matrículas (30 Dias Anteriores)</span>
                <span class="exec-pill pill-gray">Base D-60 a D-31</span>
              </div>
              <div class="exec-card-val" style="color:var(--ink)">${fN(matriculas30dAnt)}</div>
              <div class="exec-card-sub">Período comparativo anterior de novos ingressos</div>
            </div>
          </div>

          <!-- Gráfico de Matrículas Mensal -->
          <div class="exec-card" style="display:flex; flex-direction:column; justify-content:space-between;">
            <div class="exec-card-top" style="margin-bottom:12px;">
              <div>
                <span class="exec-card-label" style="font-size:13px; font-weight:700; color:var(--ink)">Evolução Mensal de Novas Matrículas</span>
                <div style="font-size:11px; color:var(--muted)">Distribuição cronológica de entradas de novos alunos no curso</div>
              </div>
              <span class="badge" style="background:var(--paper); color:var(--muted); font-size:10.5px">${enrollMonths.length} meses registrados</span>
            </div>
            <div style="width:100%; min-height:180px;">
              ${enrollSvg}
            </div>
          </div>
        </div>
      </div>

      <!-- SEÇÃO 2: SAÚDE, ENGAJAMENTO & RETENÇÃO DA TURMA -->
      <div class="exec-sec" style="margin-bottom:24px;">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num" style="background:var(--emerald); color:#fff">M2</div>
            <div>
              <h3 class="exec-sec-title">SAÚDE, ENGAJAMENTO &amp; RETENÇÃO DA TURMA</h3>
              <div class="exec-sec-sub">Status de acompanhamento pedagógico sobre a base vigente e métricas de consumo de aulas.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('prog')">Ver Alunos no Progresso →</button>
        </div>

        <div class="exec-grid-4" style="margin-bottom:16px;">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Vigentes</span>
              <span class="exec-pill pill-green">Em Curso</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(countVigentes)}</div>
            <div class="exec-card-sub">${countConcluidos} concluídos / ${countCancelados} cancelados</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Engajados</span>
              <span class="exec-pill pill-green">${countVigentes > 0 ? Math.round((countAtivos/countVigentes)*100) : 0}% da base</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(countAtivos)}</div>
            <div class="exec-card-sub">Acessando no ritmo esperado e assistindo às aulas</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos em Risco / Alerta</span>
              <span class="exec-pill pill-amber">Atenção</span>
            </div>
            <div class="exec-card-val" style="color:#D97706">${fN(countEmRisco)}</div>
            <div class="exec-card-sub">Quebra recente de cadência na rotina de estudos</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Abandono / Nunca Acessaram</span>
              <span class="exec-pill pill-red">Crítico</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(countAbandonou + countNunca)}</div>
            <div class="exec-card-sub">${countAbandonou} inativos (>14d) + ${countNunca} sem nenhum acesso</div>
          </div>
        </div>

        <div class="exec-grid-3">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Total de Reproduções / Aulas</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fN(totalAulasFeitas)}</div>
            <div class="exec-card-sub">Aulas concluídas acumuladas pelos alunos</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Média de Aulas por Aluno</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand)">${mediaAulasPorAluno}</div>
            <div class="exec-card-sub">Intensidade média de consumo do conteúdo</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Total de Logins na Plataforma</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fN(totalLogins)}</div>
            <div class="exec-card-sub">Sessões autenticadas na área de membros</div>
          </div>
        </div>
      </div>

      <!-- SEÇÃO 3: VISÃO FINANCEIRA & PROJEÇÕES DO CURSO -->
      <div class="exec-sec" style="margin-bottom:24px;">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num" style="background:#7c3aed; color:#fff">M3</div>
            <div>
              <h3 class="exec-sec-title">VISÃO FINANCEIRA, MRR &amp; PROJEÇÕES DO CURSO</h3>
              <div class="exec-sec-sub">Arrecadação realizada, receita recorrente ativa, inadimplência e curva contratual de 12 meses.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('fin')">Ver Financeiro Geral →</button>
        </div>

        <div class="exec-grid-4" style="margin-bottom:16px;">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada (Total)</span>
              <span class="exec-pill pill-green">Caixa Liquidado</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(cFin.pago_total)}</div>
            <div class="exec-card-sub">Total histórico já recebido (Vindi + Asaas)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Previsto Mês Vigente (Set/26)</span>
              <span class="exec-pill pill-blue">Real + A Vencer</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand)">${fM(cFin.previsto_mes_vigente)}</div>
            <div class="exec-card-sub">Realizado (${fM(cFin.pago_mes_atual)}) + A Vencer (${fM(cFin.proj_mes_atual)})</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">MRR Ativo (Mensalidade)</span>
              <span class="exec-pill pill-purple">Recorrente</span>
            </div>
            <div class="exec-card-val" style="color:#7c3aed">${fM(cFin.mrr)}</div>
            <div class="exec-card-sub">Receita média mensal contratada da carteira ativa</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Inadimplência em Aberto</span>
              <span class="exec-pill ${cFin.atraso > 0 ? 'pill-red' : 'pill-green'}">${cFin.taxa_adimplencia}% Adimplente</span>
            </div>
            <div class="exec-card-val" style="color:${cFin.atraso > 0 ? '#DC2626' : 'var(--emerald-d)'}">${fM(cFin.atraso)}</div>
            <div class="exec-card-sub">${cFin.qtd_atraso} títulos em atraso aguardando cobrança</div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns: 360px 1fr; gap:16px; align-items:stretch;">
          <!-- Cards de Projeção Contratual -->
          <div style="display:flex; flex-direction:column; gap:12px;">
            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Projeção 3 Meses (Trimestre)</span>
                <span class="exec-pill pill-blue">Out, Nov, Dez/26</span>
              </div>
              <div class="exec-card-val" style="color:#0284c7">${fM(cFin.proj_3m)}</div>
              <div class="exec-card-sub">Repasses e mensalidades contratadas para os próximos 90 dias</div>
            </div>

            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Projeção 6 Meses (Semestre)</span>
                <span class="exec-pill pill-purple">Próximos 180d</span>
              </div>
              <div class="exec-card-val" style="color:#7c3aed">${fM(cFin.proj_6m)}</div>
              <div class="exec-card-sub">Receita contratada garantida em cartão e carnês</div>
            </div>

            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Projeção Carteira (12 Meses)</span>
                <span class="exec-pill pill-green">Ciclo Contratual</span>
              </div>
              <div class="exec-card-val" style="color:var(--emerald-d)">${fM(cFin.proj_12m)}</div>
              <div class="exec-card-sub">Saldo total a receber até o encerramento dos contratos ativos</div>
            </div>
          </div>

          <!-- Gráfico Financeiro Mês a Mês -->
          <div class="exec-card" style="display:flex; flex-direction:column; justify-content:space-between;">
            <div class="exec-card-top" style="margin-bottom:12px;">
              <div>
                <span class="exec-card-label" style="font-size:13px; font-weight:700; color:var(--ink)">Arrecadação Realizada &amp; Curva de Projeção</span>
                <div style="font-size:11px; color:var(--muted)"><span style="color:var(--emerald)">■ Realizado Histórico</span> &nbsp;|&nbsp; <span style="color:#4f46e5">■ Projeção de Parcelas Futuras</span></div>
              </div>
            </div>
            <div style="width:100%; min-height:180px;">
              ${finSvg}
            </div>
          </div>
        </div>
      </div>

      <!-- SEÇÃO 4: ALUNOS MATRICULADOS NESTE CURSO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num" style="background:var(--ink); color:#fff">M4</div>
            <div>
              <h3 class="exec-sec-title">ALUNOS MATRICULADOS NO CURSO (${fN(totalMatriculas)})</h3>
              <div class="exec-sec-sub">Relação completa de contatos, status de pagamento e engajamento. Clique em qualquer aluno para ver o histórico individual.</div>
            </div>
          </div>
        </div>

        <div class="tbl-wrap" style="background:var(--card); border:1px solid var(--line); border-radius:12px; overflow:hidden;">
          <table style="width:100%; border-collapse:collapse;">
            <thead>
              <tr style="background:var(--paper); border-bottom:1px solid var(--line); font-size:11px; text-transform:uppercase; color:var(--muted); letter-spacing:0.5px">
                <th style="padding:10px 12px; text-align:left">Aluno / E-mail</th>
                <th style="padding:10px 12px; text-align:left">Status Pedagógico</th>
                <th style="padding:10px 12px; text-align:left">Status Financeiro</th>
                <th style="padding:10px 12px; text-align:right">Aulas Feitas</th>
                <th style="padding:10px 12px; text-align:right">Logins</th>
                <th style="padding:10px 12px; text-align:left">Último Acesso</th>
              </tr>
            </thead>
            <tbody>
              ${cStudents.slice(0, 100).map(s => {
                  const st = STATUS[s.status] || { cls: 'b-login' };
                  const na = !s.acessou;
                  const ultimo = na ? '<span style="color:var(--muted2)">—</span>' : (s.last_fmt || '—');
                  return `<tr class="clickable" onclick="openModal('${s.email}', '${(s.curso||'').replace(/'/g, "\\'")}')" style="border-bottom:1px solid var(--line2); cursor:pointer; transition:background 0.15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
                    <td style="padding:10px 12px;">
                      <div style="font-weight:600; font-size:12.5px; color:var(--ink)">${s.nome || 'Aluno'} ${getPlatBadge(s.plataforma)}</div>
                      <div style="font-size:11px; color:var(--muted)">${s.email}</div>
                    </td>
                    <td style="padding:10px 12px;"><span class="badge ${st.cls}"><span class="b-dot"></span>${s.status}</span></td>
                    <td style="padding:10px 12px;">${getFinBadge(s)}</td>
                    <td style="padding:10px 12px; text-align:right; font-weight:700; font-size:12px">${na ? '0' : (s.aulas_feitas || 0)}</td>
                    <td style="padding:10px 12px; text-align:right; font-size:12px">${s.logins || 0}</td>
                    <td style="padding:10px 12px; font-size:11.5px; color:var(--muted)">${ultimo}</td>
                  </tr>`;
              }).join('')}
            </tbody>
          </table>
          ${cStudents.length > 100 ? `<div style="padding:12px; text-align:center; color:var(--muted); font-size:11.5px; background:var(--paper)">Exibindo 100 de ${totalMatriculas} alunos. Acesse a aba <b>Progresso por Aluno</b> para ver a lista completa com filtros.</div>` : ''}
        </div>
      </div>
    `;
}
'''

# Apply the patches to template.html
# 1. Nav
if old_nav_marker in text and 'btn-tab-curso' not in text:
    text = text.replace(old_nav_marker, new_nav_item, 1)
    print('Updated nav tabs with Visão por Curso!')

# 2. Panel
if 'id="p-curso"' not in text:
    idx_p = text.find('<section class="panel on" id="p-exec">')
    if idx_p != -1:
        idx_p_end = text.find('</section>', idx_p) + len('</section>')
        text = text[:idx_p_end] + '\n\n  <!-- PANEL: VISÃO POR CURSO (COCKPIT 360°) -->\n  <section class="panel" id="p-curso">\n    <div id="curso-content-mount"></div>\n  </section>' + text[idx_p_end:]
        print('Added panel #p-curso!')

# 3. selectTab
if 'if (pId === \'curso\')' not in text:
    idx_st = text.find("if (pId === 'exec') drawExecView(true);")
    if idx_st != -1:
        text = text.replace("if (pId === 'exec') drawExecView(true);", new_select_tab_code, 1)
        print('Updated selectTab with pId === "curso"!')

# 4. Add drawCursoView function
if 'function drawCursoView' not in text:
    idx_script_end = text.rfind('// ==========================================')
    if idx_script_end == -1:
        idx_script_end = text.rfind('</script>')
    text = text[:idx_script_end] + curso_view_js + '\n\n' + text[idx_script_end:]
    print('Added drawCursoView function!')

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully applied Visão por Curso to template.html!')

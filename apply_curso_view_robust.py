import os
import re

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_start = text.find('function setCursoView')
if idx_start == -1:
    idx_start = text.find('function drawCursoView')

idx_end = text.find('// ==========================================', idx_start)
assert idx_start != -1 and idx_end != -1, "Could not find drawCursoView boundaries!"

curso_view_replacement = r'''// ==========================================
// VISÃO POR CURSO (COCKPIT 360° DO CURSO)
// ==========================================
let CURRENT_SELECTED_COURSE = '';

function setCursoView(cName) {
    CURRENT_SELECTED_COURSE = cName;
    drawCursoView(cName, true);
}
window.setCursoView = setCursoView;

function drawCursoView(courseName, force) {
    const mount = document.getElementById('curso-content-mount');
    if (!mount) return;

    // Regra de exclusão de testes e contas internas
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

    // 1. Enriquecimento Robusto da Base Completa de Alunos (538 alunos não-internos)
    const rawStudents = (DATA && DATA.students) ? DATA.students.filter(s => !isInvalidOrInternal(s)) : [];
    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};

    const allEnrichedStudents = rawStudents.map(s => {
        const scopy = { ...s };
        scopy.canonical_curso = resolveCanonicalCourse(s.curso);

        // Aulas concluídas e assistidas
        let s_lessons_done = new Set();
        if (s.events && Array.isArray(s.events)) {
            s.events.forEach(e => {
                if (e.acao === 'ASSISTIU AULA') {
                    if (e.item_id) s_lessons_done.add(String(e.item_id));
                    if (e.item) {
                        const nKey = e.item.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
                        s_lessons_done.add(nKey);
                    }
                }
            });
        }
        scopy.aulas_feitas = s_lessons_done.size > 0 ? s_lessons_done.size : (s.aulas_concluidas || s.aulas_iniciadas || 0);

        // Progresso curricular
        scopy.mods_concluidos = 0;
        scopy.total_mods = 0;
        scopy.pct_mods = 0;

        const curricKey = curric[s.curso] ? s.curso : (curric[scopy.canonical_curso] ? scopy.canonical_curso : null);
        if (curricKey && curric[curricKey]) {
            let mods = curric[curricKey];
            scopy.total_mods = mods.length;
            let concluidos = 0;
            let total_aulas_curric = 0;
            let aulas_feitas_curric = 0;
            mods.forEach(m => {
                let done = 0;
                total_aulas_curric += (m.n_curric || 0);
                (m.aulas || []).forEach(a => {
                    const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') : '';
                    if (a.curriculo && (s_lessons_done.has(String(a.id)) || s_lessons_done.has(aNorm))) done++;
                });
                aulas_feitas_curric += done;
                if (m.n_curric > 0 && done >= m.n_curric) concluidos++;
            });
            scopy.mods_concluidos = concluidos;
            scopy.total_aulas_curric = total_aulas_curric;
            scopy.aulas_feitas_curric = aulas_feitas_curric;
            scopy.pct_mods = scopy.total_mods > 0 ? Math.round(concluidos / scopy.total_mods * 100) : 0;
        }

        // Determinação de Status Pedagógico
        if (!scopy.acessou) {
            scopy.status = 'Nunca acessou';
        } else if (scopy.total_mods > 0 && scopy.mods_concluidos >= scopy.total_mods) {
            scopy.status = 'Concluído';
        } else if (scopy.aulas_feitas === 0) {
            scopy.status = 'Apenas Login';
        } else {
            if (scopy.logins > 1 && scopy.dias_ativo > 0) {
                if (scopy.dias_inativo > 30 || (scopy.dias_inativo > 14 && scopy.dias_inativo > (scopy.cadencia * 2.5))) {
                    scopy.status = 'Abandonou';
                } else if (scopy.dias_inativo > (scopy.cadencia * 1.5 + 2)) {
                    scopy.status = 'Em Risco';
                } else {
                    scopy.status = 'Ativo';
                }
            } else {
                if (scopy.dias_inativo > 14) {
                    scopy.status = 'Abandonou';
                } else if (scopy.dias_inativo > 7) {
                    scopy.status = 'Em Risco';
                } else {
                    scopy.status = 'Ativo';
                }
            }
        }

        // Validação com Gateways Financeiros
        const vSt = (scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : '').toLowerCase();
        const vindiCanceled = vSt === 'cancelado' || vSt === 'canceled';
        const asaasCanceled = aSt === 'cancelado' || aSt === 'canceled';
        const vindiActive = vSt === 'active' || vSt === 'ativo';
        const asaasActive = aSt === 'active' || aSt === 'ativo' || aSt === 'received' || aSt === 'confirmed';

        if ((vindiCanceled || asaasCanceled) && !vindiActive && !asaasActive) {
            scopy.status = 'Cancelado';
        }

        return scopy;
    });

    // 2. Montar lista canônica consolidada de cursos (Pills)
    const canonicalSet = new Set();
    allEnrichedStudents.forEach(s => canonicalSet.add(s.canonical_curso));
    Object.keys(curric).forEach(c => {
        if (c && c !== 'Sem Curso') canonicalSet.add(resolveCanonicalCourse(c));
    });

    const availableCourses = Array.from(canonicalSet).sort((a, b) => {
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

    let activeCourse = courseName || CURRENT_SELECTED_COURSE || (FILTER && FILTER.curso !== 'all' ? resolveCanonicalCourse(FILTER.curso) : '');
    if (!activeCourse || !availableCourses.includes(activeCourse)) {
        activeCourse = availableCourses[0];
    }
    CURRENT_SELECTED_COURSE = activeCourse;

    // 3. Alunos do Curso Ativo
    const cStudents = allEnrichedStudents.filter(s => s.canonical_curso === activeCourse);
    const totalMatriculas = cStudents.length;

    // 4. Dados Financeiros Unificados do Curso
    const unifiedFin = computeUnifiedFinancialDataset('all');
    const coursesData = (unifiedFin && (unifiedFin.courses || unifiedFin.coursesMap)) || {};
    const cFin = coursesData[activeCourse] || {
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

    // 5. Indicadores de Matrícula (Totais, 30d recentes, 30d anteriores, evolução mensal)
    const refDate = new Date(2026, 8, 15); // Data base de referência do fechamento
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

    // 6. Saúde, Engajamento & Retenção da Turma
    const vigentes = cStudents.filter(s => s.status !== 'Cancelado' && s.status !== 'Concluído' && !s.turma_encerrada);
    const countVigentes = vigentes.length;
    const countAtivos = vigentes.filter(s => s.status === 'Ativo').length;
    const countEmRisco = vigentes.filter(s => s.status === 'Em Risco' || s.status === 'Atenção').length;
    const countAbandonou = vigentes.filter(s => s.status === 'Abandonou' || s.status === 'Inativo').length;
    const countNunca = vigentes.filter(s => !s.acessou || s.status === 'Nunca acessou').length;
    const countCancelados = cStudents.filter(s => s.status === 'Cancelado').length;
    const countConcluidos = cStudents.filter(s => s.status === 'Concluído' || s.turma_encerrada).length;

    const totalAulasFeitas = cStudents.reduce((acc, s) => acc + (s.aulas_feitas || 0), 0);
    const mediaAulasPorAluno = totalMatriculas > 0 ? (totalAulasFeitas / totalMatriculas).toFixed(1) : '0.0';

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
        const W = 620, H = 180, pad = { l: 56, r: 16, t: 24, b: 32 };
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
            const barFill = isReal ? 'var(--brand)' : 'var(--purple, #7c3aed)';
            const opacity = isReal ? '0.88' : '0.65';
            const dash = isReal ? '' : 'stroke="#7c3aed" stroke-dasharray="2,2" stroke-width="1"';

            bars += `<rect x="${x}" y="${y}" width="${barW}" height="${h}" rx="3" fill="${barFill}" opacity="${opacity}" ${dash}>
                <title>${item.label} (${item.tipo.toUpperCase()}): ${fM(item.val)}</title>
            </rect>`;
            if (item.val > 0) {
                bars += `<text x="${x + barW/2}" y="${Math.max(pad.t + 10, y - 4)}" font-size="8.5" font-weight="700" fill="var(--ink)" text-anchor="middle">${Math.round(item.val/1000) > 0 ? (item.val/1000).toFixed(1)+'k' : item.val.toFixed(0)}</text>`;
            }
            labels += `<text x="${x + barW/2}" y="${H - 10}" font-size="9" fill="var(--muted)" text-anchor="middle">${item.label || item.mes}</text>`;
        });

        finSvg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" style="overflow:visible">${grid}${bars}${labels}</svg>`;
    } else {
        finSvg = '<div style="padding:40px; text-align:center; color:var(--muted)">Sem movimentações financeiras registradas para este curso.</div>';
    }

    // Helper para status badge do aluno
    const getStatusChip = (st) => {
        const map = {
            'Ativo': { bg: 'rgba(16, 185, 129, 0.12)', col: '#047857', border: 'rgba(16, 185, 129, 0.3)' },
            'Atenção': { bg: 'rgba(245, 158, 11, 0.12)', col: '#b45309', border: 'rgba(245, 158, 11, 0.3)' },
            'Em Risco': { bg: 'rgba(239, 68, 68, 0.12)', col: '#b91c1c', border: 'rgba(239, 68, 68, 0.3)' },
            'Abandonou': { bg: 'rgba(107, 114, 128, 0.15)', col: '#374151', border: 'rgba(107, 114, 128, 0.3)' },
            'Inativo': { bg: 'rgba(107, 114, 128, 0.15)', col: '#374151', border: 'rgba(107, 114, 128, 0.3)' },
            'Cancelado': { bg: 'rgba(220, 38, 38, 0.15)', col: '#991b1b', border: 'rgba(220, 38, 38, 0.3)' },
            'Concluído': { bg: 'rgba(14, 165, 233, 0.12)', col: '#0284c7', border: 'rgba(14, 165, 233, 0.3)' },
            'Apenas Login': { bg: 'rgba(217, 119, 6, 0.12)', col: '#92400e', border: 'rgba(217, 119, 6, 0.3)' },
            'Nunca acessou': { bg: 'rgba(156, 163, 175, 0.15)', col: '#4b5563', border: 'rgba(156, 163, 175, 0.3)' }
        };
        const cfg = map[st] || { bg: 'var(--paper)', col: 'var(--ink)', border: 'var(--line)' };
        return `<span style="background:${cfg.bg}; color:${cfg.col}; border:1px solid ${cfg.border}; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:12px; display:inline-block;">${st}</span>`;
    };

    // Montagem do Cockpit Completo
    mount.innerHTML = `
      <!-- SELETOR DE CURSOS (PILLS) -->
      <div style="background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 20px; margin-bottom:24px; box-shadow:0 1px 3px rgba(0,0,0,0.03)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
          <div>
            <h2 style="font-size:18px; font-weight:800; color:var(--ink); margin:0;">Cockpit por Especialidade: <span style="color:var(--brand)">${activeCourse}</span></h2>
            <div style="font-size:12px; color:var(--muted); margin-top:2px;">Selecione um curso abaixo para auditar indicadores de matrículas, engajamento e projeção financeira consolidada.</div>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Base Vigente do Curso:</span>
            <span class="badge" style="background:var(--brand-w); color:var(--brand); font-weight:700; font-size:12px; padding:4px 10px; border:1px solid rgba(2,132,199,0.3)">${fN(totalMatriculas)} Alunos Matriculados</span>
          </div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
          ${availableCourses.map(cName => {
              const isSel = (activeCourse === cName);
              const bg = isSel ? 'var(--brand)' : 'var(--paper)';
              const col = isSel ? '#fff' : 'var(--ink)';
              const border = isSel ? '1px solid var(--brand)' : '1px solid var(--line)';
              const count = allEnrichedStudents.filter(s => s.canonical_curso === cName).length;
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
              <div class="exec-sec-sub">Carteira histórica acumulada, entradas recentes (30d vs 30d anteriores) e evolução mensal de novos alunos.</div>
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
              <div class="exec-sec-sub">Status pedagógico da base vigente e métricas de consumo de aulas.</div>
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
            <div class="exec-card-sub">Acessando no ritmo esperado da especialidade</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Em Risco / Atenção</span>
              <span class="exec-pill ${countEmRisco > 0 ? 'pill-red' : 'pill-gray'}">${countVigentes > 0 ? Math.round((countEmRisco/countVigentes)*100) : 0}% da base</span>
            </div>
            <div class="exec-card-val" style="color:${countEmRisco > 0 ? '#DC2626' : 'var(--ink)'}">${fN(countEmRisco)}</div>
            <div class="exec-card-sub">Inatividade prolongada ou queda na cadência</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Inativos / Abandonaram</span>
              <span class="exec-pill ${countAbandonou > 0 ? 'pill-red' : 'pill-gray'}">${countVigentes > 0 ? Math.round((countAbandonou/countVigentes)*100) : 0}% da base</span>
            </div>
            <div class="exec-card-val" style="color:${countAbandonou > 0 ? '#DC2626' : 'var(--ink)'}">${fN(countAbandonou)}</div>
            <div class="exec-card-sub">Mais de 30 dias sem acesso (${countNunca} nunca acessaram)</div>
          </div>
        </div>

        <div style="background:var(--paper); border:1px solid var(--line); border-radius:10px; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div style="display:flex; gap:20px; align-items:center; flex-wrap:wrap;">
            <div>
              <span style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700">Média de Aulas por Aluno:</span>
              <span style="font-size:14px; font-weight:800; color:var(--ink); margin-left:6px">${mediaAulasPorAluno} aulas</span>
            </div>
            <div>
              <span style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700">Total de Aulas Concluídas:</span>
              <span style="font-size:14px; font-weight:800; color:var(--brand); margin-left:6px">${fN(totalAulasFeitas)} aulas</span>
            </div>
            <div>
              <span style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700">Taxa de Conclusão de Curso:</span>
              <span style="font-size:14px; font-weight:800; color:var(--emerald-d); margin-left:6px">${totalMatriculas > 0 ? ((countConcluidos / totalMatriculas)*100).toFixed(1) : 0}%</span>
            </div>
          </div>
          <button class="btn-exec-link" onclick="FILTER.curso = '${activeCourse.replace(/'/g, "\\'")}'; applyFilters(); selectTab('prog');" style="font-size:11.5px; padding:4px 10px;">Filtrar Alunos deste Curso no Progresso ➔</button>
        </div>
      </div>

      <!-- SEÇÃO 3: DESEMPENHO FINANCEIRO DO CURSO -->
      <div class="exec-sec" style="margin-bottom:24px;">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num" style="background:#7c3aed; color:#fff">$</div>
            <div>
              <h3 class="exec-sec-title">DESEMPENHO FINANCEIRO &amp; PROJEÇÃO DO CURSO</h3>
              <div class="exec-sec-sub">Receitas realizadas, previsibilidade contratual, MRR e projeções futuras consolidadas (Vindi + Asaas).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('fin')">Abrir Financeiro Geral →</button>
        </div>

        <div class="exec-grid-4" style="margin-bottom:16px;">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada Total</span>
              <span class="exec-pill pill-green">Acumulado</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(cFin.pago_total)}</div>
            <div class="exec-card-sub">${cFin.total_faturas_pagas || (cFin.faturas_tabela || []).filter(f=>f.pago).length} pagamentos processados</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Mês Atual (Pago / Previsto)</span>
              <span class="exec-pill pill-blue">Setembro/26</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand)">${fM(cFin.pago_mes_atual)}</div>
            <div class="exec-card-sub">Previsto mês: ${fM(cFin.previsto_mes_vigente || cFin.proj_mes_atual)} (a vencer: ${fM(cFin.proj_mes_atual)})</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">MRR Ativo do Curso</span>
              <span class="exec-pill pill-purple">Recorrência</span>
            </div>
            <div class="exec-card-val" style="color:#7c3aed">${fM(cFin.mrr)}</div>
            <div class="exec-card-sub">Receita Mensal Recorrente ativa deste curso</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Taxa de Adimplência</span>
              <span class="exec-pill ${cFin.taxa_adimplencia >= 90 ? 'pill-green' : 'pill-red'}">${cFin.taxa_adimplencia || 100}%</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${cFin.taxa_adimplencia || 100}%</div>
            <div class="exec-card-sub">${fM(cFin.atraso)} em atraso (${cFin.qtd_atraso || 0} faturas)</div>
          </div>
        </div>

        <!-- Projeções e Gráfico SVG -->
        <div style="display:grid; grid-template-columns: 360px 1fr; gap:16px; align-items:stretch;">
          <div style="display:flex; flex-direction:column; gap:12px;">
            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Projeção 3 Meses (Contratada)</span>
                <span class="exec-pill pill-purple">3M Futuro</span>
              </div>
              <div class="exec-card-val" style="color:#7c3aed">${fM(cFin.proj_3m)}</div>
              <div class="exec-card-sub">Recebíveis parcelados e mensalidades dos próximos 90 dias</div>
            </div>

            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Projeção 6 Meses</span>
                <span class="exec-pill pill-purple">6M Futuro</span>
              </div>
              <div class="exec-card-val" style="color:#7c3aed">${fM(cFin.proj_6m)}</div>
              <div class="exec-card-sub">Previsibilidade de faturamento para os próximos 180 dias</div>
            </div>

            <div class="exec-card" style="flex:1;">
              <div class="exec-card-top">
                <span class="exec-card-label">Projeção 12 Meses (LTV Futuro)</span>
                <span class="exec-pill pill-purple">12M Futuro</span>
              </div>
              <div class="exec-card-val" style="color:#7c3aed">${fM(cFin.proj_12m)}</div>
              <div class="exec-card-sub">Previsibilidade contratual anualizada para este curso</div>
            </div>
          </div>

          <div class="exec-card" style="display:flex; flex-direction:column; justify-content:space-between;">
            <div class="exec-card-top" style="margin-bottom:12px;">
              <div>
                <span class="exec-card-label" style="font-size:13px; font-weight:700; color:var(--ink)">Evolução Financeira: Realizado vs Previsto</span>
                <div style="font-size:11px; color:var(--muted)">Histórico recente de repasses realizados e projeção dos próximos meses</div>
              </div>
              <div style="display:flex; gap:12px; font-size:11px; align-items:center;">
                <span style="display:inline-flex; align-items:center; gap:4px;"><span style="width:10px; height:10px; border-radius:2px; background:var(--brand); display:inline-block"></span> Realizado</span>
                <span style="display:inline-flex; align-items:center; gap:4px;"><span style="width:10px; height:10px; border-radius:2px; background:#7c3aed; display:inline-block"></span> Previsto</span>
              </div>
            </div>
            <div style="width:100%; min-height:180px;">
              ${finSvg}
            </div>
          </div>
        </div>
      </div>

      <!-- SEÇÃO 4: ALUNOS MATRICULADOS NESTE CURSO -->
      <div class="exec-sec" style="margin-bottom:24px;">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num" style="background:var(--ink); color:#fff">👥</div>
            <div>
              <h3 class="exec-sec-title">ALUNOS MATRICULADOS NESTE CURSO</h3>
              <div class="exec-sec-sub">Listagem de alunos vinculados a esta especialidade com status de engajamento pedagógico e financeiro.</div>
            </div>
          </div>
          <span class="badge" style="background:var(--paper); color:var(--ink); font-weight:700">${cStudents.length} Alunos Listados</span>
        </div>

        <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; overflow:hidden;">
          <div style="max-height:480px; overflow-y:auto;">
            <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12px;">
              <thead style="background:var(--paper); position:sticky; top:0; z-index:1; border-bottom:1px solid var(--line);">
                <tr>
                  <th style="padding:10px 14px; font-weight:700; color:var(--muted)">ALUNO</th>
                  <th style="padding:10px 14px; font-weight:700; color:var(--muted)">STATUS</th>
                  <th style="padding:10px 14px; font-weight:700; color:var(--muted)">MATRÍCULA</th>
                  <th style="padding:10px 14px; font-weight:700; color:var(--muted)">AULAS FEITAS</th>
                  <th style="padding:10px 14px; font-weight:700; color:var(--muted)">PROGRESSO</th>
                  <th style="padding:10px 14px; font-weight:700; color:var(--muted)">ÚLTIMO ACESSO</th>
                  <th style="padding:10px 14px; font-weight:700; color:var(--muted); text-align:right">AÇÃO</th>
                </tr>
              </thead>
              <tbody>
                ${cStudents.map(s => {
                    const pct = s.pct_mods || 0;
                    const lastTxt = s.last_fmt ? (s.last_fmt + (s.dias_inativo != null ? ` (${s.dias_inativo}d)` : '')) : (s.acessou ? 'Acessou' : 'Nunca');
                    return `<tr style="border-bottom:1px solid var(--line); transition:background 0.1s;" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background='transparent'">
                      <td style="padding:10px 14px;">
                        <div style="font-weight:700; color:var(--ink)">${s.nome || 'Sem Nome'}</div>
                        <div style="font-size:11px; color:var(--muted)">${s.email || '-'}</div>
                      </td>
                      <td style="padding:10px 14px;">
                        ${getStatusChip(s.status)}
                      </td>
                      <td style="padding:10px 14px; color:var(--ink)">
                        ${s.data_insc || s.data_inscricao || s.inscricao || '-'}
                      </td>
                      <td style="padding:10px 14px; font-weight:700; color:var(--ink)">
                        ${s.aulas_feitas || 0} aulas
                      </td>
                      <td style="padding:10px 14px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                          <div style="flex:1; height:6px; background:var(--line); border-radius:3px; overflow:hidden; min-width:60px;">
                            <div style="width:${pct}%; height:100%; background:var(--brand); border-radius:3px;"></div>
                          </div>
                          <span style="font-size:11px; font-weight:700; color:var(--ink)">${pct}%</span>
                        </div>
                      </td>
                      <td style="padding:10px 14px; font-size:11.5px; color:var(--muted)">
                        ${lastTxt}
                      </td>
                      <td style="padding:10px 14px; text-align:right;">
                        <button type="button" onclick="FILTER.aluno='${(s.nome + " (" + s.email + ")").replace(/'/g, "\\'")}'; applyFilters(); selectTab('prog');" style="padding:4px 8px; font-size:11px; font-weight:700; border-radius:6px; background:var(--paper); border:1px solid var(--line); color:var(--brand); cursor:pointer;">
                          Ver Detalhes ➔
                        </button>
                      </td>
                    </tr>`;
                }).join('')}
              </tbody>
            </table>
          </div>
          ${cStudents.length > 100 ? `<div style="padding:12px; text-align:center; color:var(--muted); font-size:11.5px; background:var(--paper)">Exibindo 100 de ${totalMatriculas} alunos. Acesse a aba <b>Progresso por Aluno</b> para ver a lista completa com filtros.</div>` : ''}
        </div>
      </div>
    `;
}
'''

new_text = text[:idx_start] + curso_view_replacement + '\n\n' + text[idx_end:]

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print(f"Successfully replaced drawCursoView in template.html! (len before: {len(text)}, len after: {len(new_text)})")

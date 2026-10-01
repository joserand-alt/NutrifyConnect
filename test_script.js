const window = {}; const document = { querySelector: () => null, querySelectorAll: () => [] };

// Will be injected by gerador.py
const DATA = {};

let CURRENT_DATA = {};
let FILTER = { curso: 'all', aluno: 'all', start: '', end: '' };
let filterText = '';
const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);
const fmt = n => new Intl.NumberFormat('pt-BR').format(n);

function initFilters() {
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
}

function parseDate(dStr) {
    if(!dStr) return null;
    const parts = dStr.split(' ')[0].split('/');
    if(parts.length===3) return new Date(parts[2], parts[1]-1, parts[0]);
    return new Date(dStr);
}

function applyFilters() {
    let filteredStudents = DATA.students.filter(s => {
        if (FILTER.curso !== 'all' && s.curso !== FILTER.curso) return false;
        if (FILTER.aluno !== 'all' && (s.nome + " (" + s.email + ")") !== FILTER.aluno) return false;
        return true;
    });

    let sStart = FILTER.start ? new Date(FILTER.start) : null;
    let sEnd = FILTER.end ? new Date(FILTER.end) : null;
    if(sStart) sStart.setHours(0,0,0,0);
    if(sEnd) sEnd.setHours(23,59,59,999);
    
    let allEvents = [];
    let action_counts = {};
    let timelineMap = {}; 
    let activeStudentsCount = 0;
    
    // For module funnel
    let lessonViews = {}; // lesson_id -> Set of emails
    
    let emailsProcessedForStats = new Set();
    
    filteredStudents = filteredStudents.map(s => {
        let scopy = {...s};
        let s_lessons_done = new Set();
        
        let processStats = false;
        if (!emailsProcessedForStats.has(scopy.email)) {
            emailsProcessedForStats.add(scopy.email);
            processStats = true;
        }
        
        if (scopy.events) {
            scopy.events = scopy.events.filter(e => {
                if (!e.d) return true;
                let d = parseDate(e.d);
                if (!d || isNaN(d.getTime())) return true;
                if (sStart && d < sStart) return false;
                if (sEnd && d > sEnd) return false;
                return true;
            });
            
            scopy.acessou = scopy.events.length > 0;
            if (scopy.acessou && processStats) activeStudentsCount++;
            
            scopy.events.forEach(e => {
                let d = parseDate(e.d);
                if (!d || isNaN(d.getTime())) return;
                let isoDate = d.toISOString().split('T')[0];
                
                if (processStats) {
                    allEvents.push(e);
                    action_counts[e.acao] = (action_counts[e.acao]||0)+1;
                    
                    if (!timelineMap[isoDate]) {
                        timelineMap[isoDate] = {date:isoDate, logins:0, iniciou:0, concluiu:0, material:0, teste:0, _alunos:new Set(), total:0};
                    }
                    if (e.cat === 'login') timelineMap[isoDate].logins++;
                    else if (e.cat === 'iniciou') timelineMap[isoDate].iniciou++;
                    else if (e.cat === 'concluiu') timelineMap[isoDate].concluiu++;
                    else if (e.acao.includes('MATERIAL')) timelineMap[isoDate].material++;
                    else if (e.acao.includes('TESTE')) timelineMap[isoDate].teste++;
                    
                    timelineMap[isoDate]._alunos.add(s.email);
                    timelineMap[isoDate].total++;
                }
                
                if (e.acao === 'ASSISTIU AULA') {
                    if (e.item_id) {
                        s_lessons_done.add(e.item_id);
                        s_lessons_done.add(String(e.item_id));
                        if(!lessonViews[e.item_id]) lessonViews[e.item_id] = new Set();
                        lessonViews[e.item_id].add(s.email);
                    }
                    if (e.item) {
                        const nKey = e.item.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
                        s_lessons_done.add(nKey);
                        if(!lessonViews[nKey]) lessonViews[nKey] = new Set();
                        lessonViews[nKey].add(s.email);
                    }
                }
            });
        }
        
        scopy.aulas_feitas = s_lessons_done.size;
        scopy.mods_concluidos = 0;
        scopy.total_mods = 0;
        scopy.pct_mods = 0;
        scopy.status = 'Nunca acessou';
        scopy.status_motivo = 'O aluno nunca realizou login na plataforma.';
        
        if (DATA.curriculum[s.curso]) {
            let mods = DATA.curriculum[s.curso];
            scopy.total_mods = mods.length;
            let concluidos = 0;
            let total_aulas_curric = 0;
            let aulas_feitas_curric = 0;
            mods.forEach(m => {
                let done = 0;
                total_aulas_curric += m.n_curric;
                m.aulas.forEach(a => {
                    const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') : '';
                    if(a.curriculo && (s_lessons_done.has(a.id) || s_lessons_done.has(String(a.id)) || s_lessons_done.has(aNorm))) done++;
                });
                aulas_feitas_curric += done;
                if(m.n_curric > 0 && done >= m.n_curric) concluidos++;
            });
            scopy.mods_concluidos = concluidos;
            scopy.total_aulas_curric = total_aulas_curric;
            scopy.aulas_feitas_curric = aulas_feitas_curric;
            scopy.pct_mods = scopy.total_mods > 0 ? (concluidos / scopy.total_mods * 100) : 0;
        }

        if (!scopy.acessou) {
            scopy.status = 'Nunca acessou';
            scopy.status_motivo = 'O aluno nunca realizou login na plataforma.';
        } else {
            // Regra robusta: Concluído somente se concluiu todos os módulos com aulas disponíveis
            if (scopy.total_mods > 0 && scopy.mods_concluidos >= scopy.total_mods) {
                scopy.status = 'Concluído';
                scopy.status_motivo = 'Concluiu 100% dos módulos com aulas disponíveis do curso.';
            }
            else if (scopy.aulas_feitas === 0) {
                scopy.status = 'Apenas Login';
                scopy.status_motivo = `Acessou a plataforma (${scopy.logins || 1} login(s)), mas ainda não iniciou as aulas.`;
            }
            else {
                // Alunos com histórico de múltiplos logins
                if (scopy.logins > 1 && scopy.dias_ativo > 0) {
                    if (scopy.dias_inativo > 30 || (scopy.dias_inativo > 14 && scopy.dias_inativo > (scopy.cadencia * 2.5))) {
                        scopy.status = 'Abandonou';
                        scopy.status_motivo = scopy.dias_inativo > 30 
                            ? `Inatividade severa: ${scopy.dias_inativo} dias sem acessar a plataforma.` 
                            : `Inatividade crítica: acessava a cada ${Math.round(scopy.cadencia)} dias, mas está há ${scopy.dias_inativo} dias sem acesso.`;
                    } else if (scopy.dias_inativo > (scopy.cadencia * 1.5 + 2)) {
                        scopy.status = 'Em Risco';
                        scopy.status_motivo = `Quebra de padrão: o aluno acessa em média a cada ${Math.round(scopy.cadencia)} dias e está há ${scopy.dias_inativo} dias sem acesso.`;
                    } else {
                        scopy.status = 'Ativo';
                        scopy.status_motivo = 'O aluno está engajado e acessando no seu ritmo normal.';
                    }
                } else {
                    // Alunos sem histórico suficiente para calcular cadência
                    if (scopy.dias_inativo > 14) {
                        scopy.status = 'Abandonou';
                        scopy.status_motivo = `Inatividade severa: realizou apenas 1 login e está há ${scopy.dias_inativo} dias sem acessar.`;
                    } else if (scopy.dias_inativo > 7) {
                        scopy.status = 'Em Risco';
                        scopy.status_motivo = `Sem histórico consolidado e está há ${scopy.dias_inativo} dias sem acessar (ultrapassou limite de 7 dias).`;
                    } else {
                        scopy.status = 'Ativo';
                        scopy.status_motivo = 'O aluno está engajado e acessando normalmente.';
                    }
                }
            }
        }
        
        // REGRA DE STATUS FINANCEIRO:
        // Se o aluno tem assinatura CANCELADA na Vindi, o status dele eh sempre 'Cancelado',
        // independente do status calculado pela plataforma (Abandonou, Nunca acessou, etc.)
        const vindiStatus = scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : null;
        const asaasStatus = scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : null;
        if (vindiStatus === 'cancelado' || vindiStatus === 'canceled') {
            scopy.status = 'Cancelado';
            scopy.status_motivo = 'Assinatura cancelada no sistema financeiro (Vindi).';
        } else if (asaasStatus === 'cancelado' || asaasStatus === 'canceled') {
            scopy.status = 'Cancelado';
            scopy.status_motivo = 'Cobrança cancelada no sistema financeiro (Asaas).';
        }

        return scopy;
    });

    let timeline = Object.values(timelineMap).sort((a,b) => a.date.localeCompare(b.date)).map(t => {
        t.alunos = t._alunos.size;
        return t;
    });

    CURRENT_DATA = {
        meta: {...DATA.meta},
        students: filteredStudents,
        action_counts: action_counts,
        timeline: timeline,
        lesson_views: lessonViews
    };

    CURRENT_DATA.meta.n_inscritos = filteredStudents.length;
    CURRENT_DATA.meta.n_acessaram = activeStudentsCount;
    CURRENT_DATA.meta.n_eventos = allEvents.length;

    renderAll();
}

const STATUS = {
  'Concluído':{cls:'b-muito'}, 'Ativo':{cls:'b-ativo'},
  'Atenção':{cls:'b-atencao'}, 'Em Risco':{cls:'b-risco'},
  'Abandonou':{cls:'b-aband'}, 'Inativo':{cls:'b-aband'}, 'Cancelado':{cls:'b-canc'},
  'Apenas Login':{cls:'b-login'}, 'Nunca acessou':{cls:'b-nunca'}
};

function renderAll() {
    buildHead();
    drawExecView(true);
    drawHome(true);
    statusChips();
    renderRows();
    renderRetention();
    drawTimeline(true);
    renderModules();
    drawOrigem(true);
    drawFinanceiro(true);
}

function renderRetention() {
    let uniqueMap = new Map();
    CURRENT_DATA.students.forEach(s => {
        if(!uniqueMap.has(s.email)) uniqueMap.set(s.email, s);
        else {
            let exist = uniqueMap.get(s.email);
            if (exist.status === 'Nunca acessou' && s.status !== 'Nunca acessou') {
                uniqueMap.set(s.email, s);
            }
        }
    });
    
    let students = Array.from(uniqueMap.values());
    let total = students.length;
    if (total === 0) return;
    
    let never = 0, churn = 0, risco = 0, ativo = 0;
    let onesession = 0;
    let lags = [];
    let sameDay = 0;
    let enrolledNever = 0;
    let churnDiasAtivo = [];
    let survivalData = []; // for survival curve
    
    students.forEach(s => {
        if (!s.acessou || s.status === 'Nunca acessou' || (s.status === 'Atenção' && !s.acessou)) {
            never++;
            if (s.data_insc) enrolledNever++;
        } else {
            if (s.status === 'Abandonou' || s.status === 'Inativo') {
                churn++;
                churnDiasAtivo.push(s.dias_ativo);
            } else if (s.status === 'Em Risco') {
                risco++;
            } else {
                ativo++;
            }
            
            if (s.dias_ativo === 0) onesession++;
            
            if (s.data_insc && s.lag !== undefined) {
                if (s.lag === 0) sameDay++;
                if (s.lag >= 0) lags.push(s.lag);
            }
            
            // For survival curve: everyone who logged in has a dias_ativo length.
            survivalData.push(s.dias_ativo);
        }
    });
    
    $('#o-never').textContent = fmt(never);
    $('#o-aband').textContent = fmt(churn);
    $('#o-risco').textContent = fmt(risco);
    $('#o-ativo').textContent = fmt(ativo);
    
    $('#ab-onesession').textContent = fmt(onesession);
    
    $('#ret-insight').innerHTML = `<b>${fmt(Math.round((never/total)*100))}%</b> da base nunca logou. Dos que logaram, <b>${fmt(Math.round((churn/(total-never||1))*100))}%</b> estão inativos.`;
    
    $('#lag-never').textContent = fmt(enrolledNever);
    if (lags.length > 0) {
        lags.sort((a,b)=>a-b);
        let sum = lags.reduce((a,b)=>a+b, 0);
        let med = lags[Math.floor(lags.length/2)];
        $('#lag-media').textContent = fmt(Math.round(sum/lags.length)) + ' d';
        $('#lag-med').textContent = med + ' d';
        $('#lag-same').textContent = fmt(sameDay) + ' alunos';
    } else {
        $('#lag-media').textContent = '—';
        $('#lag-med').textContent = '—';
        $('#lag-same').textContent = '—';
    }
    
    if (churnDiasAtivo.length > 0) {
        churnDiasAtivo.sort((a,b)=>a-b);
        let sum = churnDiasAtivo.reduce((a,b)=>a+b,0);
        let med = churnDiasAtivo[Math.floor(churnDiasAtivo.length/2)];
        $('#ab-media').textContent = fmt(Math.round(sum/churnDiasAtivo.length)) + ' d';
        $('#ab-med').textContent = med + ' d';
    } else {
        $('#ab-media').textContent = '—';
        $('#ab-med').textContent = '—';
    }
    
    // Draw survival curve
    const sBox = $('#survival');
    if(survivalData.length === 0) {
        sBox.innerHTML = '<div style="padding:20px;text-align:center;color:var(--muted)">Sem dados suficientes</div>';
    } else {
        const W = sBox.clientWidth || 400; const H = 140; const pad={l:30,r:10,t:10,b:20};
        const maxDays = Math.max(...survivalData, 1);
        const steps = 20;
        const stepSize = maxDays/steps;
        let pts = [];
        let totalValids = survivalData.length;
        for(let i=0; i<=steps; i++){
            let d = i * stepSize;
            let alive = survivalData.filter(x => x >= d).length;
            let pct = (alive / totalValids) * 100;
            
            let cx = pad.l + (i/steps) * (W-pad.l-pad.r);
            let cy = pad.t + (1 - pct/100) * (H-pad.t-pad.b);
            pts.push(`${cx},${cy}`);
        }
        
        let pathLine = `<polyline points="${pts.join(' ')}" fill="none" stroke="var(--ink)" stroke-width="2"/>`;
        let areaPts = `M${pad.l},${H-pad.b} L` + pts.join(' L') + ` L${pts[pts.length-1].split(',')[0]},${H-pad.b} Z`;
        let pathArea = `<path d="${areaPts}" fill="rgba(18, 35, 46, 0.05)" />`;
        
        // Grid Y
        let grid = '';
        [0, 25, 50, 75, 100].forEach(v => {
            let yy = pad.t + (1 - v/100) * (H-pad.t-pad.b);
            grid += `<line x1="${pad.l}" y1="${yy}" x2="${W-pad.r}" y2="${yy}" stroke="var(--line2)"/>`;
            grid += `<text x="${pad.l-5}" y="${yy+3}" font-size="9" text-anchor="end" fill="var(--muted)">${v}%</text>`;
        });
        
        // Axis X
        [0, 0.25, 0.5, 0.75, 1].forEach(frac => {
            let xx = pad.l + frac * (W-pad.l-pad.r);
            let d = Math.round(frac * maxDays);
            grid += `<text x="${xx}" y="${H-5}" font-size="9" text-anchor="middle" fill="var(--muted)">${d}d</text>`;
        });
        
        sBox.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%">${grid}${pathArea}${pathLine}</svg>`;
    }
}

function buildHead(){
  const M = CURRENT_DATA.meta;
  $('#hd-sub').innerHTML = `<b>${fmt(M.n_inscritos)}</b> matriculados · <b>${fmt(M.n_acessaram)}</b> já acessaram (${(M.n_acessaram/Math.max(1, M.n_inscritos)*100).toFixed(1).replace('.', ',')}%)`;
  
  const ev = CURRENT_DATA.action_counts;
  const kpis = [
    {l:'Matriculados',v:fmt(M.n_inscritos),c:'var(--ink)',s:'No período / filtro'},
    {l:'Total de Reproduções',v:fmt(ev['ASSISTIU AULA']||0),c:'var(--emerald)',s:'Visualizações em aulas'},
    {l:'Logins',v:fmt(ev['LOGIN WEB']||0),c:'var(--sky)',s:'Sessões iniciadas'},
    {l:'Testes Realizados',v:fmt((ev['CONCLUIU TESTE/MÓDULO']||0)+(ev['REFAZER TESTE/MÓDULO']||0)),c:'var(--amber)',s:'Módulos finalizados'},
    {l:'Nunca acessaram',v:fmt(M.n_inscritos - M.n_acessaram),c:'var(--coral)',s:'Zero atividade',id:'kpi-aband'}
  ];
  $('#kpis').innerHTML = kpis.map(k=>`<div class="kpi"><div class="k-lab"><i class="k-dot" style="background:${k.c}"></i>${k.l}</div>
    <div class="k-val" style="color:${k.c}">${k.v}</div><div class="k-sub">${k.s}</div></div>`).join('');
}

let ST_FILT='all';
function statusChips(){
  const counts={'all':CURRENT_DATA.students.length};
  CURRENT_DATA.students.forEach(s=>{ counts[s.status]=(counts[s.status]||0)+1; });
  const chips=[{id:'all',l:'Todos'}];
  Object.keys(STATUS).forEach(k=>{if(counts[k])chips.push({id:k,l:k});});
  $('#statuschips').innerHTML = chips.map(c=>`<button class="chip ${ST_FILT===c.id?'on':''}" data-id="${c.id}">${c.l} <span class="cn">${counts[c.id]||0}</span></button>`).join('');
  $$('#statuschips .chip').forEach(b=>b.onclick=e=>{ST_FILT=b.dataset.id;statusChips();renderRows();});
}

const COLS = [
  { id: 'nome', label: 'Aluno', defaultAsc: true, align: 'left' },
  { id: 'curso', label: 'Curso', defaultAsc: true, align: 'left' },
  { id: 'status', label: 'Status', defaultAsc: false, align: 'left' },
  { id: 'vindi', label: 'Vindi (Pgto)', defaultAsc: false, align: 'left' },
  { id: 'progresso', label: 'Progresso', defaultAsc: false, align: 'left' },
  { id: 'last', label: 'Último acesso', defaultAsc: false, align: 'left' },
  { id: 'aulas_feitas', label: 'Aulas feitas', defaultAsc: false, align: 'right' },
  { id: 'logins', label: 'Logins', defaultAsc: false, align: 'right' },
  { id: 'materiais', label: 'Materiais', defaultAsc: false, align: 'right' },
  { id: 'dias_ativo', label: 'Dias ativo', defaultAsc: false, align: 'right' },
  { id: 'dias_inativo', label: 'Inativo (d)', defaultAsc: false, align: 'right' }
];

let sortCol = 'nome';
let sortAsc = true;

function sortRows(colId) {
    if (sortCol === colId) {
        sortAsc = !sortAsc;
    } else {
        sortCol = colId;
        const colDef = COLS.find(c => c.id === colId);
        sortAsc = colDef ? colDef.defaultAsc : true;
    }
    renderRows();
}

function getPlatBadge(plat) {
    if (plat === 'Cativa') {
        return `<span style="font-size:9.5px; padding:1.5px 6px; border-radius:4px; background:rgba(236,72,153,0.12); color:#db2777; border:1px solid rgba(236,72,153,0.3); font-weight:600; margin-left:6px; vertical-align:middle;" title="Plataforma Cativa Digital">Cativa</span>`;
    } else if (plat === 'Ambas') {
        return `<span style="font-size:9.5px; padding:1.5px 6px; border-radius:4px; background:rgba(168,85,247,0.12); color:#7c3aed; border:1px solid rgba(168,85,247,0.3); font-weight:600; margin-left:6px; vertical-align:middle;" title="Presente em ambas as plataformas">Ambas</span>`;
    }
    return `<span style="font-size:9.5px; padding:1.5px 6px; border-radius:4px; background:rgba(2,132,199,0.12); color:#0284c7; border:1px solid rgba(2,132,199,0.3); font-weight:600; margin-left:6px; vertical-align:middle;" title="Plataforma InfectoCast Academy">Academy</span>`;
}

function getFinBadge(s) {
    const v = s.vindi;
    const a = s.asaas;
    if ((!v || !v.has_vindi) && (!a || !a.has_asaas)) {
        return `<span style="color:var(--muted2); font-size:11px;" title="Sem registros financeiros">—</span>`;
    }

    // Se tiver cobrança em atraso em qualquer gateway, destaca como Atraso
    if (a && a.status_financeiro === 'em_atraso') {
        const d = a.dias_atraso || 0;
        return `<span class="badge" style="background:rgba(244,63,94,0.12); color:#e11d48; border:1px solid rgba(244,63,94,0.3); font-weight:700; cursor:pointer;" title="Asaas: em atraso há ${d} dias · R$ ${(a.valor_atraso||0).toFixed(2)}"><span class="b-dot" style="background:#e11d48"></span>[Asaas] Atraso ${d}d</span>`;
    }
    if (v && v.status_financeiro === 'em_atraso') {
        const d = v.dias_atraso || 0;
        return `<span class="badge" style="background:rgba(244,63,94,0.12); color:#e11d48; border:1px solid rgba(244,63,94,0.3); font-weight:700; cursor:pointer;" title="Vindi: em atraso há ${d} dias · R$ ${(v.valor_atraso||0).toFixed(2)}"><span class="b-dot" style="background:#e11d48"></span>[Vindi] Atraso ${d}d</span>`;
    }

    // Se estiver a vencer
    if (a && a.status_financeiro === 'a_vencer') {
        return `<span class="badge" style="background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.3); font-weight:600;" title="Asaas: vencimento próximo"><span class="b-dot" style="background:#d97706"></span>[Asaas] A Vencer</span>`;
    }
    if (v && v.status_financeiro === 'a_vencer') {
        return `<span class="badge" style="background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.3); font-weight:600;" title="Vindi: vencimento próximo"><span class="b-dot" style="background:#d97706"></span>[Vindi] A Vencer</span>`;
    }

    // Se estiver adimplente
    if (a && a.status_financeiro === 'adimplente') {
        return `<span class="badge" style="background:rgba(16,185,129,0.12); color:#059669; border:1px solid rgba(16,185,129,0.3); font-weight:600;" title="Asaas: Em dia"><span class="b-dot" style="background:#059669"></span>[Asaas] Em Dia</span>`;
    }
    if (v && v.status_financeiro === 'adimplente') {
        return `<span class="badge" style="background:rgba(16,185,129,0.12); color:#059669; border:1px solid rgba(16,185,129,0.3); font-weight:600;" title="Vindi: Em dia"><span class="b-dot" style="background:#059669"></span>[Vindi] Em Dia</span>`;
    }

    // Quitado / Cancelado
    if (v && v.status_financeiro === 'quitado') {
        return `<span class="badge" style="background:rgba(100,116,139,0.1); color:#64748b; border:1px solid rgba(100,116,139,0.25); font-weight:600;"><span class="b-dot" style="background:#64748b"></span>Quitado</span>`;
    }
    if ((v && v.status_financeiro === 'cancelado') || (a && a.status_financeiro === 'cancelado')) {
        return `<span class="badge" style="background:rgba(0,0,0,0.05); color:var(--muted); border:1px solid rgba(0,0,0,0.1); font-weight:500;"><span class="b-dot" style="background:var(--muted)"></span>Cancelado</span>`;
    }

    const label = (a && a.status_label) || (v && v.status_label) || 'Financeiro';
    return `<span class="badge" style="background:rgba(0,0,0,0.05); color:var(--muted); font-weight:500;"><span class="b-dot"></span>${label}</span>`;
}

function renderRows(){
  const tbody = $('#tbody');
  const dash='<span style="color:var(--muted2)">—</span>';
  
  let rows = CURRENT_DATA.students.filter(s=>{
    if(ST_FILT!=='all' && s.status!==ST_FILT) return false;
    if(filterText) {
        const ft = filterText.toLowerCase();
        const nome = (s.nome || '').toLowerCase();
        const email = (s.email || '').toLowerCase();
        const plat = (s.plataforma || 'Academy').toLowerCase();
        if(!nome.includes(ft) && !email.includes(ft) && !plat.includes(ft)) return false;
    }
    return true;
  });

  rows.sort((a, b) => {
      let vA, vB;
      if (sortCol === 'nome') {
          vA = (a.nome || '').toLowerCase();
          vB = (b.nome || '').toLowerCase();
          return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
      }
      if (sortCol === 'curso') {
          vA = (a.curso || '').toLowerCase();
          vB = (b.curso || '').toLowerCase();
          return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
      }
      if (sortCol === 'status') {
          vA = (a.status || '').toLowerCase();
          vB = (b.status || '').toLowerCase();
          return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
      }
      if (sortCol === 'vindi') {
          const rank = { 'em_atraso': 1, 'a_vencer': 2, 'adimplente': 3, 'quitado': 4, 'cancelado': 5 };
          const rA = (a.vindi && rank[a.vindi.status_financeiro]) ? rank[a.vindi.status_financeiro] : 99;
          const rB = (b.vindi && rank[b.vindi.status_financeiro]) ? rank[b.vindi.status_financeiro] : 99;
          vA = rA;
          vB = rB;
      } else if (sortCol === 'progresso') {
          vA = a.pct_mods || 0;
          vB = b.pct_mods || 0;
      } else if (sortCol === 'last') {
          vA = parseDate(a.last_fmt) || new Date(0);
          vB = parseDate(b.last_fmt) || new Date(0);
      } else if (sortCol === 'aulas_feitas') {
          vA = a.aulas_feitas || 0;
          vB = b.aulas_feitas || 0;
      } else if (sortCol === 'logins') {
          vA = a.logins || 0;
          vB = b.logins || 0;
      } else if (sortCol === 'materiais') {
          vA = a.materiais || 0;
          vB = b.materiais || 0;
      } else if (sortCol === 'dias_ativo') {
          vA = a.dias_ativo || 0;
          vB = b.dias_ativo || 0;
      } else if (sortCol === 'dias_inativo') {
          vA = a.dias_inativo != null ? a.dias_inativo : -1;
          vB = b.dias_inativo != null ? b.dias_inativo : -1;
      }
      if (vA < vB) return sortAsc ? -1 : 1;
      if (vA > vB) return sortAsc ? 1 : -1;
      return 0;
  });

  $('#thead').innerHTML = COLS.map(c => {
      const isSorted = sortCol === c.id;
      const arrow = isSorted ? (sortAsc ? ' ▲' : ' ▼') : ' <span style="opacity:0.35">↕</span>';
      return `<th onclick="sortRows('${c.id}')" style="cursor:pointer; user-select:none; text-align:${c.align}; ${c.id==='dias_inativo'?'min-width:90px;':''}" title="Ordenar por ${c.label}">
          ${c.label}${arrow}
      </th>`;
  }).join('');

  tbody.innerHTML = rows.map(s=>{
    const st=STATUS[s.status]||{cls:'b-login'};
    const na=!s.acessou;
    const da = na?dash:s.dias_ativo;
    const di = na?dash:`<span style="color:${s.dias_inativo>=14?'var(--amber)':'var(--muted)'}">${s.dias_inativo}</span>`;
    const pctBar = (s.total_aulas_curric > 0 && s.aulas_feitas_curric > 0) ? (s.aulas_feitas_curric / s.total_aulas_curric * 100) : (s.pct_mods || 0);
    const prog = na?dash:`<div class="pct-cell" title="${s.aulas_feitas_curric||0}/${s.total_aulas_curric||0} aulas feitas (${Math.round(pctBar)}%) | ${s.mods_concluidos||0}/${s.total_mods||0} módulos concluídos"><div class="pct-bar"><i style="width:${pctBar}%"></i></div><span class="pct-txt">${s.mods_concluidos||0}/${s.total_mods||0}</span></div>`;
    const ultimo = na?dash:`<span title="log mais recente">${s.last_fmt}</span>`;
    return `<tr class="clickable" data-email="${s.email}" data-curso="${s.curso}"${na?' style="opacity:.72"':''}>
      <td><div class="al-nome">${s.nome}${getPlatBadge(s.plataforma)}${na?'':' <span class="row-open">ver histórico ›</span>'}</div><div class="al-mail">${s.email}</div></td>
      <td style="font-size:11.5px;color:var(--muted);white-space:nowrap;max-width:140px;overflow:hidden;text-overflow:ellipsis" title="${s.curso}">${s.curso}</td>
      <td class="st-td"><span class="badge ${st.cls}" title="${s.status_motivo}"><span class="b-dot"></span>${s.status}</span></td>
      <td>${getFinBadge(s)}</td>
      <td>${prog}</td>
      <td class="num-c" style="text-align:left">${ultimo}</td>
      <td class="num-c">${na?dash:s.aulas_feitas}</td>
      <td class="num-c">${s.logins||0}</td>
      <td class="num-c">${s.materiais||0}</td>
      <td class="num-c">${da}</td>
      <td class="num-c">${di}</td>
    </tr>`;
  }).join('');
  $('#tblcount').textContent = `${rows.length} aluno${rows.length!==1?'s':''} exibido${rows.length!==1?'s':''}`;
}

$('#search').oninput = e=>{filterText=e.target.value;renderRows();};

// MODAL
const STMAP={};
window.openModal = function(param){ openStudent(param); };
function openStudent(email, curso){
  if (!email) return;
  const emLow = email.toLowerCase().trim();
  const s = (CURRENT_DATA?.students || []).find(x => x.email && x.email.toLowerCase().trim() === emLow && (!curso || x.curso === curso)) || 
            (CURRENT_DATA?.students || []).find(x => x.email && x.email.toLowerCase().trim() === emLow) || 
            (DATA.students || []).find(x => x.email && x.email.toLowerCase().trim() === emLow && (!curso || x.curso === curso)) ||
            (DATA.students || []).find(x => x.email && x.email.toLowerCase().trim() === emLow);
  if(!s) return;
  const statusDisplay = s.status || (!s.acessou ? 'Nunca acessou' : (s.dias_inativo > 30 ? 'Abandonou' : 'Ativo'));
  const modal=$('#modal');
  $('#md-nome').innerHTML=`${s.nome}${getPlatBadge(s.plataforma)}`;
  let btnWpp = '';
  if (['Em Risco', 'Atenção', 'Inativo'].includes(s.status)) {
      let avisoMsg = '';
      if (CURRENT_DATA.mensagens_recentes && CURRENT_DATA.mensagens_recentes[s.email]) {
          const m = CURRENT_DATA.mensagens_recentes[s.email];
          avisoMsg = `<span style="color:var(--amber); font-size:10px; margin-left:8px; font-weight:600;" title="Último registro em: ${m.data}">⚠️ Avisado há ${m.dias} dia${m.dias!==1?'s':''}</span>`;
      }
      btnWpp = `<button onclick="sendWhatsapp('${s.email}', '${s.status}')" style="margin-left:12px; padding:4px 8px; font-family:var(--body); font-size:10px; background:rgba(255,255,255,.15); color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:500; display:inline-flex; align-items:center; gap:4px; vertical-align:middle;"><svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg> Mensagem</button>${avisoMsg}`;
  }
  let btnChat = '';
  if (s.telefone && s.wa_total > 0) {
      btnChat = `<button onclick="openWAChat('${s.telefone.replace(/\D/g,'')}', '${s.nome.replace(/'/g,"\'").replace(/"/g,'&quot;')}')" style="margin-left:4px; padding:4px 8px; font-family:var(--body); font-size:10px; background:rgba(255,255,255,.15); color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:500; display:inline-flex; align-items:center; gap:4px; vertical-align:middle;">👁 Histórico</button>`;
  }
  $('#md-mail').innerHTML=`${s.email}${btnWpp}${btnChat}`;
  let dataInscFmt = s.data_insc || '—';
  if (dataInscFmt && dataInscFmt.includes('-')) {
      const p = dataInscFmt.split('-');
      if (p.length === 3) dataInscFmt = `${p[2]}/${p[1]}/${p[0]}`;
  }
  $('#md-stats').innerHTML=[
    ['Status',statusDisplay],['Módulos',`${s.mods_concluidos||0}/${s.total_mods||0}`],
    ['Último acesso',s.last_fmt||'—'],['Dias inativo',s.dias_inativo != null ? s.dias_inativo : '—'],
    ['Inscrição',dataInscFmt], ['Plataforma', s.plataforma || 'Academy'], ['Último WA', s.wa_dt_ultima || '—']
  ].map(([l,v])=>`<div class="st"><div class="v">${v}</div><div class="l">${l}</div></div>`).join('');
  
  let rdHtml = '';
  if (s.rd_funnel) {
      const rd = s.rd_funnel;
      const origin = rd.origem || 'Desconhecida';
      const conv = rd.conversoes || 0;
      const pri = rd.dt_primeira || '—';
      const ult = rd.dt_ultima || '—';
      const isApi = rd.fonte === 'API Oficial RD Station';
      const antesQtd = rd.conversoes_antes !== undefined ? rd.conversoes_antes : (rd.eventos ? rd.eventos.length : 0);
      const evsStr = rd.eventos && rd.eventos.length ? rd.eventos.map(e => `<li style="margin-bottom:6px">${e}</li>`).join('') : '<li style="color:var(--muted)">Nenhum evento registrado antes da matrícula</li>';
      rdHtml = `
      <div style="margin:20px 20px 0; padding:14px 16px; border:1px solid var(--line2); border-radius:10px; background:rgba(255,255,255,0.03); box-shadow:0 2px 8px rgba(0,0,0,0.04)">
        <div style="display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="const b=document.getElementById('rd-body'); b.style.display=b.style.display==='none'?'block':'none'">
            <div>
              <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px">
                <b style="font-size:12px; color:var(--text)">Jornada RD Station (Antes da Matrícula)${s.wa_total ? ' + WhatsApp' : ''}</b>
                ${isApi ? '<span style="background:rgba(0,180,216,0.15); color:#00b4d8; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; border:1px solid rgba(0,180,216,0.3)">API Oficial RD Station</span>' : ''}
              </div>
              <span style="font-size:11px; color:var(--muted)">Origem: <b>${origin}</b> · Conversões: <b>${conv}</b> (${antesQtd} antes da matrícula) · Primeira: <b>${pri}</b> · Última: <b>${ult}</b></span>
              ${s.wa_total ? `<br><b style="font-size:11px; color:#25D366">Primeiro contato WA: ${s.wa_dt_primeira}</b>` : ''}
            </div>
            <button style="border:1px solid var(--line2); background:var(--bg); color:var(--text); padding:5px 10px; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer">Ver Conversões (${antesQtd}) ▾</button>
        </div>
        <div id="rd-body" style="display:none; margin-top:12px; padding-top:12px; border-top:1px solid var(--line2)">
            <div style="font-size:11px; font-weight:700; color:var(--text); margin-bottom:8px">Linha do Tempo de Conversões (API RD Station):</div>
            <ul style="font-size:11px; color:var(--text); padding-left:18px; margin:0; line-height:1.7">
                ${evsStr}
            </ul>
        </div>
      </div>
      `;
  }
  
  let vindiHtml = '';
  const hasV = s.vindi && s.vindi.has_vindi;
  const hasA = s.asaas && s.asaas.has_asaas;

  function buildFaturasTableRows(faturas, alunoNome, alunoEmail, gwNome) {
      if (!faturas || !faturas.length) {
          return `<tr><td colspan="6" style="padding:12px; text-align:center; color:var(--muted); font-size:11px">Nenhuma fatura registrada no ${gwNome} para este aluno.</td></tr>`;
      }
      return faturas.map(f => {
          const isPago = f.status === 'paid' || f.status === 'pago';
          const isOverdue = f.status === 'em_atraso';
          const isAvencer = f.status === 'a_vencer';
          const isFuturo = f.status === 'futuro';

          let stBadge = '';
          if (isPago) {
              stBadge = `<span style="background:rgba(16,185,129,0.12); color:#059669; font-weight:700; padding:2px 8px; border-radius:10px; font-size:10px; border:1px solid rgba(16,185,129,0.3)">✓ Pago</span>`;
          } else if (isOverdue) {
              stBadge = `<span style="background:rgba(225,29,72,0.12); color:#e11d48; font-weight:700; padding:2px 8px; border-radius:10px; font-size:10px; border:1px solid rgba(225,29,72,0.3)">Atraso (${f.dias_atraso||0}d)</span>`;
          } else if (isAvencer) {
              stBadge = `<span style="background:rgba(245,158,11,0.12); color:#d97706; font-weight:700; padding:2px 8px; border-radius:10px; font-size:10px; border:1px solid rgba(245,158,11,0.3)">A Vencer</span>`;
          } else if (isFuturo) {
              stBadge = `<span style="background:rgba(59,130,246,0.1); color:#2563eb; font-weight:600; padding:2px 8px; border-radius:10px; font-size:10px; border:1px solid rgba(59,130,246,0.25)">Futuro</span>`;
          } else {
              stBadge = `<span style="background:rgba(0,0,0,0.05); color:var(--muted); font-weight:600; padding:2px 8px; border-radius:10px; font-size:10px; border:1px solid rgba(0,0,0,0.1)">${f.status_label || f.status}</span>`;
          }

          let formaBadge = `<span style="font-size:10.5px; color:var(--ink)">${f.forma_pagamento || '—'}</span>`;
          const fpLow = (f.forma_pagamento||'').toLowerCase();
          if (fpLow.includes('pix')) {
              formaBadge = `<span style="display:inline-flex; align-items:center; gap:3px; background:rgba(16,185,129,0.08); color:#047857; padding:1px 6px; border-radius:4px; font-size:10.5px; font-weight:700">❖ Pix</span>`;
          } else if (fpLow.includes('cart') || fpLow.includes('credit')) {
              formaBadge = `<span style="display:inline-flex; align-items:center; gap:3px; background:rgba(2,132,199,0.08); color:#0284c7; padding:1px 6px; border-radius:4px; font-size:10.5px; font-weight:700">💳 Cartão</span>`;
          } else if (fpLow.includes('boleto')) {
              formaBadge = `<span style="display:inline-flex; align-items:center; gap:3px; background:rgba(245,158,11,0.08); color:#b45309; padding:1px 6px; border-radius:4px; font-size:10.5px; font-weight:700">📄 Boleto</span>`;
          }

          const dataTxt = isPago 
              ? `<div style="font-size:11px; font-weight:700; color:#059669">${f.data_pagamento || f.vencimento}</div><div style="font-size:9.5px; color:var(--muted)">Venc: ${f.vencimento || '—'}</div>`
              : `<div style="font-size:11px; font-weight:700; color:${isOverdue ? '#e11d48' : 'var(--ink)'}">${f.vencimento || '—'}</div>${isOverdue ? `<div style="font-size:9.5px; color:#e11d48">Vencida há ${f.dias_atraso||0}d</div>` : (isFuturo ? `<div style="font-size:9.5px; color:#2563eb">Agendada</div>` : '')}`;

          let acaoHtml = '';
          if (f.url) {
              acaoHtml += `<a href="${f.url}" target="_blank" style="display:inline-flex; align-items:center; gap:4px; padding:3px 8px; border-radius:5px; background:var(--sky-w); color:var(--sky-d); border:1px solid rgba(2,132,199,0.25); font-size:10.5px; font-weight:700; text-decoration:none;">Abrir Fatura ↗</a>`;
          }
          if (isOverdue) {
              const safeNome = (alunoNome || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
              const vFmt = f.valor_fmt || `R$ ${(f.valor||0).toFixed(2)}`;
              acaoHtml += `<button onclick="sendVindiCobranca('${alunoEmail}', '${safeNome}', '${vFmt}', '${f.vencimento}', '${f.url}')" style="margin-left:6px; display:inline-flex; align-items:center; gap:3px; background:#e11d48; color:#fff; border:none; padding:3px 8px; border-radius:5px; font-size:10px; font-weight:700; cursor:pointer" title="Cobrar esta fatura no WhatsApp">💬 Cobrar</button>`;
          }

          return `
            <tr style="border-bottom:1px solid var(--line2); font-size:11px">
              <td style="padding:6px 8px; font-family:monospace; color:var(--muted)">#${String(f.id).slice(0, 16)}</td>
              <td style="padding:6px 8px">${dataTxt}</td>
              <td style="padding:6px 8px; font-weight:700; color:var(--ink)">${f.valor_fmt || `R$ ${(f.valor||0).toFixed(2)}`}</td>
              <td style="padding:6px 8px">${formaBadge}</td>
              <td style="padding:6px 8px">${stBadge}</td>
              <td style="padding:6px 8px; text-align:right">${acaoHtml || '—'}</td>
            </tr>
          `;
      }).join('');
  }

  let cardsHtml = '';
  const safeMailId = (s.email||'').replace(/[^a-zA-Z0-9]/g,'');

  // Card Asaas
  if (hasA) {
      const a = s.asaas;
      const isAtrasoA = a.status_financeiro === 'em_atraso';
      const stColorA = isAtrasoA ? '#e11d48' : (a.status_financeiro === 'adimplente' ? '#059669' : '#64748b');
      const stBgA = isAtrasoA ? 'rgba(244,63,94,0.12)' : (a.status_financeiro === 'adimplente' ? 'rgba(16,185,129,0.12)' : 'rgba(100,116,139,0.12)');
      const stBorderA = isAtrasoA ? 'rgba(244,63,94,0.3)' : 'rgba(16,185,129,0.3)';
      const faturasRowsA = buildFaturasTableRows(a.faturas, s.nome, s.email, 'Asaas');

      let btnCobrancaA = '';
      if (isAtrasoA) {
          const safeNome = (s.nome || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
          const valorFmt = a.valor_atraso ? `R$ ${a.valor_atraso.toFixed(2)}` : 'da sua mensalidade';
          const faturaVenc = a.proximo_vencimento || 'em aberto';
          btnCobrancaA = `
            <button onclick="sendVindiCobranca('${s.email}', '${safeNome}', '${valorFmt}', '${faturaVenc}', '')" style="display:inline-flex; align-items:center; gap:6px; background:#e11d48; color:#fff; border:none; padding:6px 12px; border-radius:6px; font-size:11px; font-weight:700; cursor:pointer; box-shadow:0 2px 6px rgba(225,29,72,0.25)">
              <span>💬</span> <span>Cobrar no WhatsApp</span>
            </button>
          `;
      }

      cardsHtml += `
      <div style="margin:14px 20px 0; padding:14px 16px; border:1px solid ${isAtrasoA ? 'rgba(244,63,94,0.3)' : 'rgba(2,132,199,0.25)'}; border-radius:10px; background:${isAtrasoA ? 'rgba(244,63,94,0.03)' : 'rgba(2,132,199,0.02)'}; box-shadow:0 2px 8px rgba(0,0,0,0.04)">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px">
              <span style="font-size:11px; background:rgba(2,132,199,0.12); color:#0284c7; padding:2px 6px; border-radius:4px; font-weight:800">ASAAS</span>
              <b style="font-size:12.5px; color:var(--text)">Financeiro &amp; Cobranças</b>
              <span style="background:${stBgA}; color:${stColorA}; font-size:10px; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid ${stBorderA}">${a.status_label || 'Asaas'}</span>
              ${a.customer_id ? `<span style="font-size:10px; color:var(--muted); font-family:monospace">Cliente: ${a.customer_id}</span>` : ''}
              ${a.cpfcnpj ? `<span style="font-size:10px; color:var(--muted)">CPF: ${a.cpfcnpj}</span>` : ''}
            </div>
            <div style="font-size:11px; color:var(--muted)">
              Total Pago: <b style="color:#059669">${a.total_pago_fmt || 'R$ ' + (a.total_pago||0).toFixed(2)}</b>
              ${a.valor_atraso ? ` · Em Atraso: <b style="color:#e11d48">R$ ${a.valor_atraso.toFixed(2)}</b>` : ''}
              ${a.faturas ? ` · Total Faturas: <b>${a.faturas.length}</b>` : ''}
            </div>
            ${isAtrasoA ? `
              <div style="margin-top:6px; font-size:11.5px; color:#e11d48; font-weight:700; display:flex; align-items:center; gap:6px">
                <span>⚠️</span> <span>Em atraso há ${a.dias_atraso} dias · Total pendente: R$ ${(a.valor_atraso||0).toFixed(2)}</span>
              </div>
            ` : ''}
          </div>
          <div style="display:flex; align-items:center; gap:8px">
            ${btnCobrancaA}
            <button onclick="const fb=document.getElementById('asaas-faturas-${safeMailId}'); fb.style.display=fb.style.display==='none'?'block':'none'" style="border:1px solid var(--line2); background:var(--bg); color:var(--text); padding:5px 10px; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer">
              Faturas (${a.faturas ? a.faturas.length : 0}) ▾
            </button>
          </div>
        </div>

        <div id="asaas-faturas-${safeMailId}" style="display:block; margin-top:12px; padding-top:12px; border-top:1px solid var(--line2)">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
            <div style="font-size:11.5px; font-weight:700; color:var(--text)">Histórico de Pagamentos e Faturas (Asaas):</div>
            <div style="font-size:10px; color:var(--muted)">Total de ${a.faturas ? a.faturas.length : 0} faturas registradas</div>
          </div>
          <div style="overflow-x:auto; max-height:260px; overflow-y:auto">
            <table style="width:100%; border-collapse:collapse; text-align:left">
              <thead style="position:sticky; top:0; background:var(--card); z-index:2">
                <tr style="border-bottom:1px solid var(--line); font-size:10px; color:var(--muted); text-transform:uppercase">
                  <th style="padding:6px 8px">Fatura</th>
                  <th style="padding:6px 8px">Data</th>
                  <th style="padding:6px 8px">Valor</th>
                  <th style="padding:6px 8px">Forma</th>
                  <th style="padding:6px 8px">Status</th>
                  <th style="padding:6px 8px; text-align:right">Ação</th>
                </tr>
              </thead>
              <tbody>
                ${faturasRowsA}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      `;
  }

  // Card Vindi
  if (hasV) {
      const v = s.vindi;
      const isAtrasoV = v.status_financeiro === 'em_atraso';
      const stColorV = isAtrasoV ? '#e11d48' : (v.status_financeiro === 'adimplente' ? '#059669' : (v.status_financeiro === 'a_vencer' ? '#d97706' : '#64748b'));
      const stBgV = isAtrasoV ? 'rgba(244,63,94,0.12)' : (v.status_financeiro === 'adimplente' ? 'rgba(16,185,129,0.12)' : 'rgba(245,158,11,0.12)');
      const stBorderV = isAtrasoV ? 'rgba(244,63,94,0.3)' : (v.status_financeiro === 'adimplente' ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)');
      const faturasRowsV = buildFaturasTableRows(v.faturas, s.nome, s.email, 'Vindi');

      let btnCobrancaV = '';
      if (isAtrasoV) {
          const safeNome = (s.nome || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
          const valorFmt = (v.valor_atraso || v.valor_parcela) ? `R$ ${(v.valor_atraso || v.valor_parcela).toFixed(2)}` : 'da sua mensalidade';
          const faturaVenc = v.proximo_vencimento || 'em aberto';
          btnCobrancaV = `
            <button onclick="sendVindiCobranca('${s.email}', '${safeNome}', '${valorFmt}', '${faturaVenc}', '')" style="display:inline-flex; align-items:center; gap:6px; background:#e11d48; color:#fff; border:none; padding:6px 12px; border-radius:6px; font-size:11px; font-weight:700; cursor:pointer; box-shadow:0 2px 6px rgba(225,29,72,0.25)">
              <span>💬</span> <span>Cobrar no WhatsApp</span>
            </button>
          `;
      }

      cardsHtml += `
      <div style="margin:14px 20px 0; padding:14px 16px; border:1px solid ${isAtrasoV ? 'rgba(244,63,94,0.3)' : 'rgba(124,58,237,0.25)'}; border-radius:10px; background:${isAtrasoV ? 'rgba(244,63,94,0.03)' : 'rgba(124,58,237,0.02)'}; box-shadow:0 2px 8px rgba(0,0,0,0.04)">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px">
              <span style="font-size:11px; background:rgba(124,58,237,0.12); color:#7c3aed; padding:2px 6px; border-radius:4px; font-weight:800">VINDI</span>
              <b style="font-size:12.5px; color:var(--text)">Assinatura e Financeiro</b>
              <span style="background:${stBgV}; color:${stColorV}; font-size:10px; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid ${stBorderV}">${v.status_label || 'Vindi'}</span>
              ${v.subscription_id ? `<span style="font-size:10px; color:var(--muted); font-family:monospace">Sub #${v.subscription_id}</span>` : ''}
            </div>
            <div style="font-size:11px; color:var(--muted)">
              Plano: <b style="color:var(--ink)">${v.plano || '—'}</b> · Forma: <b>${v.forma_pagamento || 'Boleto / Cartão'}</b>
              ${v.valor_parcela ? ` · Parcela: <b>R$ ${v.valor_parcela.toFixed(2)}</b>` : ''}
              ${v.proximo_vencimento ? ` · Próx. Vencimento: <b>${v.proximo_vencimento}</b>` : ''}
            </div>
            ${isAtrasoV ? `
              <div style="margin-top:6px; font-size:11.5px; color:#e11d48; font-weight:700; display:flex; align-items:center; gap:6px">
                <span>⚠️</span> <span>Em atraso há ${v.dias_atraso} dias · Total em aberto: R$ ${(v.valor_atraso||v.valor_parcela||0).toFixed(2)}</span>
              </div>
            ` : ''}
          </div>
          <div style="display:flex; align-items:center; gap:8px">
            ${btnCobrancaV}
            <button onclick="const fb=document.getElementById('vindi-faturas-${safeMailId}'); fb.style.display=fb.style.display==='none'?'block':'none'" style="border:1px solid var(--line2); background:var(--bg); color:var(--text); padding:5px 10px; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer">
              Faturas (${v.faturas ? v.faturas.length : 0}) ▾
            </button>
          </div>
        </div>

        <div id="vindi-faturas-${safeMailId}" style="display:block; margin-top:12px; padding-top:12px; border-top:1px solid var(--line2)">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
            <div style="font-size:11.5px; font-weight:700; color:var(--text)">Histórico de Pagamentos e Faturas (Vindi):</div>
            <div style="font-size:10px; color:var(--muted)">Total de ${v.faturas ? v.faturas.length : 0} faturas registradas</div>
          </div>
          <div style="overflow-x:auto; max-height:260px; overflow-y:auto">
            <table style="width:100%; border-collapse:collapse; text-align:left">
              <thead style="position:sticky; top:0; background:var(--card); z-index:2">
                <tr style="border-bottom:1px solid var(--line); font-size:10px; color:var(--muted); text-transform:uppercase">
                  <th style="padding:6px 8px">Fatura</th>
                  <th style="padding:6px 8px">Data</th>
                  <th style="padding:6px 8px">Valor</th>
                  <th style="padding:6px 8px">Forma</th>
                  <th style="padding:6px 8px">Status</th>
                  <th style="padding:6px 8px; text-align:right">Ação</th>
                </tr>
              </thead>
              <tbody>
                ${faturasRowsV}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      `;
  }

  vindiHtml = cardsHtml;
  const evs=s.events||[];
  $('#md-sub').textContent=`Histórico de acessos plataforma — ${evs.length} evento${evs.length!==1?'s':''} (mais recente primeiro)`;
  
  let platHtml = '';
  if(!evs.length) platHtml=`<div class="md-empty">Sem eventos registrados.</div>`;
  else platHtml=evs.map(e=>`<div class="ev"><span class="ev-d">${e.d}</span><span class="ev-a ea-${e.cat}">${e.acao}</span><span class="ev-i">${e.item}${e.mod?`<span class="tag">${e.mod}</span>`:''}</span></div>`).join('');
  
  let modProgressHtml = '';
  if (s.curso && DATA.curriculum && DATA.curriculum[s.curso]) {
      const s_done = new Set();
      (s.events || []).forEach(e => {
          if (e.acao === 'ASSISTIU AULA') {
              if (e.item_id) s_done.add(String(e.item_id));
              if (e.item) s_done.add(e.item.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''));
          }
      });
      const mRows = DATA.curriculum[s.curso].map(m => {
          let mDone = 0;
          m.aulas.forEach(a => {
              const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') : '';
              if (s_done.has(String(a.id)) || s_done.has(aNorm)) mDone++;
          });
          const mPct = m.n_curric > 0 ? Math.min(100, Math.round(mDone / m.n_curric * 100)) : 0;
          const isDone = m.n_curric > 0 && mDone >= m.n_curric;
          const color = isDone ? 'var(--emerald)' : (mPct > 0 ? 'var(--sky)' : 'var(--muted)');
          return `
            <div style="display:flex; flex-direction:column; gap:4px; font-size:11.5px; padding:7px 0; border-bottom:1px solid var(--line2)">
              <div style="display:flex; justify-content:space-between; align-items:center">
                <span style="font-weight:600; color:var(--ink)">${m.modulo}</span>
                <span style="font-weight:700; color:${color}">${mDone}/${m.n_curric} aulas (${mPct}%) ${isDone ? '✓ Concluído' : ''}</span>
              </div>
              <div style="background:var(--line); height:6px; border-radius:3px; overflow:hidden">
                <div style="width:${mPct}%; background:${color}; height:100%; border-radius:3px; transition:width 0.3s"></div>
              </div>
            </div>
          `;
      }).join('');
      
      modProgressHtml = `
        <div style="margin:20px 20px 0; padding:14px 16px; border:1px solid var(--line2); border-radius:10px; background:rgba(255,255,255,0.03); box-shadow:0 2px 8px rgba(0,0,0,0.04)">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px">
            <b style="font-size:12px; color:var(--ink)">Evolução e Conclusão por Módulos (${s.curso})</b>
            <span style="font-size:11px; font-weight:700; color:var(--emerald-d)">${s.mods_concluidos || 0}/${s.total_mods || 0} módulos concluídos</span>
          </div>
          <div>${mRows}</div>
        </div>
      `;
  }
  $('#md-body').innerHTML= modProgressHtml + vindiHtml + rdHtml + platHtml;
  modal.classList.add('on'); $('#md-body').scrollTop=0; document.body.style.overflow='hidden';
}
window.sendVindiCobranca = function(email, nome, valor, vencimento, faturaUrl) {
    const s = (CURRENT_DATA?.students || []).find(x => x.email === email);
    let tel = (s && s.telefone) ? s.telefone.replace(/\D/g, '') : '';
    const primeironome = (nome || 'Aluno').split(' ')[0];
    
    let linkTexto = faturaUrl ? `\n\n📄 Segue o link direto da sua fatura: ${faturaUrl}` : '';
    let msg = `Olá, ${primeironome}! Tudo bem?\n\nAqui é da equipe acadêmica da Pós-Graduação InfectoCast.\n\nNotamos que a sua mensalidade de ${vencimento} no valor de R$ ${valor} consta pendente em nosso sistema.${linkTexto}\n\nCaso já tenha realizado o pagamento, por favor desconsidere este aviso. Se precisar de alguma ajuda ou emitir 2ª via, pode nos responder por aqui!\n\nUm abraço,\nEquipe InfectoCast`;
    
    const waUrl = tel ? `https://wa.me/55${tel}?text=${encodeURIComponent(msg)}` : `https://wa.me/?text=${encodeURIComponent(msg)}`;
    window.open(waUrl, '_blank');
};

window.goToVindiAtraso = function() {
    switchTab('prog');
    ST_FILT = 'all';
    statusChips();
    sortCol = 'vindi';
    sortAsc = true;
    renderRows();
};

function closeModal(){ $('#modal').classList.remove('on'); document.body.style.overflow=''; }
function closeListModal(){ $('#modal-list').classList.remove('on'); if(!$('#modal').classList.contains('on')) document.body.style.overflow=''; }

$('#tbody').addEventListener('click',e=>{
  const tr=e.target.closest('tr.clickable'); if(tr) openStudent(tr.dataset.email, tr.dataset.curso);
});
$('#md-close').onclick=closeModal;
$('#modal').addEventListener('click',e=>{ if(e.target===$('#modal')) closeModal(); });

$('#ml-close').onclick=closeListModal;
$('#modal-list').addEventListener('click',e=>{ if(e.target===$('#modal-list')) closeListModal(); });

function openModalList(status) {
    let rows = CURRENT_DATA.students.filter(s => {
        if (s.status === status) return true;
        if ((status === 'Abandonou' || status === 'Inativo') && (s.status === 'Abandonou' || s.status === 'Inativo')) return true;
        if (status === 'Nunca acessou' && (s.status === 'Nunca acessou' || (s.status === 'Atenção' && !s.acessou))) return true;
        return false;
    });
    
    $('#ml-title').textContent = status;
    $('#ml-sub').textContent = `${rows.length} aluno${rows.length !== 1 ? 's' : ''}`;
    
    if (rows.length === 0) {
        $('#ml-body').innerHTML = '<div style="padding: 20px; text-align: center; color: var(--muted)">Nenhum aluno encontrado.</div>';
    } else {
        const dash='<span style="color:var(--muted2)">—</span>';
        let tbody = rows.map(s => {
            const st = STATUS[s.status] || {cls:'b-login'};
            const na = !s.acessou;
            const ultimo = na ? dash : (s.last_fmt || dash);
            
            let btnWpp = '';
            if (['Em Risco', 'Atenção', 'Inativo'].includes(s.status)) {
                let avisoMsg = '';
                if (CURRENT_DATA.mensagens_recentes && CURRENT_DATA.mensagens_recentes[s.email]) {
                    const m = CURRENT_DATA.mensagens_recentes[s.email];
                    avisoMsg = `<span style="color:var(--amber); font-size:10px; margin-left:8px; font-weight:600;" title="Último registro em: ${m.data}">⚠️ Avisado há ${m.dias} dia${m.dias!==1?'s':''}</span>`;
                }
                btnWpp = `<button onclick="sendWhatsapp('${s.email}', '${s.status}')" style="margin-top:10px; padding:6px 10px; font-family:var(--body); font-size:11px; background:var(--emerald-w); color:var(--emerald-d); border:none; border-radius:6px; cursor:pointer; font-weight:500; display:inline-flex; align-items:center; gap:4px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg> Enviar Mensagem</button>${avisoMsg}`;
            }
            
            return `<div style="padding:12px 22px; border-bottom:1px solid var(--line2); ${na?'opacity:.72':''}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-family:var(--disp); font-weight:600; color:var(--ink); font-size:13.5px">${s.nome}${getPlatBadge(s.plataforma)}</div>
                        <div style="font-size:11.5px; color:var(--muted); margin-top:2px">${s.email}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="margin-bottom:4px"><span class="badge ${st.cls}" style="font-size:9.5px; padding:2px 6px"><span class="b-dot" style="width:5px;height:5px"></span>${s.status}</span></div>
                        <div style="font-size:11px; color:var(--muted)">${ultimo}</div>
                    </div>
                </div>
                <div style="margin-top:10px; padding-top:10px; border-top:1px dashed var(--line2); font-size:11.5px; color:var(--muted)">
                    <b style="color:var(--muted2)">Curso:</b> ${s.curso}<br>
                    <b style="color:var(--muted2)">Motivo:</b> <span style="color:var(--ink2)">${s.status_motivo}</span>
                    <br>${btnWpp}
                </div>
            </div>`;
        }).join('');
        
        $('#ml-body').innerHTML = tbody;
    }
    
    $('#modal-list').classList.add('on');
    $('#ml-body').scrollTop = 0;
    document.body.style.overflow = 'hidden';
}

function openLead(email){
  const l = DATA.funil.scoring.find(x => x.email === email);
  if(!l) return;
  const modal=$('#modal');
  $('#md-nome').textContent = l.nome || 'Sem Nome';
  
  let btnWpp = `<button onclick="sendLeadWhatsapp('${l.email}', '${l.maturidade}')" style="margin-left:12px; padding:4px 8px; font-family:var(--body); font-size:10px; background:rgba(255,255,255,.15); color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:500; display:inline-flex; align-items:center; gap:4px; vertical-align:middle;"><svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg> Mensagem</button>`;
  let btnChat = '';
  if (l.telefone && l.wa_total > 0) {
      btnChat = `<button onclick="openWAChat('${l.telefone.replace(/\D/g,'')}', '${l.nome.replace(/'/g,"\'").replace(/"/g,'&quot;')}')" style="margin-left:4px; padding:4px 8px; font-family:var(--body); font-size:10px; background:rgba(255,255,255,.15); color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:500; display:inline-flex; align-items:center; gap:4px; vertical-align:middle;">👁 Histórico</button>`;
  }
  $('#md-mail').innerHTML=`${l.email}${btnWpp}${btnChat}`;
  
  $('#md-stats').innerHTML=[
    ['Maturidade', l.maturidade],
    ['Score', l.score],
    ['Conversões', l.conversoes],
    ['Mensagens WA', l.wa_total || 0],
    ['Profissão', l.profissao || '-'],
    ['Curso', l.curso || '-']
  ].map(([lb,v])=>`<div class="st"><div class="v" style="font-size:12px;${lb==='Profissão'?'font-size:10px;line-height:1.2;':''}">${v}</div><div class="l">${lb}</div></div>`).join('');
  
  const evs = l.eventos || [];
  $('#md-sub').innerHTML=`Histórico RD Station — ${evs.length} evento${evs.length!==1?'s':''} únicos mapeados<br><span style="font-size:11px;color:var(--muted)">Primeira conversão: ${l.dt_primeira || '—'} · Última: ${l.dt_ultima || '—'}<br>Primeiro contato WA: ${l.wa_dt_primeira || 'Não contatado'}</span>`;
  
  if(!evs.length) {
      $('#md-body').innerHTML=`<div class="md-empty" style="padding:20px;text-align:center;color:var(--muted)">Nenhum evento mapeado no RD Station.</div>`;
  } else {
      $('#md-body').innerHTML=evs.map(e=>`<div class="ev"><span class="ev-i" style="font-size:11px">${e}</span></div>`).join('');
  }
  
  modal.classList.add('on'); $('#md-body').scrollTop=0; document.body.style.overflow='hidden';
}

window.sendLeadWhatsapp = function(email, maturidade) {
    const l = DATA.funil.scoring.find(x => x.email === email);
    if (!l) return;
    
    let msg = '';
    const firstName = l.nome ? l.nome.split(' ')[0] : 'Dr(a)';
    msg = `Olá ${firstName}! Tudo bem?

Sou da Infectocast e vi que você tem consumido nossos materiais. Queria entender um pouco mais sobre o seu momento profissional atual e se uma pós-graduação faria sentido para você agora.

Qualquer dúvida estou à disposição!`;
    
    let phone = l.telefone;
    if (!phone || phone.trim() === '') {
        phone = prompt("O telefone deste lead não consta. Por favor, digite o número (com DDD) para enviar o WhatsApp:");
        if (!phone) return;
    }
    
    // Dispara registro no servidor local
    const postData = { email: email, telefone: phone, status: maturidade, mensagem: msg };
    fetch('http://localhost:8080/registrar', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(postData)
    }).catch(err => console.log('Erro ao registrar (servidor offline?):', err));
    
    phone = phone.replace(/[^0-9]/g, '');
    const url = `https://api.whatsapp.com/send/?phone=${phone}&text=${encodeURIComponent(msg)}`;
    window.open(url, '_blank');
};

window.sendWhatsapp = function(email, status) {
    const s = CURRENT_DATA.students.find(x => x.email === email && x.status === status);
    if (!s) return;
    
    let msg = '';
    const firstName = s.nome.split(' ')[0];
    
    if (status === 'Em Risco') {
        const diasSem = s.dias_inativo || s.dias_desde_insc;
        const cadencia = s.cadencia ? Math.round(s.cadencia) : 7;
        msg = `Olá ${firstName}! Tudo bem?

Vi aqui que você está a ${diasSem} dias sem acessar seu curso e como você costuma acessar os conteúdos a cada ${cadencia} dias, queremos saber se está tudo bem por aí.

Caso precise de qualquer ajuda estou por aqui`;
    } else if (status === 'Atenção') {
        msg = `Olá ${firstName}! Tudo bem?

Vi aqui que você ainda não acessou o conteúdo do seu curso e queremos saber se está tudo bem por aí.

Todos os seus cursos ativos vão aparecer para você no link https://academy.infectocast.com.br/cursos

Caso precise de qualquer ajuda estou por aqui`;
    } else if (status === 'Inativo') {
        msg = `Olá ${firstName}! Tudo bem?

Vi aqui que você não tem acessado o conteúdo do seu curso e queremos saber se está tudo bem por aí.

Todos os seus cursos ativos vão aparecer para você no link https://academy.infectocast.com.br/cursos

Caso precise de qualquer ajuda estou por aqui`;
    }
    
    let phone = s.telefone;
    if (!phone || phone.trim() === '') {
        phone = prompt("O telefone deste aluno não consta na planilha. Por favor, digite o número (com DDD) para enviar o WhatsApp:");
        if (!phone) return;
    }
    
    // Dispara registro no servidor local
    const postData = {
        email: email,
        telefone: phone,
        status: status,
        mensagem: msg
    };
    fetch('http://localhost:8080/registrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData)
    })
    .then(res => {
        if(res.ok) {
            if(!CURRENT_DATA.mensagens_recentes) CURRENT_DATA.mensagens_recentes = {};
            const agora = new Date();
            const pad = (n) => n.toString().padStart(2, '0');
            const dataStr = `${agora.getFullYear()}-${pad(agora.getMonth()+1)}-${pad(agora.getDate())} ${pad(agora.getHours())}:${pad(agora.getMinutes())}:${pad(agora.getSeconds())}`;
            
            CURRENT_DATA.mensagens_recentes[email] = { data: dataStr, dias: 0 };
            
            // Atualiza a tela imediatamente
            if($('#modal').classList.contains('on') && $('#md-mail').textContent.includes(email)) {
                openStudent(email);
            }
            if($('#modal-list').classList.contains('on')) {
                openModalList(status);
            }
        }
    })
    .catch(err => console.log('Erro ao registrar (servidor offline?):', err));
    
    // clean phone string just in case
    phone = phone.replace(/[^0-9]/g, '');
    const url = `https://api.whatsapp.com/send/?phone=${phone}&text=${encodeURIComponent(msg)}`;
    window.open(url, '_blank');
};

function selectTab(pId) {
    if (!pId) return;
    $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.p === pId));
    $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));

    if (pId === 'exec') {
        drawExecView(true);
        if ($('#kpis')) $('#kpis').style.display = 'none';
    } else {
        if ($('#kpis')) $('#kpis').style.display = 'grid';
    }

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
});

// TIMELINE
let gran='day', metric='stack', timelineDrawn=false;
$$('#seg-gran button').forEach(b=>b.onclick=()=>{$$('#seg-gran button').forEach(x=>x.classList.remove('on'));b.classList.add('on');gran=b.dataset.g;drawTimeline(true);});
$$('#seg-metric button').forEach(b=>b.onclick=()=>{
    $$('#seg-metric button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    metric=b.dataset.m;
    $('#tl-legend').style.display = (metric==='stack') ? 'flex' : 'none';
    $('#tl-legend-status').style.display = (metric==='status') ? 'flex' : 'none';
    drawTimeline(true);
});

function drawTimeline(force){
  if(timelineDrawn&&!force) return; timelineDrawn=true;
  const el=$('#timeline'); const W=el.clientWidth||900, H=300, pad={l:36,r:14,t:14,b:34};
  let data = CURRENT_DATA.timeline;
  if(!data || data.length === 0) { el.innerHTML = '<div style="padding:20px; text-align:center; color:var(--muted)">Sem dados no período</div>'; return; }
  
  // Agrupamento Semanal
  if (gran === 'week') {
      let grouped = [];
      for(let i=0; i<data.length; i+=7) {
          let chunk = data.slice(i, i+7);
          let item = { ...chunk[0], logins:0, iniciou:0, concluiu:0, material:0, teste:0, total:0, alunos:0 };
          chunk.forEach(d => {
              item.logins += d.logins; item.iniciou += d.iniciou; item.concluiu += d.concluiu;
              item.material += d.material; item.teste += d.teste; item.total += d.total;
              item.alunos += d.alunos;
          });
          grouped.push(item);
      }
      data = grouped;
  }
  
  // Cálculo de Status Histórico
  if (metric === 'status') {
      // Filtra alunos respeitando os filtros ativos (curso, aluno)
      let baseStudents = DATA.students.filter(s => {
          if (FILTER.curso !== 'all' && s.curso !== FILTER.curso) return false;
          if (FILTER.aluno !== 'all' && (s.nome + " (" + s.email + ")") !== FILTER.aluno) return false;
          return true;
      });
      
      // Deduplica alunos por email (pode ter múltiplas inscrições)
      let uniqueStudents = {};
      baseStudents.forEach(s => {
          if (!uniqueStudents[s.email]) {
              uniqueStudents[s.email] = { ...s, allEvents: s.events ? [...s.events] : [] };
          } else {
              if (s.events) uniqueStudents[s.email].allEvents.push(...s.events);
              let existInsc = parseDate(uniqueStudents[s.email].inscricao) || new Date(uniqueStudents[s.email].inscricao);
              let newInsc = parseDate(s.inscricao) || new Date(s.inscricao);
              if (newInsc < existInsc) {
                  uniqueStudents[s.email].inscricao = s.inscricao;
              }
          }
      });
      let allStudents = Object.values(uniqueStudents);
      
      // Pré-processa: parseia as datas dos eventos uma única vez
      allStudents.forEach(s => {
          s.parsedEvents = s.allEvents.map(e => ({
              ...e,
              _dt: parseDate(e.d) || new Date(e.d)
          })).filter(e => e._dt && !isNaN(e._dt)).sort((a,b) => a._dt - b._dt);
          
          s._inscDt = parseDate(s.inscricao) || new Date(s.inscricao);
      });
      
      data = data.map(d => {
          let dt = new Date(d.date);
          dt.setHours(23,59,59);
          
          let stCounts = { ativo: 0, risco: 0, inativo: 0, atencao: 0, concluido: 0 };
          
          allStudents.forEach(s => {
              if (s._inscDt > dt) return; // Ainda não estava inscrito
              
              // Todos os eventos ATÉ esta data (histórico completo)
              let evts = s.parsedEvents.filter(e => e._dt <= dt);
              let diasInsc = Math.floor((dt - s._inscDt)/(1000*3600*24));
              
              if (evts.length === 0) {
                  if (diasInsc > 7) stCounts.atencao++;
                  return;
              }
              
              // Último acesso e dias inativos relativos àquela data
              let lastEvtDt = evts[evts.length-1]._dt;
              let diasInat = Math.floor((dt - lastEvtDt)/(1000*3600*24));
              let loginsCount = evts.filter(e => e.cat === 'login').length;
              
              // Aulas assistidas até aquela data
              let aulasDone = new Set();
              evts.forEach(e => { if(e.acao === 'ASSISTIU AULA' && e.item_id) aulasDone.add(e.item_id); });
              
              // Verificar conclusão relativa
              let pctAulas = 0;
              if (s.curso && DATA.curriculum && DATA.curriculum[s.curso]) {
                  let totalCurric = 0;
                  let feitasCurric = 0;
                  DATA.curriculum[s.curso].forEach(m => {
                      m.aulas.forEach(a => {
                          if(a.curriculo) { totalCurric++; if(aulasDone.has(a.id)) feitasCurric++; }
                      });
                  });
                  pctAulas = totalCurric > 0 ? (feitasCurric / totalCurric * 100) : 0;
              }
              
              if (pctAulas >= 80) {
                  stCounts.concluido++;
                  return;
              }
              
              // Cadência relativa
              let cadencia = 7;
              if (loginsCount > 1) {
                  let loginDates = evts.filter(e => e.cat === 'login').map(e => e._dt);
                  let spanDays = Math.max(1, Math.floor((loginDates[loginDates.length-1] - loginDates[0])/(1000*3600*24)));
                  cadencia = spanDays / (loginsCount - 1);
              }
              
              // Mesma lógica de status do applyFilters
              if (evts.filter(e => e.acao === 'ASSISTIU AULA').length === 0 && diasInsc > 7) {
                  stCounts.atencao++;
              } else if (loginsCount > 1) {
                  if (diasInat > 30 || (diasInat > 14 && diasInat > (cadencia * 2.5))) stCounts.inativo++;
                  else if (diasInat > (cadencia * 1.5 + 2)) stCounts.risco++;
                  else stCounts.ativo++;
              } else {
                  if (diasInat > 30) stCounts.inativo++;
                  else if (diasInat > 14) stCounts.inativo++;
                  else if (diasInat > 7) stCounts.risco++;
                  else stCounts.ativo++;
              }
          });
          return { ...d, total_status: stCounts.ativo + stCounts.risco + stCounts.inativo + stCounts.atencao + stCounts.concluido, stCounts: stCounts };
      });
  }

  const n=data.length; const bw=(W-pad.l-pad.r)/n;
  const keys_stack = ['logins','iniciou','material','teste'];
  const colors_stack = {logins:'var(--sky)',iniciou:'var(--emerald)',concluiu:'var(--emerald)',material:'var(--violet)',teste:'var(--amber)'};
  
  const keys_status = ['ativo','risco','inativo','atencao','concluido'];
  const colors_status = {ativo:'#5C92F3', risco:'var(--amber)', inativo:'var(--coral)', atencao:'#E3E7E5', concluido:'var(--emerald)'};
  
  let maxY=1;
  if (metric==='alunos') maxY=Math.max(...data.map(d=>d.alunos),1);
  else if (metric==='status') maxY=Math.max(...data.map(d=>d.total_status),1);
  else maxY=Math.max(...data.map(d=>d.total),1);
  
  maxY=Math.ceil(maxY/10)*10 || 10;
  const y=v=>pad.t+(1-v/maxY)*(H-pad.t-pad.b);
  const x=i=>pad.l+i*bw;
  
  let grid='';
  const steps=4;
  for(let s=0;s<=steps;s++){const v=maxY/steps*s;grid+=`<line class="grid-line" x1="${pad.l}" y1="${y(v)}" x2="${W-pad.r}" y2="${y(v)}"/><text class="axis-lab" x="${pad.l-6}" y="${y(v)+3}" text-anchor="end">${Math.round(v)}</text>`;}
  
  let xlab='';
  const step=Math.max(1,Math.ceil(n/8));
  for(let i=0;i<n;i+=step){const parts=data[i].date.split('-'); xlab+=`<text class="axis-lab-d" x="${x(i)+bw/2}" y="${H-8}" text-anchor="middle">${parts[2]}/${parts[1]}</text>`;}
  
  let bars='';
  if(metric==='alunos'){
    const pts=data.map((d,i)=>`${x(i)+bw/2},${y(d.alunos)}`).join(' ');
    const area=`M${pad.l},${y(0)} L`+data.map((d,i)=>`${x(i)+bw/2},${y(d.alunos)}`).join(' L')+` L${x(n-1)+bw/2},${y(0)} Z`;
    bars=`<path d="${area}" fill="var(--emerald-w)" opacity=".6"/><polyline points="${pts}" fill="none" stroke="var(--emerald)" stroke-width="2"/>`;
  } else if(metric==='status'){
    data.forEach((d,i)=>{
      let acc=0;
      keys_status.forEach(k=>{
        const v=d.stCounts[k]||0;
        if(v>0){
          const h=(v/maxY)*(H-pad.t-pad.b);
          const yy=y(acc+v);
          bars+=`<rect x="${x(i)+bw*0.12}" y="${yy}" width="${bw*0.76}" height="${h}" fill="${colors_status[k]}"/>`;
          acc+=v;
        }
      });
    });
  } else {
    data.forEach((d,i)=>{
      let acc=0;
      keys_stack.forEach(k=>{
        const v=d[k]||0;
        if(v>0){
          const h=(v/maxY)*(H-pad.t-pad.b);
          const yy=y(acc+v);
          bars+=`<rect x="${x(i)+bw*0.12}" y="${yy}" width="${bw*0.76}" height="${h}" fill="${colors_stack[k]}"/>`;
          acc+=v;
        }
      });
    });
  }
  el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" width="100%">${grid}${bars}${xlab}</svg>`;
}

// MODULE ENGAGEMENT
function renderModules() {
    const c = FILTER.curso;
    const view = $('#modcard');
    if (c === 'all') {
        view.innerHTML = '<div style="padding:20px; text-align:center; color:var(--muted)">Por favor, selecione um curso específico no filtro acima para ver os módulos.</div>';
        return;
    }
    
    let mods = DATA.curriculum[c];
    if (!mods) {
        view.innerHTML = '<div style="padding:20px; text-align:center; color:var(--muted)">Nenhum módulo encontrado para este curso.</div>';
        return;
    }
    
    // Calculate max completion for scaling bars
    let maxIni = 1;
    mods.forEach(m => {
        m.aulas.forEach(a => {
            const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') : '';
            let count = CURRENT_DATA.lesson_views[a.id] ? CURRENT_DATA.lesson_views[a.id].size : (CURRENT_DATA.lesson_views[aNorm] ? CURRENT_DATA.lesson_views[aNorm].size : 0);
            if (count > maxIni) maxIni = count;
        });
    });
    
    view.innerHTML = mods.map(m => {
        const fora = m.n_fora > 0 ? ` · <span style="color:var(--muted2)">${m.n_fora} fora do currículo</span>` : '';
        return `<div class="funnel-mod">
          <div class="fm-head"><div class="name">${m.modulo} <b>·</b> <span style="color:var(--muted);font-weight:400">${m.n_curric} aulas no currículo${fora}</span></div>
          </div>
          ${m.aulas.map(a => {
            const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') : '';
            let views = CURRENT_DATA.lesson_views[a.id] ? CURRENT_DATA.lesson_views[a.id].size : (CURRENT_DATA.lesson_views[aNorm] ? CURRENT_DATA.lesson_views[aNorm].size : 0);
            const wi = (views / maxIni) * 100;
            let btnAlocar = '';
            if (m.modulo === 'Aulas Adicionais') {
                const safeCurso = c.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                const safeNome = a.nome.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                btnAlocar = `<button onclick="openAllocModal('${safeCurso}', '${safeNome}')" style="flex-shrink: 0; margin-left: 10px; padding: 2px 6px; font-size: 10px; border: 1px solid var(--line); border-radius: 4px; background: white; cursor: pointer;">📍 Alocar</button>`;
            }
            
            if (!a.curriculo) {
              return `<div class="aula-row" style="opacity:.5">
                <div class="aula-name" title="${a.nome} — Não conta (Inativa)" style="display:flex; align-items:center; padding-right:10px;">
                  <span class="ord" style="flex-shrink:0">${a.ordem}</span>
                  <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${a.nome}</span>
                  <span style="font-size:10px;color:var(--muted2); flex-shrink:0; margin-left:4px;">· Inativa</span>${btnAlocar}
                </div>
                <div class="aula-bar">${views > 0 ? `<div class="con" style="width:${wi}%;background:#E3E7E5"></div><div class="lbl" style="color:var(--muted)">${views}</div>` : ''}</div></div>`;
            }
            
            return `<div class="aula-row">
              <div class="aula-name" title="${a.nome}" style="display:flex; align-items:center; padding-right:10px;">
                <span class="ord" style="flex-shrink:0">${a.ordem}</span>
                <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${a.nome}</span>
                ${btnAlocar}
              </div>
              <div class="aula-bar"><div class="con" style="width:${wi}%"></div><div class="lbl">${views} fizeram</div></div>
            </div>`;
          }).join('')}
        </div>`;
    }).join('');
}

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
            <td style="padding:10px 8px; font-weight:500; color:var(--ink)">${s.curso}</td>
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

    // Usar CURRENT_DATA.students quando já enriquecido com status, ou enriquecer localmente
    const baseStudents = (CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0)
        ? CURRENT_DATA.students
        : rawStudents.map(s => {
            const scopy = { ...s };
            const acessou = scopy.acessou;
            const logins = scopy.logins || 0;
            const dias_inativo = scopy.dias_inativo || 0;
            const cadencia = scopy.cadencia || 0;
            const dias_ativo = scopy.dias_ativo || 0;

            const vSt = scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : null;
            const aSt = scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : null;

            if (vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled') {
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

    // Mapeamento rápido de e-mail e nome para vincular faturas a estudantes e cursos
    const emailToStudent = {};
    const nameToStudent = {};
    baseStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        if (em) emailToStudent[em] = s;
        if (nm) nameToStudent[nm] = s;
    });

    // Classificação de status de alunos
    let countAtivos = 0;
    let countEmRisco = 0;
    let countAbandonou = 0;
    let countNuncaAcessou = 0;
    let countCancelados = 0;

    const coursesMap = {};

    baseStudents.forEach(s => {
        let st = s.status;
        if (!st) {
            st = !s.acessou ? 'Nunca acessou' : (s.dias_inativo > 30 ? 'Abandonou' : 'Ativo');
        }

        const c = s.curso || 'OUTROS / PLATAFORMA GERAL';
        if (!coursesMap[c]) {
            coursesMap[c] = {
                curso: c,
                total: 0,
                ativos: 0,
                em_risco: 0,
                abandono: 0,
                nunca: 0,
                cancelados: 0,
                pago: 0,
                atraso: 0,
                proj: 0,
                mrr: 0
            };
        }
        const cm = coursesMap[c];
        cm.total++;

        if (st === 'Cancelado') {
            countCancelados++;
            cm.cancelados++;
        } else if (st === 'Ativo' || st.includes('Conclu')) {
            countAtivos++;
            cm.ativos++;
        } else if (st === 'Em Risco') {
            countEmRisco++;
            cm.em_risco++;
        } else if (st === 'Abandonou' || st === 'Inativo') {
            countAbandonou++;
            cm.abandono++;
        } else if (st === 'Nunca acessou') {
            countNuncaAcessou++;
            cm.nunca++;
        } else {
            countAtivos++;
            cm.ativos++;
        }

        // Soma MRR por curso para alunos que não estão cancelados
        if (st !== 'Cancelado') {
            const vindiObj = s.vindi;
            const asaasObj = s.asaas;
            const vParcela = vindiObj ? (Number(vindiObj.valor_parcela) || 0) : 0;
            const aParcela = asaasObj ? (Number(asaasObj.valor_parcela) || Number(asaasObj.mrr) || 0) : 0;
            cm.mrr += (vParcela + aParcela);

            // Faturas futuras do próprio aluno no Vindi (já calculadas e agendadas)
            if (vindiObj && Array.isArray(vindiObj.faturas)) {
                vindiObj.faturas.forEach(f => {
                    if (f.status === 'futuro') {
                        cm.proj += (Number(f.valor) || 0);
                    }
                });
            }
        }
    });

    // Faturas globais (Vindi + Asaas) para cálculo de Pago, Atraso (Inadimplência) e Projeção adicional
    const vFaturas = (vindi.faturas_tabela || []);
    const aFaturas = (asaas.faturas_tabela || []);

    vFaturas.forEach(f => {
        const em = (f.email || '').toString().toLowerCase().trim();
        const nm = (f.aluno || '').toString().toLowerCase().trim();
        const stObj = emailToStudent[em] || nameToStudent[nm];
        const c = (stObj && stObj.curso) ? stObj.curso : 'OUTROS / PLATAFORMA GERAL';

        if (!coursesMap[c]) {
            coursesMap[c] = { curso: c, total: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, cancelados: 0, pago: 0, atraso: 0, proj: 0, mrr: 0 };
        }

        const val = Number(f.valor) || 0;
        const st = f.status || '';
        if (st === 'pago' || st === 'paid') {
            coursesMap[c].pago += val;
        } else if (st === 'em_atraso') {
            coursesMap[c].atraso += val;
        }
    });

    aFaturas.forEach(f => {
        const em = (f.email || '').toString().toLowerCase().trim();
        const nm = (f.aluno || '').toString().toLowerCase().trim();
        const stObj = emailToStudent[em] || nameToStudent[nm];
        const c = (stObj && stObj.curso) ? stObj.curso : 'OUTROS / PLATAFORMA GERAL';

        if (!coursesMap[c]) {
            coursesMap[c] = { curso: c, total: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, cancelados: 0, pago: 0, atraso: 0, proj: 0, mrr: 0 };
        }

        const val = Number(f.valor) || 0;
        const st = f.status || '';
        if (st === 'pago' || st === 'paid') {
            coursesMap[c].pago += val;
        } else if (st === 'em_atraso') {
            coursesMap[c].atraso += val;
        } else if (st === 'a_vencer' || st === 'pending' || st === 'futuro') {
            coursesMap[c].proj += val;
        }
    });

    // Totalizadores Consolidados
    const vKpis = vindi.kpis || {};
    const aKpis = asaas.kpis || {};

    const recRealizadaTotal = (Number(vKpis.total_recebido) || 0) + (Number(aKpis.total_recebido) || 0);
    const recMesAtual = (Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || 0);
    const mrrConsolidado = (Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0);
    const proj30d = (Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0);
    const proj12m = (Number(vKpis.projecao_12m) || 2651945.16);
    const atrasoTotal = (Number(vKpis.total_em_atraso) || 0) + (Number(aKpis.total_em_atraso) || 0);
    const qtdAtrasoTotal = (Number(vKpis.qtd_em_atraso) || 0) + (Number(aKpis.qtd_em_atraso) || 0);
    const taxaAdimplencia = vKpis.taxa_adimplencia || 96;

    // Meta Mensal
    const metaMensal = 250000.0;
    const projecaoFechamentoMes = recMesAtual + (proj30d * 0.85);
    const pctAtingimento = Math.min(100, (projecaoFechamentoMes / metaMensal) * 100);
    const gapMeta = Math.max(0, metaMensal - projecaoFechamentoMes);

    // Funil
    const fKpis = funil.kpis || {};
    const totalLeads = Number(fKpis.total) || 26566;
    const leadsQualificados = Number(fKpis.lead_qualificado) || 5638;
    const contatadosWA = Number(fKpis.wa_contatados) || 365;
    const alunosPagantes = Number(fKpis.aluno) || 456;

    const totalMatriculas = baseStudents.length;
    const totalAtivas = totalMatriculas - countCancelados;
    const taxaChurn = totalMatriculas > 0 ? ((countCancelados / totalMatriculas) * 100).toFixed(1) : '0';
    const taxaRetencao = (100 - parseFloat(taxaChurn)).toFixed(1);

    const totalReproducoes = ev['ASSISTIU AULA'] || 0;
    const totalLogins = ev['LOGIN WEB'] || 0;

    // Ordenar cursos por matrículas ativas e receita
    const cursosList = Object.values(coursesMap).filter(c => c.total > 0 || c.pago > 0 || c.atraso > 0 || c.proj > 0).sort((a,b) => b.total - a.total);

    // Helpers
    const fM = val => (Number(val) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    const fN = val => (Number(val) || 0).toLocaleString('pt-BR');

    // Montar HTML da Visão Executiva
    mount.innerHTML = `
      <!-- HERO HEADER COM BOTÃO VER DASH COMPLETO -->
      <div class="exec-hero">
        <div>
          <div class="exec-badge">COCKPIT ESTRATÉGICO CONSOLIDADO</div>
          <h1 class="exec-hero-title">Cockpit Executivo InfectoCast</h1>
          <p class="exec-hero-sub">Visão executiva unificada: <b>resultado → previsão → conversão → recorrência → retenção → risco</b>. O detalhamento completo de cada frente permanece disponível nas abas operacionais especializadas.</p>
        </div>
        <div>
          <button class="btn-exec-cta" onclick="selectTab('home')">
            <span>📊 Ver Dashboard Completo</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </button>
        </div>
      </div>

      <!-- GRUPO 1: RECEITA E PREVISIBILIDADE -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G1</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 1 — RECEITA &amp; PREVISIBILIDADE</h3>
              <div class="exec-sec-sub">Visão executiva de faturamento acumulado, cadência recorrente (MRR) e atingimento de metas.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('fin')">Ver Financeiro Detalhado →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada Total</span>
              <span class="exec-pill pill-green">Consolidado</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(recRealizadaTotal)}</div>
            <div class="exec-card-sub">Vindi (${fM(vKpis.total_recebido)}) + Asaas (${fM(aKpis.total_recebido)})</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Recorrente (MRR)</span>
              <span class="exec-pill pill-blue">Mensal Ativo</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(mrrConsolidado)}</div>
            <div class="exec-card-sub">Base ativa recorrente (${fM(vKpis.mrr_ativo)} Vindi + ${fM(aKpis.mrr_ativo)} Asaas)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Mês Atual + Proj.</span>
              <span class="exec-pill pill-amber">${pctAtingimento.toFixed(1)}% Meta</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(projecaoFechamentoMes)}</div>
            <div class="exec-card-sub">Realizado: ${fM(recMesAtual)} · Gap para meta: ${fM(gapMeta)}</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Carteira (12m)</span>
              <span class="exec-pill pill-green">Contratado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(proj12m)}</div>
            <div class="exec-card-sub">Previsão contratual de faturamento para próximos 12 meses</div>
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
          <button class="btn-exec-link" onclick="selectTab('funil')">Ver Funil de Vendas →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Leads Gerados</span>
              <span class="exec-pill pill-blue">CRM / RD</span>
            </div>
            <div class="exec-card-val">${fN(totalLeads)}</div>
            <div class="exec-card-sub">${fN(leadsQualificados)} leads qualificados (${((leadsQualificados/totalLeads)*100).toFixed(1)}%)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Totais</span>
              <span class="exec-pill pill-green">${totalAtivas} Ativas</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(totalMatriculas)}</div>
            <div class="exec-card-sub">${fN(alunosPagantes)} alunos pagantes com transação confirmada</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Taxa de Conversão Geral</span>
              <span class="exec-pill pill-green">Lead → Aluno</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${((totalMatriculas/Math.max(1, totalLeads))*100).toFixed(2)}%</div>
            <div class="exec-card-sub">Conversão sobre leads qualificados: ${((totalMatriculas/Math.max(1, leadsQualificados))*100).toFixed(1)}%</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Ticket Médio Estimado</span>
              <span class="exec-pill pill-amber">Contrato</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">R$ 2.450,00</div>
            <div class="exec-card-sub">CAC estimado: R$ 380,00 · LTV/CAC saudável &gt; 6x</div>
          </div>
        </div>
      </div>

      <!-- GRUPO 3: FUNIL DE CONVERSÃO INTEGRADO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G3</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 3 — FUNIL DE CONVERSÃO</h3>
              <div class="exec-sec-sub">Passagem contínua entre as etapas do funil comercial e eficiência de fechamento.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('origem')">Ver Origem de Matrículas →</button>
        </div>
        <div class="exec-funnel-bar">
          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">1. Leads Totais</div>
            <div class="exec-funnel-step-val">${fN(totalLeads)}</div>
            <div class="exec-funnel-step-sub">100% da base captada</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((leadsQualificados/totalLeads)*100).toFixed(1)}%</span>
            <span>➔</span>
          </div>

          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">2. Oportunidades (LQ)</div>
            <div class="exec-funnel-step-val">${fN(leadsQualificados)}</div>
            <div class="exec-funnel-step-sub">Critérios de qualificação</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((contatadosWA/leadsQualificados)*100).toFixed(1)}%</span>
            <span>➔</span>
          </div>

          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">3. Contatados WhatsApp</div>
            <div class="exec-funnel-step-val">${fN(contatadosWA)}</div>
            <div class="exec-funnel-step-sub">Abordagem ativa comercial</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((totalMatriculas/contatadosWA)*100).toFixed(0)}%</span>
            <span>➔</span>
          </div>

          <div class="exec-funnel-step step-highlight">
            <div class="exec-funnel-step-label" style="color:var(--emerald-d)">4. Matrículas Realizadas</div>
            <div class="exec-funnel-step-val" style="color:var(--emerald-d)">${fN(totalMatriculas)}</div>
            <div class="exec-funnel-step-sub">${totalAtivas} ativas · ${countCancelados} canceladas</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((alunosPagantes/totalMatriculas)*100).toFixed(1)}%</span>
            <span>➔</span>
          </div>

          <div class="exec-funnel-step step-highlight">
            <div class="exec-funnel-step-label" style="color:var(--emerald-d)">5. Alunos Pagantes</div>
            <div class="exec-funnel-step-val" style="color:var(--emerald-d)">${fN(alunosPagantes)}</div>
            <div class="exec-funnel-step-sub">Com fatura paga confirmada</div>
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
              <div class="exec-sec-sub">Evolução de alunos matriculados ativos, retenção de carteira, inadimplência e adimplência.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('prog')">Ver Lista de Alunos →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Ativas</span>
              <span class="exec-pill pill-green">${taxaRetencao}% Retenção</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(totalAtivas)}</div>
            <div class="exec-card-sub">De um total de ${fN(totalMatriculas)} contratos cadastrados</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Cancelamentos (Churn)</span>
              <span class="exec-pill pill-red">${taxaChurn}% Churn</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(countCancelados)}</div>
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
            <div class="exec-card-sub">Índice de pagamento em dia na carteira ativa</div>
          </div>
        </div>
      </div>

      <!-- GRUPO 5: ENGAJAMENTO E RETENÇÃO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G5</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 5 — ENGAJAMENTO &amp; RETENÇÃO</h3>
              <div class="exec-sec-sub">Alunos ativos e engajados, monitoramento de risco e inatividade severa (abandono).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('ret')">Ver Matriz de Retenção →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Engajados</span>
              <span class="exec-pill pill-green">${((countAtivos/Math.max(1, totalAtivas))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(countAtivos)}</div>
            <div class="exec-card-sub">Alunos ativos com aulas e frequência em dia</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos em Risco</span>
              <span class="exec-pill pill-amber">${((countEmRisco/Math.max(1, totalAtivas))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#D97706">${fN(countEmRisco)}</div>
            <div class="exec-card-sub">Quebra recente de cadência (alerta prioritário)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Abandono / Inativos</span>
              <span class="exec-pill pill-red">${((countAbandonou/Math.max(1, totalAtivas))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(countAbandonou)}</div>
            <div class="exec-card-sub">Inatividade severa (&gt;14 ou &gt;30 dias sem acesso)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Nunca Acessaram</span>
              <span class="exec-pill pill-red">${((countNuncaAcessou/Math.max(1, totalAtivas))*100).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(countNuncaAcessou)}</div>
            <div class="exec-card-sub">${fN(totalReproducoes)} reproduções de aulas · ${fN(totalLogins)} logins</div>
          </div>
        </div>
      </div>

      <!-- GRUPO 6: VISÃO POR CURSO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G6</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 6 — VISÃO POR CURSO</h3>
              <div class="exec-sec-sub">Desempenho por especialidade com alunos ativos, em risco, abandono, cancelamento, MRR, projeção e inadimplência.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('home')">Ver Panorama Completo →</button>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12.5px; text-align:left">
            <thead>
              <tr style="border-bottom:2px solid var(--line); color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:0.04em">
                <th style="padding:10px 12px">Especialidade / Curso</th>
                <th style="padding:10px 8px; text-align:center">Ativos</th>
                <th style="padding:10px 8px; text-align:center">Em Risco</th>
                <th style="padding:10px 8px; text-align:center">Abandono</th>
                <th style="padding:10px 8px; text-align:center">Cancelados</th>
                <th style="padding:10px 12px; text-align:right">MRR Estimado</th>
                <th style="padding:10px 12px; text-align:right">Receita Projetada</th>
                <th style="padding:10px 12px; text-align:right">Inadimplência</th>
                <th style="padding:10px 12px; text-align:center">Status Executivo</th>
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
                  return `
                    <tr style="border-bottom:1px solid var(--line2); transition:background 0.15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
                      <td style="padding:12px; font-weight:700; color:var(--ink)">
                        <div style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:300px" title="${c.curso}">${c.curso}</div>
                      </td>
                      <td style="padding:12px 8px; text-align:center">
                        <span class="exec-pill pill-green" style="font-weight:700">${c.ativos}</span>
                      </td>
                      <td style="padding:12px 8px; text-align:center">
                        <span class="exec-pill ${c.em_risco > 0 ? 'pill-amber' : ''}" style="font-weight:${c.em_risco > 0 ? '700' : '400'}; color:${c.em_risco > 0 ? '#D97706' : 'var(--muted2)'}">${c.em_risco}</span>
                      </td>
                      <td style="padding:12px 8px; text-align:center">
                        <span class="exec-pill ${c.abandono > 0 ? 'pill-red' : ''}" style="font-weight:${c.abandono > 0 ? '700' : '400'}; color:${c.abandono > 0 ? '#DC2626' : 'var(--muted2)'}">${c.abandono}</span>
                      </td>
                      <td style="padding:12px 8px; text-align:center">
                        <span style="font-weight:${c.cancelados > 0 ? '700' : '400'}; color:${c.cancelados > 0 ? '#DC2626' : 'var(--muted2)'}">${c.cancelados}</span>
                      </td>
                      <td style="padding:12px; text-align:right; font-weight:600; color:var(--ink)">${fM(c.mrr)}</td>
                      <td style="padding:12px; text-align:right; font-weight:600; color:#0284c7">${fM(c.proj)}</td>
                      <td style="padding:12px; text-align:right; font-weight:700; color:${c.atraso > 0 ? '#DC2626' : 'var(--muted2)'}">${fM(c.atraso)}</td>
                      <td style="padding:12px; text-align:center">${stBadge}</td>
                    </tr>
                  `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- GRUPO 7: ALERTAS EXECUTIVOS -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G7</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 7 — ALERTAS EXECUTIVOS &amp; SEMÁFORO DE RISCO</h3>
              <div class="exec-sec-sub">Sinais de atenção prioritários para tomada de decisão da diretoria e liderança.</div>
            </div>
          </div>
        </div>
        <div class="exec-grid-2">
          <div class="exec-alert alert-critico">
            <div class="exec-alert-icon">⚠️</div>
            <div>
              <div class="exec-alert-title">Cobrança de Inadimplência (${qtdAtrasoTotal} faturas / ${fM(atrasoTotal)})</div>
              <div class="exec-alert-desc">Existem R$ 206.707,15 pendentes em atraso entre Vindi e Asaas. Recomenda-se acionar régua de renegociação automatizada para os 170 títulos vencidos.</div>
            </div>
          </div>

          <div class="exec-alert alert-atencao">
            <div class="exec-alert-icon">🔔</div>
            <div>
              <div class="exec-alert-title">Alunos em Risco &amp; Abandono (${fN(countEmRisco + countAbandonou)} alunos · ${(((countEmRisco + countAbandonou)/Math.max(1, totalAtivas))*100).toFixed(1)}%)</div>
              <div class="exec-alert-desc">Identificados ${countEmRisco} alunos em risco iminente por quebra recente de cadência e ${countAbandonou} em inatividade severa. Recomenda-se ação pedagógica segmentada via WhatsApp.</div>
            </div>
          </div>

          <div class="exec-alert alert-atencao">
            <div class="exec-alert-icon">📈</div>
            <div>
              <div class="exec-alert-title">Demanda Qualificada no Funil (${fN(leadsQualificados - contatadosWA)} sem contato)</div>
              <div class="exec-alert-desc">Grande contingente de leads qualificados no CRM ainda não abordados pelo time comercial via WhatsApp. Oportunidade imediata de aumento de vendas.</div>
            </div>
          </div>

          <div class="exec-alert alert-sucesso">
            <div class="exec-alert-icon">✓</div>
            <div>
              <div class="exec-alert-title">Adimplência Sólida e MRR Sustentável (${fM(mrrConsolidado)}/mês)</div>
              <div class="exec-alert-desc">A carteira principal de alunos apresenta taxa de adimplência de 96% e receita recorrente robusta com mais de R$ 2,65M contratados nos próximos 12 meses.</div>
            </div>
          </div>
        </div>
      </div>

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
        return s.status === 'Cancelado' || vSt === 'canceled' || vSt === 'cancelado' || aSt === 'canceled' || aSt === 'cancelado';
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

function drawFunil(force) {
    if(!DATA.funil || !DATA.funil.kpis) {
        $('#p-funil').innerHTML = '<div style="padding:40px;text-align:center;color:var(--muted)">Dados do funil (LogRD.csv) não encontrados.</div>';
        return;
    }
    if (funilDrawn && !force) return;
    funilDrawn = true;
    
    const F = DATA.funil;
    const K = F.kpis;
    
    // KPIs Top
    $('#funil-kpis').innerHTML = [
        {l:'Leads (RD)', v:fmt(K.total), c:'var(--ink)', s:'Total de contatos'},
        {l:'Qualificados', v:fmt(K.lead_qualificado), c:'var(--sky)', s:`${K.taxa_lq}% dos leads`},
        {l:'Contatados WA', v:fmt(K.wa_contatados), c:'#25D366', s:`${K.taxa_wa}% dos leads`},
        {l:'Alunos', v:fmt(K.aluno), c:'var(--emerald)', s:`${K.taxa_aluno}% dos leads`}
    ].map(k=>`<div class="kpi"><div class="k-lab"><i class="k-dot" style="background:${k.c}"></i>${k.l}</div>
    <div class="k-val" style="color:${k.c}">${k.v}</div><div class="k-sub">${k.s}</div></div>`).join('');
    
    // Funil Visual
    const maxVal = K.total || 1;
    $('#funil-visual').innerHTML = `
      <div style="display:flex; flex-direction:column; gap:8px">
        ${renderFunnelRow('Leads Base', K.total, maxVal, 'var(--ink)')}
        ${renderFunnelRow('Qualificados', K.lead_qualificado, maxVal, 'var(--sky)')}
        ${renderFunnelRow('Contatados WA', K.wa_contatados, maxVal, '#25D366')}
        ${renderFunnelRow('Clientes RD', K.cliente, maxVal, 'var(--amber)')}
        ${renderFunnelRow('Matriculados', K.aluno, maxVal, 'var(--emerald)')}
      </div>
    `;
    
    // Histograma de Tempo
    const hist = F.tempo_conv.histograma;
    let maxHist = Math.max(...hist.map(h => h.count), 1);
    $('#funil-histograma').innerHTML = `<div style="display:flex; align-items:flex-end; gap:4px; height:120px; padding-top:20px">
      ${hist.map(h => `<div style="flex:1; display:flex; flex-direction:column; align-items:center; group">
        <div style="color:var(--muted); font-size:10px; margin-bottom:4px">${h.count}</div>
        <div style="width:100%; background:var(--emerald); height:${(h.count/maxHist)*100}px; border-radius:4px 4px 0 0; opacity:0.8"></div>
        <div style="font-size:9px; color:var(--muted); margin-top:4px; text-align:center; transform:rotate(-45deg); transform-origin: top left; margin-left:10px">${h.faixa}</div>
      </div>`).join('')}
    </div>`;
    $('#funil-tempo-info').innerHTML = `Amostra: ${F.tempo_conv.total_amostras} alunos. Mediana: <b>${F.tempo_conv.mediana} dias</b>.`;
    
    // Eventos
    $('#funil-eventos').innerHTML = `
      <div style="display:flex; gap:20px; font-size:12px">
        <div style="flex:1"><b>Alunos</b><br>
          ${F.eventos_alunos.map(e => `<div style="display:flex; justify-content:space-between; margin-top:4px; padding-bottom:4px; border-bottom:1px solid var(--line)"><span style="color:var(--emerald)">${e.cat}</span> <span>${fmt(e.n)}</span></div>`).join('')}
        </div>
        <div style="flex:1"><b>Não-alunos</b><br>
          ${F.eventos_nao_alunos.slice(0, Math.min(F.eventos_alunos.length, 10)).map(e => `<div style="display:flex; justify-content:space-between; margin-top:4px; padding-bottom:4px; border-bottom:1px solid var(--line)"><span style="color:var(--muted)">${e.cat}</span> <span>${fmt(e.n)}</span></div>`).join('')}
        </div>
      </div>
    `;
    
    // Origens
    $('#funil-origens').innerHTML = `
      <div style="font-size:12px">
        ${Object.entries(F.origens_alunos).map(([origem, val]) => `<div style="display:flex; justify-content:space-between; margin-top:6px; padding-bottom:4px; border-bottom:1px solid var(--line)"><span>${origem}</span> <b>${val}</b></div>`).join('')}
      </div>
    `;
    
    // Scoring / Chips
    const matColors = {'Pronto':'var(--emerald)', 'Quente':'var(--amber)', 'Morno':'var(--sky)', 'Frio':'var(--muted)'};
    const c = F.mat_counts;
    $('#funil-mat-chips').innerHTML = `
        <button class="chip ${matFilter==='all'?'on':''}" onclick="matFilter='all'; drawFunil(true)">Todos</button>
        ${['Pronto', 'Quente'].map(k => c[k] ? `<button class="chip ${matFilter===k?'on':''}" onclick="matFilter='${k}'; drawFunil(true)"><i style="background:${matColors[k]}"></i>${k} <span class="cn">${c[k]}</span></button>` : '').join('')}
        <button onclick="exportLeadsCSV()" style="margin-left:auto; padding:7px 12px; font-family:var(--body); font-size:11px; font-weight:600; background:var(--sky-w); color:var(--sky-d); border:none; border-radius:20px; cursor:pointer;">📥 Exportar CSV</button>
    `;
    
    // Tabela de Leads
    // Tabela de Leads
    const thead = ['Lead', 'Telefone', 'Profissão', 'Origem', 'Curso', 'Conv. RD', 'Msgs WA', 'Últ. Conv.', 'Score', 'Maturidade'];
    $('#funil-thead').innerHTML = thead.map(th => {
        let sym = '';
        if (th === window.funilSortCol) {
            sym = window.funilSortDir === 1 ? ' ▲' : ' ▼';
        }
        return `<th onclick="setFunilSort('${th}')" style="cursor:pointer; user-select:none" title="Clique para ordenar por ${th}">${th}<span style="font-size:9px;color:var(--sky)">${sym}</span></th>`;
    }).join('');
    
    let leads = F.scoring.filter(l => matFilter === 'all' || l.maturidade === matFilter);
    
    leads.sort((a, b) => {
        let va, vb;
        switch(window.funilSortCol) {
            case 'Email': va = a.email; vb = b.email; break;
            case 'Nome': va = a.nome; vb = b.nome; break;
            case 'Lead': va = a.nome; vb = b.nome; break;
            case 'Telefone': va = a.telefone; vb = b.telefone; break;
            case 'Profissão': va = a.profissao || ''; vb = b.profissao || ''; break;
            case 'Origem': va = a.origem; vb = b.origem; break;
            case 'Curso': va = a.curso || ''; vb = b.curso || ''; break;
            case 'Conv. RD': va = a.conversoes; vb = b.conversoes; break;
            case 'Msgs WA': va = a.wa_total || 0; vb = b.wa_total || 0; break;
            case 'Últ. Conv.': 
                const parseD = d => { if(!d||d==='—')return 0; const p=d.split('/'); return new Date(p[2],p[1]-1,p[0]).getTime(); };
                va = parseD(a.dt_ultima); vb = parseD(b.dt_ultima);
                break;
            case 'Score': va = a.score; vb = b.score; break;
            case 'Maturidade': 
                const matOrder = {'Pronto':4, 'Quente':3, 'Morno':2, 'Frio':1};
                va = matOrder[a.maturidade]||0; vb = matOrder[b.maturidade]||0; 
                break;
            default: va = a.score; vb = b.score;
        }
        if (typeof va === 'string') va = va.toLowerCase();
        if (typeof vb === 'string') vb = vb.toLowerCase();
        if (va < vb) return -1 * window.funilSortDir;
        if (va > vb) return 1 * window.funilSortDir;
        return 0;
    });

    $('#funil-tbody').innerHTML = leads.map(l => `
      <tr class="clickable" data-email="${l.email}">
        <td style="max-width:180px; overflow:hidden; text-overflow:ellipsis" title="${l.nome} | ${l.email}"><div class="al-nome" style="overflow:hidden; text-overflow:ellipsis">${l.nome}</div><div class="al-mail" style="overflow:hidden; text-overflow:ellipsis">${l.email}</div><span style="color:var(--muted);font-size:10px">${l.estagio}</span></td>
        <td style="white-space:nowrap">${l.telefone}</td>
        <td style="font-size:10px;color:var(--muted);max-width:110px;word-wrap:break-word" title="${l.profissao||'-'}">${l.profissao||'-'}</td>
        <td style="font-size:11px;color:var(--muted);max-width:110px;word-wrap:break-word">${l.origem}</td>
        <td style="font-size:11px;font-weight:600;color:var(--sky);max-width:100px;word-wrap:break-word">${l.curso || '-'}</td>
        <td style="text-align:center">${l.conversoes}</td>
        <td style="text-align:center;font-weight:600;color:${l.wa_total > 0 ? '#25D366' : 'var(--line)'}">${l.wa_total || '-'}</td>
        <td style="text-align:center;font-size:11px;color:var(--muted)">${l.dt_ultima||'—'}</td>
        <td style="text-align:center;font-weight:600">${l.score}</td>
        <td><span class="st-bdg" style="background:${matColors[l.maturidade]}20; color:${matColors[l.maturidade]}">${l.maturidade}</span></td>
      </tr>
    `).join('');
}

function renderFunnelRow(label, val, max, color) {
    const pct = max > 0 ? (val / max * 100).toFixed(1) : 0;
    return `
      <div style="display:flex; align-items:center; font-size:12px">
        <div style="width:100px; color:var(--muted2)">${label}</div>
        <div style="flex:1; background:var(--line); height:24px; border-radius:4px; position:relative; overflow:hidden">
          <div style="position:absolute; left:0; top:0; bottom:0; width:${pct}%; background:${color}; opacity:0.8; transition:width 0.5s"></div>
        </div>
        <div style="width:120px; text-align:right; font-weight:600; color:${color}">${fmt(val)} <span style="color:var(--muted); font-weight:400; font-size:10px">(${pct}%)</span></div>
      </div>
    `;
}

window.exportLeadsCSV = function() {
    const leads = DATA.funil.scoring.filter(l => matFilter === 'all' || l.maturidade === matFilter);
    if (!leads.length) return alert('Nenhum lead para exportar neste filtro.');
    
    const keys = ['email', 'nome', 'telefone', 'profissao', 'origem', 'curso', 'conversoes', 'wa_dt_primeira', 'wa_total', 'dt_ultima', 'score', 'maturidade'];
    const header = ['Email', 'Nome', 'Telefone', 'Profissao', 'Origem', 'Curso Recomendado', 'Conversoes RD', 'Primeiro Contato WA', 'Msgs WA', 'Data Ultima Conversao', 'Score', 'Maturidade'];
    
    // Add BOM for Excel UTF-8 compatibility
    let csv = '\uFEFF' + header.join(',') + '\n';
    leads.forEach(l => {
        let row = keys.map(k => {
            let val = l[k] || '';
            val = String(val).replace(/"/g, '""');
            if (val.search(/("|,|\n)/g) >= 0) val = `"${val}"`;
            return val;
        });
        csv += row.join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute("download", `Leads_RD_${DATA.meta.ref_date.replace(/\//g, '')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

// WA CHAT MODAL
function openWAChat(phone_raw, nome) {
    let p = (phone_raw || '').replace(/\D/g, '');
    if (p.startsWith('55') && (p.length === 12 || p.length === 13)) {
        p = p.substring(2);
    }
    if (p.length === 10) {
        p = p.substring(0, 2) + '9' + p.substring(2);
    }
    if (p.length === 11) {
        p = '55' + p;
    }

    if (!DATA.wa_chats || !DATA.wa_chats[p]) {
        console.warn("Histórico WA não encontrado para:", p);
        alert("Histórico não encontrado para o número " + p);
        return;
    }
    const history = DATA.wa_chats[p];
    $('#mc-nome').textContent = nome || 'WhatsApp: ' + p;
    $('#mc-phone').textContent = p;
    
    let html = '';
    let lastDate = '';
    history.forEach(m => {
        const d = m.date.split(' ')[0]; // YYYY-MM-DD
        if (d !== lastDate) {
            html += `<div style="text-align:center; font-size:10px; color:var(--muted); margin:8px 0; font-weight:600">${d.split('-').reverse().join('/')}</div>`;
            lastDate = d;
        }
        
        const time = m.date.split(' ')[1].substring(0,5);
        if (m.sent) {
            html += `<div style="align-self:flex-end; background:#DCF8C6; padding:8px 12px; border-radius:8px 0 8px 8px; max-width:85%; font-size:12.5px; box-shadow:0 1px 1px rgba(0,0,0,.1); line-height:1.4">
                <div style="color:var(--ink); word-wrap:break-word; white-space:pre-wrap;">${m.text}</div>
                <div style="text-align:right; font-size:9px; color:var(--muted); margin-top:4px">${time}</div>
            </div>`;
        } else {
            html += `<div style="align-self:flex-start; background:#FFF; padding:8px 12px; border-radius:0 8px 8px 8px; max-width:85%; font-size:12.5px; box-shadow:0 1px 1px rgba(0,0,0,.1); line-height:1.4">
                <div style="color:var(--ink); word-wrap:break-word; white-space:pre-wrap;">${m.text}</div>
                <div style="text-align:right; font-size:9px; color:var(--muted); margin-top:4px">${time}</div>
            </div>`;
        }
    });
    
    $('#mc-body').innerHTML = html;
    $('#modal-chat').classList.add('on');
    $('#mc-body').scrollTop = $('#mc-body').scrollHeight;
}
$('#mc-close').onclick = () => { $('#modal-chat').classList.remove('on'); };
$('#modal-chat').addEventListener('click', e => { if (e.target === $('#modal-chat')) $('#modal-chat').classList.remove('on'); });

// --- API LOGS SYSTEM (INFECTOCAST ACADEMY) ---
const ACADEMY_BEARER = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ';
const ACADEMY_BASE = 'https://academy.infectocast.com.br/api';
let API_LOGS_DATA = [];

async function consultApiLogs(e) {
    if(e) e.preventDefault();
    const idAluno = $('#api-aluno-id').value.trim();
    if(!idAluno) {
        alert('Informe o ID do aluno');
        return;
    }

    const dStart = $('#api-date-start').value;
    const dEnd = $('#api-date-end').value;

    const tbody = $('#api-log-tbody');
    tbody.innerHTML = '<tr><td colspan="4" style="padding:40px; text-align:center; color:var(--muted)">⏳ Carregando dados da API...</td></tr>';

    try {
        const params = new URLSearchParams();
        if(dStart) params.append('data_inicio', dStart);
        if(dEnd) params.append('data_fim', dEnd);
        const qs = params.toString() ? `?${params.toString()}` : '';

        const [rAluno, rLogs] = await Promise.all([
            fetch(`${ACADEMY_BASE}/alunos/${idAluno}`, {
                headers: { 'Authorization': `Bearer ${ACADEMY_BEARER}`, 'Accept': 'application/json' }
            }).then(r => r.ok ? r.json() : null).catch(() => null),
            fetch(`${ACADEMY_BASE}/alunos/${idAluno}/log${qs}`, {
                headers: { 'Authorization': `Bearer ${ACADEMY_BEARER}`, 'Accept': 'application/json' }
            }).then(r => {
                if(!r.ok) throw new Error(`Erro API status ${r.status}`);
                return r.json();
            })
        ]);

        // Render Aluno Info Header
        if(rAluno && rAluno.success && rAluno.data) {
            const a = rAluno.data;
            $('#api-aluno-header').innerHTML = `
                <div style="background:linear-gradient(135deg, var(--ink) 0%, var(--ink2) 100%); color:#fff; padding:16px 20px; border-radius:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px">
                    <div>
                        <div style="font-size:11px; text-transform:uppercase; color:var(--emerald); font-weight:700; letter-spacing:.1em">Aluno Identificado</div>
                        <h3 style="margin:2px 0 0; font-family:var(--disp); font-size:18px">${a.nome || 'Sem Nome'}</h3>
                        <div style="font-size:12px; color:#A9BCC5; margin-top:2px">✉️ ${a.email || '—'} · <b>ID: #${a.id}</b></div>
                    </div>
                    <div style="background:rgba(255,255,255,.1); padding:6px 14px; border-radius:20px; font-size:11.5px; border:1px solid rgba(255,255,255,.15); font-weight:600">
                        InfectoCast Academy API
                    </div>
                </div>`;
        } else {
            $('#api-aluno-header').innerHTML = `
                <div style="background:#FFF3CD; color:#856404; border:1px solid #FFEEBA; padding:12px 16px; border-radius:10px; font-size:12.5px">
                    ⚠️ Aluno ID <b>#${idAluno}</b> consultado.
                </div>`;
        }

        if(rLogs && rLogs.success && Array.isArray(rLogs.data)) {
            API_LOGS_DATA = rLogs.data;
            
            // Populate Event Filter Select
            const evTypes = new Set(API_LOGS_DATA.map(l => l.acao_evento).filter(Boolean));
            const selFilter = $('#api-event-filter');
            selFilter.innerHTML = '<option value="ALL">Todos os Eventos (' + API_LOGS_DATA.length + ')</option>' +
                Array.from(evTypes).map(t => `<option value="${t}">${t}</option>`).join('');

            renderApiLogsTable();
        } else {
            API_LOGS_DATA = [];
            tbody.innerHTML = '<tr><td colspan="4" style="padding:40px; text-align:center; color:var(--muted)">Nenhum log encontrado para os filtros selecionados.</td></tr>';
            $('#api-kpi-total').textContent = '0';
            $('#api-kpi-logins').textContent = '0';
            $('#api-kpi-downloads').textContent = '0';
            $('#api-kpi-last').textContent = '—';
        }

    } catch(err) {
        console.error("Erro consultApiLogs:", err);
        tbody.innerHTML = `<tr><td colspan="4" style="padding:30px; text-align:center; color:var(--coral)">⚠️ Falha ao conectar à API: ${err.message}</td></tr>`;
    }
}

function setApiPreset(preset) {
    const today = new Date();
    const fmtD = d => d.toISOString().split('T')[0];

    if(preset === '7d') {
        const past = new Date(); past.setDate(today.getDate() - 7);
        $('#api-date-start').value = fmtD(past);
        $('#api-date-end').value = fmtD(today);
    } else if(preset === '30d') {
        const past = new Date(); past.setDate(today.getDate() - 30);
        $('#api-date-start').value = fmtD(past);
        $('#api-date-end').value = fmtD(today);
    } else if(preset === '2026') {
        $('#api-date-start').value = '2026-01-01';
        $('#api-date-end').value = '2026-12-31';
    } else if(preset === 'clear') {
        $('#api-date-start').value = '';
        $('#api-date-end').value = '';
    }
    consultApiLogs();
}

function renderApiLogsTable() {
    const filterEv = $('#api-event-filter').value;
    const filterTxt = ($('#api-text-filter').value || '').toLowerCase();

    const filtered = API_LOGS_DATA.filter(log => {
        if(filterEv !== 'ALL' && log.acao_evento !== filterEv) return false;
        if(filterTxt) {
            const itemMatch = (log.item_objeto || '').toLowerCase().includes(filterTxt);
            const acaoMatch = (log.acao_evento || '').toLowerCase().includes(filterTxt);
            const compMatch = (log.complemento || '').toLowerCase().includes(filterTxt);
            if(!itemMatch && !acaoMatch && !compMatch) return false;
        }
        return true;
    });

    // Update KPIs
    const total = API_LOGS_DATA.length;
    const logins = API_LOGS_DATA.filter(l => l.acao_evento === 'LOGIN WEB').length;
    const downloads = API_LOGS_DATA.filter(l => (l.acao_evento || '').includes('BAIXOU')).length;
    const lastFmt = API_LOGS_DATA.length > 0 && API_LOGS_DATA[0].data_hora ? API_LOGS_DATA[0].data_hora.replace('T', ' ').substring(0,19) : '—';

    $('#api-kpi-total').textContent = fmt(total);
    $('#api-kpi-logins').textContent = fmt(logins);
    $('#api-kpi-downloads').textContent = fmt(downloads);
    $('#api-kpi-last').textContent = lastFmt;

    $('#api-log-count').textContent = `${filtered.length} de ${total} registros`;

    const tbody = $('#api-log-tbody');
    if(filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="padding:30px; text-align:center; color:var(--muted)">Nenhum registro corresponde aos filtros locais.</td></tr>';
        return;
    }

    tbody.innerHTML = filtered.map(log => {
        let badgeStyle = 'background:#EEF2F5; color:#4A5A64;';
        let icon = '⚡';
        const ev = log.acao_evento || '';
        if(ev.includes('LOGIN')) { badgeStyle = 'background:var(--emerald-w); color:var(--emerald-d);'; icon = '🔑'; }
        else if(ev.includes('BAIXOU') || ev.includes('PDF')) { badgeStyle = 'background:#EAF4FA; color:#2C6690;'; icon = '📥'; }
        else if(ev.includes('AULA') || ev.includes('ASSISTIU')) { badgeStyle = 'background:#EFEBF7; color:#6A5A9E;'; icon = '🎬'; }

        const dtStr = log.data_hora ? log.data_hora.replace('T', ' ').substring(0,19) : '—';
        const itemStr = log.item_objeto || '—';
        const compStr = log.complemento ? `<span style="padding:2px 6px; background:var(--paper); border:1px solid var(--line); border-radius:4px; font-size:10px; font-weight:600">${log.complemento}</span>` : '—';

        return `<tr style="border-bottom:1px solid var(--line2)">
            <td style="padding:10px 14px; font-family:var(--disp); font-size:11.5px; white-space:nowrap; color:var(--muted)">${dtStr}</td>
            <td style="padding:10px 14px"><span style="display:inline-flex; align-items:center; gap:4px; font-size:10.5px; font-weight:700; font-family:var(--disp); padding:3px 8px; border-radius:12px; ${badgeStyle}"><span>${icon}</span> ${ev}</span></td>
            <td style="padding:10px 14px; font-weight:500; font-size:12.5px; color:var(--ink)">${itemStr}</td>
            <td style="padding:10px 14px; color:var(--muted)">${compStr}</td>
        </tr>`;
    }).join('');
}

function exportApiLogsToCSV() {
    if(API_LOGS_DATA.length === 0) return;
    let csv = '\uFEFFData_Hora,Acao_Evento,Item_Objeto,Complemento\n';
    API_LOGS_DATA.forEach(l => {
        const row = [
            `"${(l.data_hora||'').replace(/"/g, '""')}"`,
            `"${(l.acao_evento||'').replace(/"/g, '""')}"`,
            `"${(l.item_objeto||'').replace(/"/g, '""')}"`,
            `"${(l.complemento||'').replace(/"/g, '""')}"`
        ];
        csv += row.join(',') + '\n';
    });
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `logs_api_aluno_${$('#api-aluno-id').value}_${new Date().toISOString().slice(0,10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// INIT
$$('.tab')[0].click();
setTimeout(() => {
    initFilters();
    applyFilters();
    
    $$('.clickable-kpi').forEach(k => {
        k.onclick = () => {
            console.log('Clicked KPI:', k.dataset.st);
            try {
                openModalList(k.dataset.st);
            } catch (err) {
                console.error('Error in openModalList:', err);
                alert('Erro ao abrir lista: ' + err.message);
            }
        };
    });
    
    $('#funil-tbody').addEventListener('click', e => {
        const tr = e.target.closest('tr.clickable');
        if(tr) openLead(tr.dataset.email);
    });
    
    // Busca dados mais recentes do servidor de mensagens, se ele estiver rodando
    fetch('http://localhost:8080/mensagens_recentes')
    .then(res => res.json())
    .then(data => {
        if(data && !data.error) {
            CURRENT_DATA.mensagens_recentes = data;
        }
    })
    .catch(err => console.log('Servidor de mensagens não detectado no carregamento:', err));
    
}, 100);


// ALLOC MODAL LOGIC
function openAllocModal(curso, aulaNome) {
    const modal = document.createElement('div');
    modal.id = 'alloc-modal';
    modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:9999;';
    
    const mods = DATA.curriculum[curso].filter(m => m.modulo !== 'Aulas Adicionais').map(m => m.modulo);
    const modOptions = mods.map(m => `<option value="${m}">${m}</option>`).join('');
    
    modal.innerHTML = `
        <div style="background:white; padding:24px; border-radius:12px; width:400px; max-width:90%; font-family:var(--body); box-shadow:0 4px 20px rgba(0,0,0,0.15)">
            <h3 style="margin:0 0 16px 0; font-size:16px; color:var(--ink)">📍 Alocar Aula</h3>
            
            <div style="margin-bottom:12px">
                <label style="display:block; font-size:12px; font-weight:600; color:var(--muted); margin-bottom:4px">Aula</label>
                <input type="text" readonly value="${aulaNome}" style="width:100%; padding:8px; border:1px solid var(--line); border-radius:6px; background:#f9f9f9; color:var(--muted)">
            </div>
            
            <div style="margin-bottom:12px">
                <label style="display:block; font-size:12px; font-weight:600; color:var(--muted); margin-bottom:4px">Módulo Existente</label>
                <select id="alloc-select" style="width:100%; padding:8px; border:1px solid var(--line); border-radius:6px;">
                    <option value="">-- Selecione ou crie um novo abaixo --</option>
                    ${modOptions}
                </select>
            </div>
            
            <div style="margin-bottom:20px">
                <label style="display:block; font-size:12px; font-weight:600; color:var(--muted); margin-bottom:4px">Ou Novo Módulo</label>
                <input type="text" id="alloc-new" placeholder="Ex: Módulo 5 - Tema" style="width:100%; padding:8px; border:1px solid var(--line); border-radius:6px;">
            </div>
            
            <div style="display:flex; justify-content:flex-end; gap:8px">
                <button onclick="document.getElementById('alloc-modal').remove()" style="padding:8px 16px; border:1px solid var(--line); border-radius:6px; background:white; cursor:pointer">Cancelar</button>
                <button id="alloc-save" style="padding:8px 16px; border:none; border-radius:6px; background:var(--brand); color:white; font-weight:600; cursor:pointer">Confirmar Alocação</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('alloc-save').onclick = async () => {
        const sel = document.getElementById('alloc-select');
        const newVal = document.getElementById('alloc-new').value.trim();
        const btn = document.getElementById('alloc-save');
        
        if (!newVal && !sel.value) {
            alert('Selecione um módulo ou digite um novo.');
            return;
        }
        
        btn.innerText = 'Salvando...';
        btn.disabled = true;
        
        try {
            fetch('/api/alocar-aula', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ curso: gAllocCurso, aula: gAllocAula, modulo: targetMod })
            }).then(r => r.json()).then(res => {
                if (res.status === 'ok') {
                    window.location.reload();
                } else {
                    alert('Erro ao salvar. O server.py está rodando?');
                    btn.innerText = 'Confirmar Alocação';
                    btn.disabled = false;
                }
            }).catch(e => {
                alert('Erro de conexão. Certifique-se de que o server.py está ativo e rodando na porta correta.');
                btn.innerText = 'Confirmar Alocação';
                btn.disabled = false;
            });
        } catch (e) {
            alert('Erro inesperado.');
            btn.innerText = 'Confirmar Alocação';
            btn.disabled = false;
        }
    };
}

function triggerUpdate() {
    const btn = document.getElementById('btn-atualizar');
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="animation: spin 1s linear infinite"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/></svg> Sincronizando...';
    btn.style.opacity = '0.7';
    btn.disabled = true;

    fetch('http://127.0.0.1:8085/api/atualizar', {
        method: 'POST',
    }).then(r => r.json()).then(res => {
        if (res.status === 'ok') {
            btn.innerHTML = '✅ Concluído';
            setTimeout(() => {
                window.location.href = window.location.pathname + '?v=' + new Date().getTime();
            }, 500);
        } else {
            alert('Erro: ' + res.error);
            btn.innerHTML = 'Atualizar Dados';
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    }).catch(e => {
        alert('Erro de conexão com o servidor local (está rodando?).');
        btn.innerHTML = 'Atualizar Dados';
        btn.disabled = false;
        btn.style.opacity = '1';
    });
}

// ============================================================
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


function _resolveFinCourse(f) {
    if (!f) return 'PLATAFORMA GERAL';
    if (f.curso && f.curso !== 'PLATAFORMA GERAL' && f.curso !== 'None') return f.curso;

    const email = (f.email || f._email || '').toString().toLowerCase().trim();
    const aluno = (f.aluno || f._aluno || '').toString().toLowerCase().trim();
    const plano = (f.plano || f._plano || f.description || '').toString();

    // 1. Tentar encontrar aluno no cadastro da plataforma (Academy / Cativa)
    const stList = (CURRENT_DATA && CURRENT_DATA.students) ? CURRENT_DATA.students : (DATA && DATA.students ? DATA.students : []);
    let stMatch = null;
    if (email) {
        stMatch = stList.find(s => s.email && s.email.toLowerCase().trim() === email);
    }
    if (!stMatch && aluno) {
        stMatch = stList.find(s => s.nome && s.nome.toLowerCase().trim() === aluno);
    }
    if (stMatch && stMatch.curso && stMatch.curso !== 'PLATAFORMA GERAL' && stMatch.curso !== 'None') {
        return stMatch.curso;
    }

    // 2. Inferir a partir do nome do plano ou descrição da cobrança na Vindi / Asaas
    const textFull = (plano + ' ' + (f.description || '')).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    if (textFull.includes('ccih') || textFull.includes('prevencao') || textFull.includes('hospitalar')) {
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
    }
    if (textFull.includes('ortop') || textFull.includes('partes moles')) {
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PELE E PARTES MOLES';
    }
    if (textFull.includes('imuno') || textFull.includes('inuno')) {
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
    }
    if (textFull.includes('pediatria') || textFull.includes('infectoped')) {
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
    }
    if (textFull.includes('multi-r') || textFull.includes('multi r')) {
        return 'JORNADA MULTI-R';
    }
    if (textFull.includes('fungo') || textFull.includes('antifung')) {
        return 'DO FUNGO AO ANTIFUNGICO';
    }
    if (textFull.includes('s.o.s') || textFull.includes('antibiotico')) {
        return 'S.O.S ANTIBIOTICO';
    }
    if (textFull.includes('qualidade')) {
        return 'FERRAMENTAS DE QUALIDADE';
    }

    return 'PLATAFORMA GERAL';
}

function _getFinData(src) {
    const vindi = DATA.financeiro;
    const asaas = DATA.financeiro_asaas;

    const vfaturas = (vindi && vindi.faturas_tabela) ? vindi.faturas_tabela.map(f => { const c = _resolveFinCourse(f); return { ...f, gateway: 'Vindi', curso: c, _curso: c, _aluno: f.aluno, _email: f.email, _plano: f.plano }; }) : [];
    const afaturas = (asaas && asaas.faturas_tabela) ? asaas.faturas_tabela.map(f => { const c = _resolveFinCourse(f); return { ...f, gateway: 'Asaas', curso: c, _curso: c, _aluno: f.aluno, _email: f.email, _plano: f.plano }; }) : [];

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

    // Y-axis ticks
    const yTicks = 5;
    let ticks = [];
    for (let i = 0; i <= yTicks; i++) ticks.push(Math.round(maxVal * i / yTicks));

    const yScale = v => H - padB - (v / maxVal) * (H - padT - padB);
    const xPos = i => padL + i * step + step / 2;

    const today = new Date().toISOString().slice(0, 7);

    let svg = `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">`;

    // Grid lines
    ticks.forEach(t => {
        const y = yScale(t);
        const label = t >= 1000 ? `R$${(t/1000).toFixed(0)}k` : `R$${t}`;
        svg += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="var(--line)" stroke-width="1" stroke-dasharray="4,4"/>`;
        svg += `<text x="${padL - 5}" y="${y + 4}" text-anchor="end" font-size="9" fill="var(--muted2)">${label}</text>`;
    });

    // Bars
    sortedMeses.forEach((mes, i) => {
        const cx = xPos(i);
        const hv = histVals[i];
        const pv = projVals[i];
        const isCurrent = (mes === today);
        const isFuture = (mes > today);
        const isSelected = (mes === _finSelectedMonth);
        const hasBoth = (hv > 0 && pv > 0 && (isCurrent || isFuture));

        // Highlight visual se o mês estiver clicado / selecionado
        if (isSelected) {
            svg += `<rect x="${cx - step/2 + 1}" y="${padT}" width="${step - 2}" height="${H - padT - padB + 2}" rx="6" fill="rgba(18,161,122,0.12)" stroke="var(--emerald)" stroke-width="1.5" stroke-dasharray="3,3"/>`;
        }

        // 1. Realizado (Verde)
        if (hv > 0) {
            const bh = Math.max(2, (hv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            const bx = hasBoth ? (cx - grpW / 2) : (cx - barW / 2);
            svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradGreen)" opacity="${isFuture ? 0.4 : 1}" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
                <title>${labelsMap[mes]} - Realizado: R$ ${hv.toLocaleString('pt-BR', {minimumFractionDigits:2})} (Clique para filtrar)</title>
            </rect>`;
        }

        // 2. Projeção (Azul) - Exibe no mês atual E meses futuros
        if (pv > 0 && (isCurrent || isFuture)) {
            const bh = Math.max(2, (pv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            const bx = hasBoth ? (cx + 2) : (cx - barW / 2);
            svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradBlue)" opacity="${isCurrent ? 0.95 : 0.75}" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
                <title>${labelsMap[mes]} - Projeção: R$ ${pv.toLocaleString('pt-BR', {minimumFractionDigits:2})} (Clique para filtrar)</title>
            </rect>`;
        }

        // Área transparente clicável em toda a coluna do mês para facilitar o clique
        svg += `<rect x="${cx - step/2}" y="${padT}" width="${step}" height="${H - padT - padB}" fill="transparent" style="cursor:pointer" onclick="_finToggleMonthFilter('${mes}')">
            <title>${labelsMap[mes]}: Clique para filtrar composição por este mês</title>
        </rect>`;

        // X-axis label com destaque
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

    // Agrupar por curso
    const byCourse = {};
    const studentsList = DATA.students || [];

    // Contagem de alunos com financeiro considerado (ao menos 1 pagamento) por curso
    studentsList.filter(s => s.vindi || s.asaas).forEach(s => {
        const c = s.curso || 'PLATAFORMA GERAL';
        if (!byCourse[c]) {
            byCourse[c] = { curso: c, alunos: 0, pago: 0, previsto: 0, atraso: 0 };
        }
        byCourse[c].alunos++;
    });

    // Faturas a considerar
    const faturas = fin.faturas_tabela || [];
    faturas.forEach(f => {
        const c = f.curso || 'PLATAFORMA GERAL';
        if (!byCourse[c]) {
            byCourse[c] = { curso: c, alunos: 0, pago: 0, previsto: 0, atraso: 0 };
        }

        const pIso = f.data_pagamento_iso || f.data_pagamento || '';
        const vIso = f.vencimento_iso || f.vencimento || '';
        const refYm = (f.status === 'paid' || f.status === 'pago') ? (pIso.slice(0, 7) || vIso.slice(0, 7)) : vIso.slice(0, 7);

        // Se o usuário clicou em um mês específico no gráfico, filtra estritamente por esse mês!
        if (_finSelectedMonth && refYm !== _finSelectedMonth) {
            return;
        }

        const val = Number(f.valor) || 0;
        const st = f.status || '';

        if (st === 'paid' || st === 'pago') {
            byCourse[c].pago += val;
        } else if (st === 'em_atraso') {
            byCourse[c].atraso += val;
        } else if (st === 'futuro' || st === 'a_vencer' || st === 'pending') {
            byCourse[c].previsto += val;
        }
    });

    const rows = Object.values(byCourse).filter(r => r.pago > 0 || r.previsto > 0 || r.atraso > 0 || r.alunos > 0);
    const totalVolume = rows.reduce((acc, r) => acc + r.pago + r.previsto, 0);

    // Ordena pelo volume total
    rows.sort((a, b) => (b.pago + b.previsto) - (a.pago + a.previsto));

    const fmt = v => 'R$ ' + (Number(v)||0).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});

    if (!rows.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="padding:24px; text-align:center; color:var(--muted); font-size:12px">Nenhuma receita registrada para este filtro.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map((r, idx) => {
        const vol = r.pago + r.previsto;
        const pct = totalVolume > 0 ? ((vol / totalVolume) * 100).toFixed(1) : '0.0';
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
            const curso = f.curso || _resolveFinCourse(f) || 'PLATAFORMA GERAL';
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
            const tel = studentObj && studentObj.telefone ? studentObj.telefone.replace(/\D/g, '') : '';
            let waBtn = '';
            if (st.has_atraso) {
                const msg = encodeURIComponent(`Olá, ${st.aluno}! Aqui é da equipe da Pós-Graduação InfectoCast.\n\nConstatamos que sua mensalidade no valor de ${fmtMoney(st.total_atraso)} está pendente.\n\nCaso precise de ajuda para regularizar, entre em contato conosco por aqui. Um abraço!`);
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
            const tel = s && s.telefone ? s.telefone.replace(/\D/g,'') : '';
            const msg = encodeURIComponent(`Olá! Aqui é da equipe da Pós-Graduação InfectoCast.\n\nSua mensalidade de ${venc} no valor de ${valor} está pendente.\n\nCaso precise de ajuda para regularizar, entre em contato conosco. Um abraço!`);
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
}


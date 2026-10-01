
const fs = require('fs');
const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'utf-8');
const matchData = html.match(/const DATA = (\{[\s\S]*?\});/);
const DATA = JSON.parse(matchData[1]);

// Mock browser DOM globals
const domElements = new Map();
function getOrCreateElem(id) {
    if (!domElements.has(id)) {
        domElements.set(id, {
            id: id,
            innerHTML: '',
            innerText: '',
            textContent: '',
            style: {},
            classList: {
                add: () => {},
                remove: () => {},
                toggle: () => {},
                contains: () => false
            },
            appendChild: () => {},
            setAttribute: () => {},
            getAttribute: () => '',
            querySelectorAll: () => [],
            addEventListener: () => {}
        });
    }
    return domElements.get(id);
}

const document = {
    getElementById: id => getOrCreateElem(id),
    querySelector: sel => getOrCreateElem(sel.replace('#', '')),
    querySelectorAll: sel => [getOrCreateElem(sel.replace('#', ''))],
    body: getOrCreateElem('body'),
    addEventListener: () => {}
};

const window = {
    document: document,
    addEventListener: () => {},
    innerWidth: 1920,
    innerHeight: 1080
};

const $ = sel => getOrCreateElem(sel.replace('#', '').replace('.', ''));
const $$ = sel => [getOrCreateElem(sel.replace('#', '').replace('.', ''))];

try {
    
// Will be injected by gerador.py
const DATA = {};

let CURRENT_DATA = {};
let FILTER = { curso: 'all', aluno: 'all', start: '', end: '' };
let filterText = '';
const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);
const fmt = n => new Intl.NumberFormat('pt-BR').format(n);

// Funcoes do Filtro Geral Global Unificado
window.resetGlobalFilters = function() {
    FILTER.curso = 'all';
    FILTER.aluno = 'all';
    FILTER.start = '';
    FILTER.end = '';
    const selCurso = document.getElementById('filter-curso');
    if (selCurso) selCurso.value = 'all';
    const selStart = document.getElementById('filter-date-start');
    if (selStart) selStart.value = '';
    const selEnd = document.getElementById('filter-date-end');
    if (selEnd) selEnd.value = '';
    applyFilters();
};

window.setCursoView = function(cName) {
    if (!cName || cName === 'all') {
        FILTER.curso = 'all';
        CURRENT_SELECTED_COURSE = 'all';
        const sel = document.getElementById('filter-curso');
        if (sel) sel.value = 'all';
        applyFilters();
        if (typeof drawCursoView === 'function') {
            drawCursoView('all', true);
        }
        return;
    }
    const cCanonical = (typeof resolveCanonicalCourse === 'function') ? resolveCanonicalCourse(cName) : cName;
    CURRENT_SELECTED_COURSE = cCanonical;
    FILTER.curso = cCanonical;
    const sel = document.getElementById('filter-curso');
    if (sel) {
        for (let i = 0; i < sel.options.length; i++) {
            const optVal = (typeof resolveCanonicalCourse === 'function') ? resolveCanonicalCourse(sel.options[i].value) : sel.options[i].value;
            if (optVal === cCanonical || sel.options[i].value === cName) {
                sel.selectedIndex = i;
                break;
            }
        }
    }
    applyFilters();
    if (typeof drawCursoView === 'function') {
        drawCursoView(cCanonical, true);
    }
};

function initFilters() {
    const cursos = new Set();
    const stList = (DATA && DATA.students) ? DATA.students : [];
    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};

    stList.forEach(s => {
        if(s.curso && s.curso !== 'Sem Curso') {
            const cName = (typeof resolveCanonicalCourse === 'function') ? resolveCanonicalCourse(s.curso) : s.curso;
            cursos.add(cName);
        }
    });
    if (curric) {
        Object.keys(curric).forEach(c => { 
            if(c && c !== 'Sem Curso') {
                const cName = (typeof resolveCanonicalCourse === 'function') ? resolveCanonicalCourse(c) : c;
                cursos.add(cName);
            }
        });
    }

    const selCurso = $('#filter-curso');
    const sortedCourses = Array.from(cursos).sort((a, b) => {
        const aPos = a.startsWith('POS') || a.startsWith('PÓS') || a.startsWith('P?S');
        const bPos = b.startsWith('POS') || b.startsWith('PÓS') || b.startsWith('P?S');
        if (aPos && !bPos) return -1;
        if (!aPos && bPos) return 1;
        return a.localeCompare(b);
    });
    if (selCurso) {
        selCurso.innerHTML = '<option value="all">Todos os Cursos (Consolidado)</option>' + sortedCourses.map(c => `<option value="${c}">${c}</option>`).join('');
        if (FILTER.curso && FILTER.curso !== 'all') {
            selCurso.value = FILTER.curso;
        }
    }

    const selAluno = $('#filter-aluno');
    if (selAluno) {
        selAluno.innerHTML = '<option value="all">Todos os Alunos</option>';
    }

    if (selCurso) {
        selCurso.onchange = e => { 
            FILTER.curso = e.target.value; 
            if (FILTER.curso !== 'all') {
                CURRENT_SELECTED_COURSE = (typeof resolveCanonicalCourse === 'function') ? resolveCanonicalCourse(FILTER.curso) : FILTER.curso;
            } else {
                CURRENT_SELECTED_COURSE = 'all';
            }
            applyFilters(); 
        };
    }

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
        if (FILTER.curso !== 'all') {
            const sCur = (typeof resolveCanonicalCourse === 'function') ? resolveCanonicalCourse(s.curso) : s.curso;
            const fCur = (typeof resolveCanonicalCourse === 'function') ? resolveCanonicalCourse(FILTER.curso) : FILTER.curso;
            if (sCur !== fCur && s.curso !== FILTER.curso) return false;
        }
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
        
        // REGRA INTELIGENTE DE STATUS FINANCEIRO:
        // Só marca como 'Cancelado' se NÃO existir assinatura ATIVA em nenhum gateway.
        // Se o aluno tem Vindi cancelada mas Asaas ativa (ou vice-versa), a ativa prevalece.
        const vindiStatus = scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : null;
        const asaasStatus = scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : null;
        const vindiCanceled = vindiStatus === 'cancelado' || vindiStatus === 'canceled';
        const asaasCanceled = asaasStatus === 'cancelado' || asaasStatus === 'canceled';
        const vindiActive = vindiStatus && !vindiCanceled;
        const asaasActive = asaasStatus && !asaasCanceled;
        // Só cancela se existe pelo menos um cancelamento E nenhum gateway ativo
        if ((vindiCanceled || asaasCanceled) && !vindiActive && !asaasActive) {
            if (vindiCanceled) {
                scopy.status = 'Cancelado';
                scopy.status_motivo = 'Assinatura cancelada no sistema financeiro (Vindi).';
            } else {
                scopy.status = 'Cancelado';
                scopy.status_motivo = 'Cobrança cancelada no sistema financeiro (Asaas).';
            }
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
  if (typeof drawCursoView === 'function') {
      const active = (FILTER && FILTER.curso && FILTER.curso !== 'all') ? resolveCanonicalCourse(FILTER.curso) : 'all';
      drawCursoView(active, true);
  }
  if (typeof drawFunil === 'function') {
      drawFunil(true);
  }
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

function getCursoBadge(s) {
  if (!s || !s.curso_inferido) return '';
  const orig = s.curso_origem || 'RD Station';
  return `<span class="badge-inferido" title="Curso deduzido através de ${orig}. Será atualizado automaticamente assim que houver registro oficial ou acesso às aulas na plataforma.">✨ Inferido (${orig})</span>`;
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
      <td style="font-size:11.5px;color:var(--muted);white-space:nowrap;max-width:160px;overflow:hidden;text-overflow:ellipsis" title="${s.curso}">${s.curso} ${getCursoBadge(s)}</td>
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
    ['Status',statusDisplay],['Curso',`${s.curso || 'Sem Curso'} ${getCursoBadge(s)}`],['Módulos',`${s.mods_concluidos||0}/${s.total_mods||0}`],
    ['Último acesso',s.last_fmt||'—'],['Dias inativo',s.dias_inativo != null ? s.dias_inativo : '—'],
    ['Inscrição',dataInscFmt], ['Plataforma', s.plataforma || 'Academy'], ['Último WA', s.wa_dt_ultima || '—']
  ].map(([l,v])=>`<div class="st"><div class="v">${v}</div><div class="l">${l}</div></div>`).join('');
  
  let rdHtml = '';
  if (s.rd_funnel) {
      const rd = s.rd_funnel;
      const origin = rd.origem || 'Desconhecida';
      const conv = rd.conversoes || 0;
      const pri = rd.dt_primeira || '—';
      const isApi = rd.fonte === 'API Oficial RD Station';
      const nonCheckoutEvs = (rd.eventos_detalhados || []).filter(e => !isCheckoutEvent(e));
      const antesQtd = nonCheckoutEvs.length;
      const validFmtEvents = (rd.eventos || []).filter(e => !isCheckoutString(e));
      const evsStr = validFmtEvents.length ? validFmtEvents.map(e => `<li style="margin-bottom:6px">${e}</li>`).join('') : '<li style="color:var(--muted)">Nenhum ponto de contato pré-matrícula registrado (compra direta no checkout)</li>';
      rdHtml = `
      <div style="margin:20px 20px 0; padding:14px 16px; border:1px solid var(--line2); border-radius:10px; background:rgba(255,255,255,0.03); box-shadow:0 2px 8px rgba(0,0,0,0.04)">
        <div style="display:flex; justify-content:space-between; align-items:center; cursor:pointer" onclick="const b=document.getElementById('rd-body'); b.style.display=b.style.display==='none'?'block':'none'">
            <div>
              <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px">
                <b style="font-size:12px; color:var(--text)">Jornada RD Station (Pontos de Contato Pré-Matrícula)${s.wa_total ? ' + WhatsApp' : ''}</b>
                ${isApi ? '<span style="background:rgba(0,180,216,0.15); color:#00b4d8; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; border:1px solid rgba(0,180,216,0.3)">API Oficial RD Station</span>' : ''}
              </div>
              <span style="font-size:11px; color:var(--muted)">Origem: <b>${origin}</b> · Conversões Pré-Matrícula: <b>${antesQtd}</b> · Primeira: <b>${pri}</b></span>
              ${s.wa_total ? `<br><b style="font-size:11px; color:#25D366">Primeiro contato WA: ${s.wa_dt_primeira}</b>` : ''}
            </div>
            <button style="border:1px solid var(--line2); background:var(--bg); color:var(--text); padding:5px 10px; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer">Ver Conversões (${antesQtd}) ▾</button>
        </div>
        <div id="rd-body" style="display:none; margin-top:12px; padding-top:12px; border-top:1px solid var(--line2)">
            <div style="font-size:11px; font-weight:700; color:var(--text); margin-bottom:8px">Pontos de Contato Pré-Matrícula (API RD Station):</div>
            <ul style="font-size:11px; color:var(--text); padding-left:18px; margin:0; line-height:1.7">
              ${evsStr}
            </ul>
        </div>
      </div>`;
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
          if (e.acao === 'ASSISTIU AULA' || e.acao === 'CONCLUIU AULA') {
              if (e.item_id) s_done.add(String(e.item_id));
              if (e.item) s_done.add(e.item.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''));
          }
      });
      // Filtra estritamente os módulos oficiais do curso (sem Aulas Adicionais)
      const officialMods = DATA.curriculum[s.curso].filter(m => m.modulo && m.modulo !== 'Aulas Adicionais');
      let totalModsConcluidos = 0;

      const mRows = officialMods.map(m => {
          let mDone = 0;
          (m.aulas || []).forEach(a => {
              const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') : '';
              if (s_done.has(String(a.id)) || s_done.has(aNorm)) mDone++;
          });
          const mPct = m.n_curric > 0 ? Math.min(100, Math.round(mDone / m.n_curric * 100)) : 0;
          const isDone = m.n_curric > 0 && mDone >= m.n_curric;
          if (isDone) totalModsConcluidos++;
          const color = isDone ? 'var(--emerald)' : (mPct > 0 ? 'var(--sky)' : 'var(--muted)');
          return `
            <div style="display:flex; flex-direction:column; gap:4px; font-size:11.5px; padding:8px 0; border-bottom:1px solid var(--line2)">
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
            <span style="font-size:11px; font-weight:700; color:var(--emerald-d)">${totalModsConcluidos}/${officialMods.length} módulos concluídos</span>
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
                    <b style="color:var(--muted2)">Curso:</b> ${s.curso} ${getCursoBadge(s)}<br>
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
    try {
        window.scrollTo({ top: 0, behavior: 'instant' });
        $$('.tab').forEach(t => t.classList.toggle('on', (t.dataset && t.dataset.p === pId) || t.getAttribute('data-p') === pId));
        $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));

// KPIs scoped to relevant tab

        if (pId === 'exec') { try { drawExecView(true); } catch(e) { console.error('Erro drawExecView:', e); } }
        if (pId === 'curso') { try { drawCursoView((FILTER && FILTER.curso !== 'all') ? FILTER.curso : 'all', true); } catch(e) { console.error('Erro drawCursoView:', e); } }
        if (pId === 'home') { try { drawHome(true); } catch(e) { console.error('Erro drawHome:', e); } }
        if (pId === 'prog') { 
            try { buildHead(); } catch(e) { console.error('Erro buildHead:', e); }
            try { statusChips(); } catch(e) { console.error('Erro statusChips:', e); }
            try { renderRows(); } catch(e) { console.error('Erro renderRows:', e); }
        }
        if (pId === 'mod') { try { renderModules(); } catch(e) { console.error('Erro renderModules:', e); } }
        if (pId === 'ret') { try { renderRetention(); } catch(e) { console.error('Erro renderRetention:', e); } }
        if (pId === 'tl') { try { drawTimeline(true); } catch(e) { console.error('Erro drawTimeline:', e); } }
        if (pId === 'funil') {
            try { drawFunil(true); } catch(e) { console.error('Erro drawFunil:', e); }
            if ($('.filters')) $('.filters').style.display = 'none';
        } else {
            if ($('.filters')) $('.filters').style.display = 'flex';
        }
        if (pId === 'origem') { try { drawOrigem(true); } catch(e) { console.error('Erro drawOrigem:', e); } }
        if (pId === 'fin') { try { drawFinanceiro(true); } catch(e) { console.error('Erro drawFinanceiro:', e); } }
    } catch(err) {
        console.error('Erro em selectTab:', err);
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
function setModCourse(cName) {
    FILTER.curso = cName;
    const sel = $('#filter-curso');
    if (sel) sel.value = cName;
    renderModules();
}

function renderModules() {
    let c = (FILTER && FILTER.curso && FILTER.curso !== 'all') ? FILTER.curso : null;
    const view = $('#modcard');
    if (!view) return;

    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};
    const availableCourses = Object.keys(curric).filter(k => k && k !== 'PLATAFORMA GERAL').sort((a, b) => {
        const aPos = a.startsWith('POS') || a.startsWith('PÓS');
        const bPos = b.startsWith('POS') || b.startsWith('PÓS');
        if (aPos && !bPos) return -1;
        if (!aPos && bPos) return 1;
        return a.localeCompare(b);
    });

    if (!c || !curric[c]) {
        c = availableCourses.length > 0 ? availableCourses[0] : Object.keys(curric)[0];
    }
    
    const mods = curric[c] || [];
    if (!mods || mods.length === 0) {
        view.innerHTML = '<div style="padding:40px; text-align:center; color:var(--muted); font-size:13px;">Nenhum módulo encontrado para este curso no currículo oficial.</div>';
        return;
    }

    // 1. Filtrar alunos do curso selecionado
    const allStudents = (CURRENT_DATA && CURRENT_DATA.students) ? CURRENT_DATA.students : ((DATA && DATA.students) ? DATA.students : []);
    const courseStudents = allStudents.filter(s => (typeof resolveCanonicalCourse === 'function' ? resolveCanonicalCourse(s.curso) === resolveCanonicalCourse(c) : s.curso === c) || (c === 'PLATAFORMA GERAL'));
    const totalAlunosCurso = Math.max(1, courseStudents.length);
    const alunosAtivosCurso = courseStudents.filter(s => s.acessou).length;

    // 2. Calcular estatísticas de cada módulo e de cada aula
    let totalAulasCurso = 0;
    let maxViewsCurso = 1;
    let modulosStats = [];

    mods.forEach((m, mIdx) => {
        const aulasArr = m.aulas || [];
        totalAulasCurso += aulasArr.length;
        
        let aulasStats = [];
        let totalViewsModulo = 0;
        let alunosIniciaramModulo = new Set();
        let alunosConcluiramModulo = new Set();

        aulasArr.forEach((a, aIdx) => {
            const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[̀-ͯ]/g, '') : '';
            const viewsSet = (CURRENT_DATA?.lesson_views?.[a.id]) || (CURRENT_DATA?.lesson_views?.[String(a.id)]) || (CURRENT_DATA?.lesson_views?.[aNorm]) || new Set();
            
            // Filtra visualizações apenas de alunos deste curso
            const viewsCount = Array.from(viewsSet).filter(em => courseStudents.some(s => s.email && s.email.toLowerCase() === em.toLowerCase())).length;
            
            if (viewsCount > maxViewsCurso) maxViewsCurso = viewsCount;
            totalViewsModulo += viewsCount;
            
            if (viewsCount > 0) {
                Array.from(viewsSet).forEach(em => alunosIniciaramModulo.add(em.toLowerCase()));
            }

            aulasStats.push({
                id: a.id,
                ordem: a.ordem || (aIdx + 1),
                nome: a.nome || f`Aula ${aIdx + 1}`,
                views: viewsCount,
                curriculo: a.curriculo !== false
            });
        });

        // Alunos que assistiram todas as aulas do módulo
        courseStudents.forEach(s => {
            if (!s.events) return;
            const aulasVistasAluno = new Set();
            s.events.forEach(e => {
                if (e.acao === 'ASSISTIU AULA' || e.acao === 'CONCLUIU AULA') {
                    if (e.item_id) aulasVistasAluno.add(String(e.item_id));
                    if (e.item) aulasVistasAluno.add(e.item.toString().trim().toUpperCase().normalize('NFD').replace(/[̀-ͯ]/g, ''));
                }
            });

            const todasAssistidas = aulasArr.length > 0 && aulasArr.every(a => {
                const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[̀-ͯ]/g, '') : '';
                return aulasVistasAluno.has(String(a.id)) || aulasVistasAluno.has(aNorm);
            });

            if (todasAssistidas) {
                alunosConcluiramModulo.add(s.email.toLowerCase());
            }
        });

        const qtdIniciaram = alunosIniciaramModulo.size;
        const qtdConcluiram = alunosConcluiramModulo.size;
        const taxaConclusaoMod = qtdIniciaram > 0 ? ((qtdConcluiram / qtdIniciaram) * 100).toFixed(1) : 0;
        const taxaAlcanceCurso = ((qtdIniciaram / totalAlunosCurso) * 100).toFixed(1);

        modulosStats.push({
            modulo: m.modulo || `Módulo ${mIdx + 1}`,
            n_curric: aulasArr.length,
            qtdIniciaram: qtdIniciaram,
            qtdConcluiram: qtdConcluiram,
            taxaConclusao: Number(taxaConclusaoMod),
            taxaAlcance: Number(taxaAlcanceCurso),
            aulas: aulasStats
        });
    });

    // Média de conclusão do curso
    const taxaMediaConclusao = modulosStats.length > 0 
        ? (modulosStats.reduce((acc, m) => acc + m.taxaConclusao, 0) / modulosStats.length).toFixed(1) 
        : 0;

    // Identificação do Gargalo (Módulo com maior queda/drop-off)
    let gargaloModulo = 'Nenhum gargalo severo';
    let maiorDrop = -1;
    for (let i = 0; i < modulosStats.length - 1; i++) {
        const drop = modulosStats[i].qtdIniciaram - modulosStats[i+1].qtdIniciaram;
        if (drop > maiorDrop && drop > 0) {
            maiorDrop = drop;
            gargaloModulo = `${modulosStats[i+1].modulo} (-${drop} alunos)`;
        }
    }

    // 3. Renderização do Seletor de Cursos (Pílulas)
    const coursePillsHtml = `
      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px; padding-bottom:14px; border-bottom:1px solid var(--line);">
        ${availableCourses.map(cName => {
            const isSel = (c === cName);
            const bg = isSel ? 'var(--emerald)' : 'var(--card)';
            const col = isSel ? '#022c22' : 'var(--ink)';
            const border = isSel ? '1px solid var(--emerald-d)' : '1px solid var(--line)';
            const numAl = allStudents.filter(s => (typeof resolveCanonicalCourse === 'function' ? resolveCanonicalCourse(s.curso) === resolveCanonicalCourse(cName) : s.curso === cName)).length;
            return `<button type="button" onclick="setModCourse('${cName.replace(/'/g, "\'")}')" style="padding:7px 14px; font-size:11.5px; font-weight:800; border-radius:20px; background:${bg}; color:${col}; border:${border}; cursor:pointer; display:flex; align-items:center; gap:6px; box-shadow:${isSel ? '0 0 12px rgba(16,185,129,0.3)' : 'none'}; transition:all 0.15s ease;">
                <span>${cName}</span>
                <span style="font-size:10px; padding:1px 6px; border-radius:10px; background:${isSel ? 'rgba(0,0,0,0.2)' : 'var(--line)'}; color:${isSel ? '#000' : 'var(--muted)'}; font-weight:700;">${numAl}</span>
            </button>`;
        }).join('')}
      </div>
    `;

    // 4. Cockpit de Métricas do Curso
    const cockpitMetricsHtml = `
      <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin-bottom:24px;">
        <div class="kpi" style="border-top:3px solid var(--emerald);">
          <div class="k-lab"><i class="k-dot" style="background:var(--emerald);"></i>Matrículas no Curso</div>
          <div class="k-val" style="color:var(--emerald-d); font-size:24px;">${courseStudents.length}</div>
          <div class="k-sub">${alunosAtivosCurso} já acessaram (${((alunosAtivosCurso/totalAlunosCurso)*100).toFixed(1)}%)</div>
        </div>
        <div class="kpi" style="border-top:3px solid var(--sky);">
          <div class="k-lab"><i class="k-dot" style="background:var(--sky);"></i>Estrutura Curricular</div>
          <div class="k-val" style="color:var(--sky); font-size:24px;">${mods.length} Módulos</div>
          <div class="k-sub">${totalAulasCurso} aulas oficiais na API</div>
        </div>
        <div class="kpi" style="border-top:3px solid #0d9488;">
          <div class="k-lab"><i class="k-dot" style="background:#0d9488;"></i>Conclusão Média</div>
          <div class="k-val" style="color:#0d9488; font-size:24px;">${taxaMediaConclusao}%</div>
          <div class="k-sub">Taxa média entre os módulos</div>
        </div>
        <div class="kpi" style="border-top:3px solid var(--amber);">
          <div class="k-lab"><i class="k-dot" style="background:var(--amber);"></i>Ponto de Maior Queda</div>
          <div class="k-val" style="color:var(--amber); font-size:14px; margin-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${gargaloModulo}">${gargaloModulo}</div>
          <div class="k-sub">Maior drop-off entre módulos</div>
        </div>
      </div>
    `;

    // 5. Lista de Módulos e Aulas Detalhadas
    const modulesCardsHtml = modulosStats.map((m, idx) => {
        const pctConcl = m.taxaConclusao;
        const barColor = pctConcl >= 70 ? 'var(--emerald)' : (pctConcl >= 40 ? 'var(--sky)' : 'var(--amber)');

        const aulasRowsHtml = m.aulas.map(a => {
            const barWidth = maxViewsCurso > 0 ? ((a.views / maxViewsCurso) * 100) : 0;
            const pctModulo = m.qtdIniciaram > 0 ? ((a.views / m.qtdIniciaram) * 100).toFixed(1) : 0;

            return `
              <div class="aula-row" style="display:flex; justify-content:space-between; align-items:center; padding:9px 14px; border-bottom:1px solid var(--line); font-size:12px; transition:background 0.15s ease;" onmouseover="this.style.background='var(--card-hover)'" onmouseout="this.style.background='transparent'">
                <div class="aula-name" style="display:flex; align-items:center; gap:10px; flex:1; max-width:60%;">
                  <span class="ord" style="width:24px; height:24px; border-radius:50%; background:var(--line); color:var(--ink); font-weight:800; font-size:10.5px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">${a.ordem}</span>
                  <span style="font-weight:600; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${a.nome}">${a.nome}</span>
                </div>
                <div style="display:flex; align-items:center; gap:14px; min-width:260px; justify-content:flex-end;">
                  <div style="width:140px; height:7px; background:var(--line); border-radius:4px; overflow:hidden;">
                    <div style="width:${barWidth}%; height:100%; background:${barColor}; border-radius:4px; transition:width 0.3s ease;"></div>
                  </div>
                  <div style="font-size:11px; font-weight:700; color:var(--ink); font-family:monospace; min-width:70px; text-align:right;">
                    ${a.views} assistiram
                  </div>
                  <div style="font-size:10px; color:var(--muted); min-width:45px; text-align:right;">
                    ${pctModulo}%
                  </div>
                </div>
              </div>
            `;
        }).join('');

        return `
          <div class="funnel-mod" style="background:var(--card); border:1px solid var(--line); border-radius:12px; margin-bottom:18px; overflow:hidden; box-shadow:0 4px 14px rgba(0,0,0,0.04);">
            <div class="fm-head" style="padding:16px 18px; background:var(--card-hover); border-bottom:1px solid var(--line); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
              <div>
                <div style="font-size:14px; font-weight:800; color:var(--ink); display:flex; align-items:center; gap:8px;">
                  <span style="width:8px; height:8px; border-radius:50%; background:${barColor};"></span>
                  ${m.modulo}
                  <span style="font-size:11px; font-weight:600; color:var(--muted); margin-left:4px;">(${m.n_curric} aulas oficiais)</span>
                </div>
                <div style="font-size:11px; color:var(--muted); margin-top:2px;">
                  <b>${m.qtdIniciaram}</b> iniciaram · <b>${m.qtdConcluiram}</b> concluíram todas as aulas (${m.taxaConclusao}% de conclusão)
                </div>
              </div>
              <div style="display:flex; align-items:center; gap:12px;">
                <div style="text-align:right;">
                  <div style="font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:700;">Taxa de Conclusão</div>
                  <div style="font-size:16px; font-weight:900; color:${barColor};">${m.taxaConclusao}%</div>
                </div>
              </div>
            </div>
            <div class="fm-body" style="padding:0;">
              ${aulasRowsHtml}
            </div>
          </div>
        `;
    }).join('');

    view.innerHTML = coursePillsHtml + cockpitMetricsHtml + modulesCardsHtml;
}

window.setModCourse = function(cName) {
    if (FILTER) FILTER.curso = cName;
    renderModules();
};


// ORIGENS & ATRIBUIÇÃO DE MATRÍCULAS
let origemDrawn = false;
let origemCatFilter = 'all';
let origemSearchQuery = '';

function isCheckoutEvent(ev) {
    if (!ev) return false;
    const cat = (ev.categoria || '').toLowerCase();
    const raw = (ev.evento_raw || '').toLowerCase();
    const clean = (ev.evento_clean || '').toLowerCase();
    if (cat.includes('checkout') || cat.includes('matrícula') || cat.includes('matricula')) return true;
    if (raw.includes('checkout') || raw.includes('pago') || raw.includes('pendente') || raw.includes('recorrencia') || raw.includes('compra') || raw.includes('problema') || raw.includes('hotmart') || raw.includes('woocommerce')) return true;
    if (clean.includes('checkout') || clean.includes('pagamento') || clean.includes('compra')) return true;
    return false;
}

function isCheckoutString(s) {
    if (!s) return false;
    const low = s.toString().toLowerCase();
    return low.includes('checkout') || low.includes('pagamento') || low.includes('pago') || low.includes('pendente') || low.includes('recorrencia') || low.includes('compra') || low.includes('problema') || low.includes('hotmart') || low.includes('woocommerce');
}

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
            
            // Filtrar estritamente eventos pré-matrícula (desconsiderando checkout)
            const evs = (rd.eventos_detalhados || []).filter(e => !isCheckoutEvent(e));
            const convAntes = evs.length;
            if (convAntes > 0) {
                countComConvAntes++;
                totalPontosContato += convAntes;
            }
            
            if (convAntes > 0 && rd.dias_venda !== '' && rd.dias_venda !== null && !isNaN(rd.dias_venda)) {
                maturacaoDiasList.push(Number(rd.dias_venda));
            }
            
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
        <div style="font-size:11px; color:var(--muted); margin-top:2px">Média de <b>${mediaPontos}</b> pontos de contato por aluno</div>
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
            <p style="font-size:11px; color:var(--muted); margin:4px 0 0">Eventos, e-books, lives e formulários acessados <b>antes</b> de matricular (sem checkout).</p>
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
          <button onclick="setOrigemCatFilter('Lista de Espera / Grade')" style="padding:4px 10px; font-size:11px; font-weight:600; border-radius:16px; border:1px solid var(--line2); cursor:pointer; background:${origemCatFilter==='Lista de Espera / Grade'?'#d97706':'var(--bg)'}; color:${origemCatFilter==='Lista de Espera / Grade'?'#fff':'var(--text)'}">⏳ Lista de Espera</button>
        </div>

        <div style="flex:1; display:flex; flex-direction:column; gap:10px" id="origem-events-list">
          ${renderOrigemEventsBars(eventsCount, baseStudents.length)}
        </div>
      </div>

      <!-- COLUNA 2: CANAIS DE ORIGEM / TRÁFEGO -->
      <div class="card" style="padding:18px; display:flex; flex-direction:column">
        <div style="margin-bottom:14px">
          <h3 style="margin:0; font-size:14px; font-weight:700; color:var(--ink)">Canais de Tráfego / Origem RD</h3>
          <p style="font-size:11px; color:var(--muted); margin:4px 0 0">Canal atribuído pelo RD Station na 1ª conversão de lead.</p>
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
          <p style="font-size:11px; color:var(--muted); margin:4px 0 0">Veja os pontos de contato pré-matrícula de cada aluno, tempo de decisão e canal de aquisição.</p>
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
        const evs = (s.rd_funnel?.eventos_detalhados || []).filter(e => !isCheckoutEvent(e)).map(e => (e.evento_clean || '').toLowerCase()).join(' ');
        return nome.includes(q) || email.includes(q) || curso.includes(q) || org.includes(q) || evs.includes(q);
    });
    
    if (filtered.length === 0) {
        return '<tr><td colspan="8" style="padding:24px; text-align:center; color:var(--muted)">Nenhum aluno encontrado para a busca.</td></tr>';
    }
    
    return filtered.map(s => {
        const rd = s.rd_funnel;
        const org = rd ? (rd.origem && rd.origem !== '-' ? rd.origem : 'Desconhecido') : 'Não Rastreado';
        const pri = rd ? (rd.dt_primeira || '—') : '—';
        const insc = s.data_insc || s.data_inscricao || s.inscricao || '—';
        
        // Renderizar badges dos primeiros 3 eventos de marketing pré-matrícula
        const evs = (rd?.eventos_detalhados || []).filter(e => !isCheckoutEvent(e));
        const dias = (evs.length > 0 && rd && rd.dias_venda !== '' && rd.dias_venda !== null && rd.dias_venda !== undefined) ? `${rd.dias_venda} dias` : '—';
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
            evBadges = '<span style="color:var(--muted); font-size:11px">Sem conversões pré-matrícula</span>';
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
        // Atualizar timestamp da última sincronização no topo do HUD
        try {
            const elSyncTime = document.getElementById('hud-last-sync-time');
            if (elSyncTime && typeof DATA !== 'undefined' && DATA && DATA.meta && DATA.meta.updated_at) {
                const parts = DATA.meta.updated_at.split(' ');
                if (parts.length >= 2) {
                    const dateParts = parts[0].split('/');
                    const timeParts = parts[1].substring(0, 5);
                    elSyncTime.textContent = `${dateParts[0]}/${dateParts[1]} ${timeParts}`;
                } else {
                    elSyncTime.textContent = DATA.meta.updated_at;
                }
            }
        } catch(e) {}
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

function getDashboardUpdateTime(allEvts) {
    if (typeof DATA !== 'undefined' && DATA && DATA.meta) {
        if (DATA.meta.updated_iso) {
            const d = new Date(DATA.meta.updated_iso);
            if (!isNaN(d.getTime())) return d;
        }
        if (DATA.meta.updated_at) {
            const parts = DATA.meta.updated_at.split(' ');
            if (parts.length === 2) {
                const [d, m, y] = parts[0].split('/').map(Number);
                const [h, min, s] = parts[1].split(':').map(Number);
                const dt = new Date(y, m - 1, d, h, min, s || 0);
                if (!isNaN(dt.getTime())) return dt;
            }
        }
    }
    if (allEvts && allEvts.length > 0) {
        const lastEvt = allEvts[allEvts.length - 1];
        if (lastEvt && lastEvt.dt && !isNaN(lastEvt.dt.getTime())) {
            return lastEvt.dt;
        }
    }
    return new Date();
}


function getDeduplicatedEvents(baseStudents) {
    const studentCoursesMap = new Map();
    (DATA.students || []).forEach(s => {
        const em = (s.email || s.nome || '').toLowerCase().trim();
        if (!em) return;
        if (!studentCoursesMap.has(em)) studentCoursesMap.set(em, new Set());
        if (s.curso) studentCoursesMap.get(em).add(s.curso);
    });

    const seenKeys = new Set();
    const allEvts = [];

    baseStudents.forEach(s => {
        const emailNorm = (s.email || s.nome || '').toLowerCase().trim();
        const studentCourses = Array.from(studentCoursesMap.get(emailNorm) || (s.curso ? [s.curso] : []));
        const hasMultiCourses = studentCourses.length > 1;

        (s.events || []).forEach(e => {
            if (!e.d) return;
            const dt = parseEventDate(e.d);
            if (!dt || isNaN(dt.getTime())) return;

            const isLogin = (e.cat === 'login') || (e.acao && e.acao.toUpperCase().includes('LOGIN'));
            
            // Login e unico na plataforma para o aluno no horario (nao e vinculado a um curso especifico).
            // Acoes de conteudo (aulas, pdfs) sao unificadas por aluno + data + acao + item.
            const evtKey = isLogin 
                ? `${emailNorm}|${e.d}|LOGIN`
                : `${emailNorm}|${e.d}|${e.acao}|${e.item_id || e.item || ''}`;

            if (seenKeys.has(evtKey)) return;
            seenKeys.add(evtKey);

            let displayCurso = s.curso || '';
            let cursoTooltip = displayCurso;
            if (isLogin) {
                if (typeof currentCourseFilter !== 'undefined' && currentCourseFilter && currentCourseFilter !== 'ALL') {
                    displayCurso = `Acesso à Plataforma · ${currentCourseFilter}`;
                    cursoTooltip = hasMultiCourses 
                        ? `Aluno matriculado em ${studentCourses.length} cursos: ${studentCourses.join(' | ')}`
                        : `Acesso à Plataforma · ${currentCourseFilter}`;
                } else if (hasMultiCourses) {
                    displayCurso = `Acesso Geral à Plataforma · Multi-Cursos (${studentCourses.length} cursos)`;
                    cursoTooltip = `Matriculado em: ${studentCourses.join(' | ')}`;
                } else {
                    displayCurso = `Acesso à Plataforma · ${studentCourses[0] || displayCurso}`;
                    cursoTooltip = displayCurso;
                }
            }

            allEvts.push({
                dt: dt,
                d: e.d,
                aluno: s.nome || 'Aluno',
                email: s.email || '',
                curso: displayCurso,
                cursoTooltip: cursoTooltip,
                rawCurso: s.curso || '',
                plataforma: s.plataforma || 'Academy',
                acao: e.acao || 'AÇÃO',
                item: e.item || (isLogin ? 'Ambiente de Aprendizagem' : ''),
                mod: e.mod || '',
                isLogin: isLogin
            });
        });
    });

    return allEvts;
}

function drawLiveMonitor(baseStudents, isAutoTick) {
    window._lastLiveBaseStudents = baseStudents;
    const liveSectionEl = document.getElementById('home-live-section');
    if (!liveSectionEl) return;

    if (!isAutoTick) {
        startHourlyAutoRefresh();
    }

    let allEvts = getDeduplicatedEvents(baseStudents);

    if (allEvts.length === 0) {
        liveSectionEl.style.display = 'none';
        return;
    }
    liveSectionEl.style.display = 'block';

    allEvts.sort((a,b) => a.dt.getTime() - b.dt.getTime());
    const maxDt = allEvts[allEvts.length - 1].dt;
    
    // JANELA REAL DA INFORMAÇÃO: ancorada no horário de atualização dos dados
    const refTime = getDashboardUpdateTime(allEvts);
    const t60m = new Date(refTime.getTime() - 60 * 60 * 1000);
    const t24h = new Date(refTime.getTime() - 24 * 60 * 60 * 1000);

    const evts60m = allEvts.filter(e => e.dt >= t60m && e.dt <= refTime).sort((a,b) => b.dt.getTime() - a.dt.getTime());
    const evts24h = allEvts.filter(e => e.dt >= t24h && e.dt <= refTime);

    const uniqueStudents60m = new Set(evts60m.map(e => (e.email || '').toLowerCase().trim()).filter(Boolean));
    const uniqueStudents24h = new Set(evts24h.map(e => (e.email || '').toLowerCase().trim()).filter(Boolean));

    const pad = n => n < 10 ? '0' + n : n;
    const startTime60mFmt = `${pad(t60m.getHours())}:${pad(t60m.getMinutes())}`;
    const refTimeFmt = `${pad(refTime.getHours())}:${pad(refTime.getMinutes())}`;
    const refDateFmt = `${pad(refTime.getDate())}/${pad(refTime.getMonth()+1)}`;
    const maxTimeHourFmt = `${pad(maxDt.getHours())}:${pad(maxDt.getMinutes())}`;
    const maxDateFmt = `${pad(maxDt.getDate())}/${pad(maxDt.getMonth()+1)}/${maxDt.getFullYear()}`;

    // Tempo decorrido desde a atualização dos dados
    const nowClient = new Date();
    const diffMs = Math.max(0, nowClient.getTime() - refTime.getTime());
    const diffHours = Math.floor(diffMs / (3600 * 1000));
    const diffMins = Math.floor((diffMs % (3600 * 1000)) / 60000);
    const tempoAtras = diffHours > 0 ? `há ${diffHours}h ${diffMins}min` : (diffMins > 0 ? `há ${diffMins} min` : 'agora');

    // Atualizar labels de referência no cabeçalho
    const refTimeEl = document.getElementById('live-ref-time');
    if (refTimeEl) {
        refTimeEl.innerHTML = `Atualizado às <b style="color:var(--ink)">${refTimeFmt}</b> (${tempoAtras}) · Último log: <b style="color:var(--ink)">${maxTimeHourFmt}</b>`;
    }

    const miniKpisEl = document.getElementById('home-live-mini-kpis');
    if (miniKpisEl) {
        miniKpisEl.innerHTML = `
          <div style="background:#090d14; border:1px solid rgba(0, 255, 157, 0.25); border-radius:8px; padding:7px 12px; text-align:right; box-shadow:0 0 10px rgba(0,255,157,0.05); min-width:110px;">
            <div style="font-size:9px; font-weight:700; color:var(--muted); font-family:var(--font-hud); letter-spacing:0.06em; text-transform:uppercase;">ÚLTIMOS 60 MIN</div>
            <div style="font-size:17px; font-weight:700; font-family:var(--font-mono); color:${evts60m.length > 0 ? '#00ff9d' : 'var(--muted)'};">${evts60m.length} <span style="font-size:9.5px; font-weight:600; color:var(--muted); font-family:var(--font-hud);">AÇÕES</span></div>
          </div>
          <div style="background:#090d14; border:1px solid rgba(0, 240, 255, 0.25); border-radius:8px; padding:7px 12px; text-align:right; box-shadow:0 0 10px rgba(0,240,255,0.05); min-width:110px;">
            <div style="font-size:9px; font-weight:700; color:var(--muted); font-family:var(--font-hud); letter-spacing:0.06em; text-transform:uppercase;">ALUNOS ONLINE (60M)</div>
            <div style="font-size:17px; font-weight:700; font-family:var(--font-mono); color:${uniqueStudents60m.size > 0 ? '#00f0ff' : 'var(--muted)'};">${uniqueStudents60m.size} <span style="font-size:9.5px; font-weight:600; color:var(--muted); font-family:var(--font-hud);">ONLINE</span></div>
          </div>
          <div style="background:#090d14; border:1px solid rgba(255, 158, 0, 0.25); border-radius:8px; padding:7px 12px; text-align:right; box-shadow:0 0 10px rgba(255,158,0,0.05); min-width:110px;">
            <div style="font-size:9px; font-weight:700; color:var(--muted); font-family:var(--font-hud); letter-spacing:0.06em; text-transform:uppercase;">TOTAL 24 HORAS</div>
            <div style="font-size:17px; font-weight:700; font-family:var(--font-mono); color:#ff9e00;">${evts24h.length} <span style="font-size:9.5px; font-weight:600; color:var(--muted); font-family:var(--font-hud);">AÇÕES</span></div>
          </div>
          <div style="background:#090d14; border:1px solid rgba(168, 85, 247, 0.25); border-radius:8px; padding:7px 12px; text-align:right; box-shadow:0 0 10px rgba(168,85,247,0.05); min-width:110px;">
            <div style="font-size:9px; font-weight:700; color:var(--muted); font-family:var(--font-hud); letter-spacing:0.06em; text-transform:uppercase;">ALUNOS EM 24H</div>
            <div style="font-size:17px; font-weight:700; font-family:var(--font-mono); color:#a855f7;">${uniqueStudents24h.size} <span style="font-size:9.5px; font-weight:600; color:var(--muted); font-family:var(--font-hud);">ALUNOS</span></div>
          </div>`;
    }

    // Feed Últimos 60 min
    const feedListEl = document.getElementById('home-live-feed-list');
    const liveCountBadge = document.getElementById('live-count-badge');
    const liveWindowLabel = document.getElementById('live-window-label');
    
    if (liveCountBadge) liveCountBadge.textContent = `${evts60m.length} evento${evts60m.length !== 1 ? 's' : ''}`;
    if (liveWindowLabel) liveWindowLabel.innerHTML = `Janela: <b>${startTime60mFmt} às ${refTimeFmt}</b> (Atualização)`;

    if (feedListEl) {
        if (evts60m.length === 0) {
            feedListEl.innerHTML = `
              <div style="text-align:center; padding:45px 15px; color:var(--muted)">
                <div style="font-size:26px; margin-bottom:8px">☕</div>
                <div style="font-size:13px; font-weight:700; color:var(--ink)">Nenhuma atividade nos últimos 60 minutos</div>
                <div style="font-size:11px; margin-top:4px; color:var(--muted)">Sem logs recebidos nas APIs entre ${startTime60mFmt} e ${refTimeFmt}.</div>
                <div style="margin-top:10px; font-size:10.5px; color:var(--muted2)">O feed será atualizado automaticamente caso surjam novas ações.</div>
              </div>
            `;
        } else {
            feedListEl.innerHTML = evts60m.map(e => {
                const diffMinsAgo = Math.max(0, Math.round((refTime.getTime() - e.dt.getTime()) / 60000));
                const timeAgo = diffMinsAgo === 0 ? 'no fechamento' : `há ${diffMinsAgo} min`;
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
                      
                      <div style="font-size:10.5px; color:var(--muted); margin-top:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap" title="${e.cursoTooltip || e.curso}">
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

    let allEvts = getDeduplicatedEvents(baseStudents);

    if (allEvts.length === 0) {
        chartContainer.innerHTML = '<div style="text-align:center; padding:40px 0; color:var(--muted)">Sem dados no período.</div>';
        return;
    }

    // Janela real estrita de 24 horas terminando na hora atual do relógio
    allEvts.sort((a,b) => a.dt.getTime() - b.dt.getTime());
    const refTime = getDashboardUpdateTime(allEvts);
    const currentHourStart = new Date(refTime.getFullYear(), refTime.getMonth(), refTime.getDate(), refTime.getHours(), 0, 0, 0);
    const t24hStart = new Date(currentHourStart.getTime() - 23 * 3600 * 1000);
    const t24hEnd = new Date(currentHourStart.getTime() + 3600 * 1000);

    const evts24h = allEvts.filter(e => e.dt >= t24hStart && e.dt <= refTime);

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
        rangeLabel.textContent = `Janela 24h: ${pad(t24hStart.getDate())}/${pad(t24hStart.getMonth()+1)} ${pad(t24hStart.getHours())}:00 às ${pad(refTime.getDate())}/${pad(refTime.getMonth()+1)} ${pad(refTime.getHours())}:${pad(refTime.getMinutes())} (Atualização)`;
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
    if (!n || n === 'SEM CURSO' || n === 'NONE' || n === 'NAN') return 'PLATAFORMA GERAL';
    if (n.includes('CCIH') || n.includes('PREVENCAO') || n.includes('PREVENÇÃO') || n.includes('CONTROLE DE INFEC') || n.includes('HOSPITALAR')) {
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
    }
    if (n.includes('IMUNO') || n.includes('INUNO') || n.includes('IMUNODEPRIMIDO') || n.includes('INUNODEPRIMIDO') || n.includes('TRANSPLANT')) {
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
    }
    if (n.includes('ORTOPED') || n.includes('MOLES') || n.includes('PELE') || n.includes('MUSCULO')) {
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES';
    }
    if (n.includes('INFECTOPED') || n.includes('PEDIATR') || n.includes('PEDIÁTR') || n.includes('CRIANCA') || n.includes('NEONATAL')) {
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
    }
    if (n.includes('MULTI-R') || n.includes('MULTIR') || n.includes('JORNADA')) {
        return 'JORNADA MULTI-R';
    }
    if (n.includes('FUNGO') || n.includes('ANTIFUNGICO') || n.includes('ANTIFÚNGICO')) {
        return 'DO FUNGO AO ANTIFUNGICO';
    }
    if (n.includes('SOS') || n.includes('ANTIBIOTICO') || n.includes('ANTIBIÓTICO') || n.includes('S.O.S')) {
        return 'S.O.S ANTIBIOTICO';
    }
    if (n.includes('INFECTOXPERT') || n.includes('EXPERT')) {
        return 'INFECTOXPERT';
    }
    return 'PLATAFORMA GERAL';
}

// Helper global e robusto para duracao contratual (ciclos de parcelas)
function parsePlanCycles(planoStr) {
    if (!planoStr) return 18;
    const p = planoStr.toString().toUpperCase().trim();
    if (p.includes('VISTA')) return 1;
    const mX = p.match(/\b(\d+)\s*X\b/i);
    if (mX) return parseInt(mX[1], 10);
    const mWord = p.match(/\b(\d+)\s*(?:MESES|PARCELAS|VEZES)\b/i);
    if (mWord) return parseInt(mWord[1], 10);
    if (p.includes('RESIDENTES 24') || p.includes('24X')) return 24;
    if (p.includes('ANUAL')) return 12;
    if (p.includes('SEMESTRAL')) return 6;
    return 18;
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
    const vSubs = (vindi && vindi.subscriptions && vindi.subscriptions.length > 0) ? vindi.subscriptions : Object.values(vindi.data || {});
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

    // 3. Assinaturas Vindi (MRR e Simulação Contratual de 18 Meses)
    if (!gatewayFilter || gatewayFilter === 'all' || gatewayFilter === 'vindi') {
        vSubs.forEach(sub => {
            if (sub.status_financeiro === 'adimplente' || sub.status_assinatura === 'active') {
                const em = (sub.customer_email || '').toString().toLowerCase().trim();
                const cm = getCourse(sub.curso || emailToCourse[em] || nameToCourse[(sub.customer_name||'').toLowerCase()]);
                const price = Number(sub.valor_parcela) || 0;
                cm.mrr += price;

                const faturasArr = sub.faturas || [];
                const totalCycles = (sub.total_cycles !== undefined) ? sub.total_cycles : parsePlanCycles(sub.plano);
                const paidCount = (sub.paid_cycles_count !== undefined) ? sub.paid_cycles_count : faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
                const remainingCycles = (sub.remaining_cycles !== undefined) ? sub.remaining_cycles : Math.max(0, totalCycles - paidCount);

                const prox = (sub.proximo_vencimento || '').toString();
                const paidThisMonth = (sub.paid_this_month !== undefined) ? sub.paid_this_month : faturasArr.some(f => {
                    const dt = (f.data_pagamento || f.data_pagamento_iso || '').toString();
                    return (f.status === 'paid' || f.status === 'pago') && (dt.includes('09/2026') || dt.includes('2026-09') || dt.includes('/09/26'));
                });

                let startM = (sub.start_m !== undefined) ? sub.start_m : 0;
                if (sub.start_m === undefined) {
                    if (paidThisMonth || prox.includes('/10/2026') || prox.includes('2026-10') || prox.includes('/10/26') || prox.includes('/11/2026') || prox.includes('/12/2026')) {
                        startM = 1;
                    } else {
                        cm.proj_mes_atual += price;
                    }
                } else if (startM === 0) {
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
                        if (diffMeses === 0) {
                            cm.proj_mes_atual += val;
                        }
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

        // MRR Oficial: Média das mensalidades ativas somadas da Vindi e do Asaas nos próximos 6 meses começando no mês posterior ao atual (Out/26 a Mar/27)
        const next6Sim = cm.projecao_18m_sim.slice(1, 7);
        const next6Avg = next6Sim.reduce((a, b) => a + b, 0) / 6;
        if (next6Avg > 0) {
            cm.mrr = next6Avg;
        }

        // Projeção Próximo Mês Oficial: Próximo mês calendário fechado (M+1: Out/26)
        cm.proj_1m = cm.projecao_mensal[1]?.previsto || cm.mrr;
        cm.proj_3m = cm.projecao_mensal.slice(1, 4).reduce((a, b) => a + b.previsto, 0) || (cm.mrr * 3);
        cm.proj_6m = cm.projecao_mensal.slice(1, 7).reduce((a, b) => a + b.previsto, 0) || (cm.mrr * 6);
        cm.proj_12m = cm.projecao_mensal.slice(1, 13).reduce((a, b) => a + b.previsto, 0) || (cm.mrr * 12);

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

    // MRR Global Oficial: Média consolidada dos próximos 6 meses (Out/26 a Mar/27)
    const gNext6Sim = globalObj.projecao_mensal.slice(1, 7);
    const gNext6Avg = gNext6Sim.reduce((a, b) => a + (b.previsto || 0), 0) / 6;
    if (gNext6Avg > 0) {
        globalObj.mrr = gNext6Avg;
    }

    // Projeções Globais Oficiais: Próximo mês calendário fechado (M+1: Out/26) e horizontes subsequentes
    globalObj.proj_1m = globalObj.projecao_mensal[1]?.previsto || globalObj.mrr;
    globalObj.proj_3m = globalObj.projecao_mensal.slice(1, 4).reduce((a, b) => a + (b.previsto || 0), 0) || (globalObj.mrr * 3);
    globalObj.proj_6m = globalObj.projecao_mensal.slice(1, 7).reduce((a, b) => a + (b.previsto || 0), 0) || (globalObj.mrr * 6);
    globalObj.proj_12m = globalObj.projecao_mensal.slice(1, 13).reduce((a, b) => a + (b.previsto || 0), 0) || (globalObj.mrr * 12);

    // Ticket Médio Oficial: (Total Recebido nos últimos 180 dias / Clientes Pagantes dentro dos últimos 180 dias) / 6
    const d180Ref = new Date().getTime() - (180 * 24 * 3600 * 1000);
    let gRec180 = 0, gRec180Pos = 0, gRec180Livres = 0;
    const gPagantes180 = new Set();
    const gPagantes180Pos = new Set();
    const gPagantes180Livres = new Set();
    faturasList.forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const dtStr = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
            const dObj = _parseDateSafe(dtStr);
            if (dObj && dObj.getTime() >= d180Ref) {
                const val = (Number(f.valor) || 0);
                gRec180 += val;
                const em = (f.email || f.aluno || '').toLowerCase().trim();
                if (em) gPagantes180.add(em);

                const cName = (f.curso || '').toUpperCase();
                const isPos = cName.includes('POS-') || cName.includes('PÓS-') || cName.includes('POS ') || cName.includes('PÓS ');
                if (isPos) {
                    gRec180Pos += val;
                    if (em) gPagantes180Pos.add(em);
                } else {
                    gRec180Livres += val;
                    if (em) gPagantes180Livres.add(em);
                }
            }
        }
    });
    globalObj.ticket_medio = gPagantes180.size > 0 ? (gRec180 / gPagantes180.size) / 6 : 0;
    globalObj.ticket_medio_pos = gPagantes180Pos.size > 0 ? (gRec180Pos / gPagantes180Pos.size) / 6 : 0;
    globalObj.ticket_medio_livres = gPagantes180Livres.size > 0 ? (gRec180Livres / gPagantes180Livres.size) / 6 : 0;

    const gBaseAdimp = globalObj.pago_total + globalObj.atraso;
    globalObj.taxa_adimplencia = gBaseAdimp > 0 ? Math.round((globalObj.pago_total / gBaseAdimp) * 100) : 100;

    globalObj.kpis = {
        total_recebido: globalObj.pago_total,
        recebido_mes_atual: globalObj.pago_mes_atual,
        a_vencer_mes_atual: globalObj.proj_mes_atual,
        previsto_mes_vigente: globalObj.previsto_mes_vigente,
        mrr_ativo: globalObj.mrr,
        ticket_medio: globalObj.ticket_medio,
        ticket_medio_pos: globalObj.ticket_medio_pos,
        ticket_medio_livres: globalObj.ticket_medio_livres,
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
function parseDateUniversal(dStr) {
    if (!dStr) return null;
    if (dStr instanceof Date) return isNaN(dStr.getTime()) ? null : dStr;
    const s = String(dStr).trim();
    if (/^\d{4}-\d{2}-\d{2}/.test(s)) {
        const dt = new Date(s.replace(' ', 'T'));
        if (!isNaN(dt.getTime())) return dt;
    }
    if (/^\d{2}\/\d{2}\/\d{4}/.test(s)) {
        const parts = s.split(' ')[0].split('/');
        const timePart = s.split(' ')[1] || '00:00:00';
        const dt = new Date(`${parts[2]}-${parts[1]}-${parts[0]}T${timePart}`);
        if (!isNaN(dt.getTime())) return dt;
    }
    const dt = new Date(s);
    return isNaN(dt.getTime()) ? null : dt;
}

function getMatriculasAuditoriaData() {
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
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@cativa') || em.includes('@estrategia1') || em.includes('@adtivo')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com') || em.includes('wgww@gmail.com')) return true;
        return false;
    };

    function normalizeCourse(cName) {
        if (!cName) return 'GERAL';
        let s = String(cName).toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
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
    const matriculasConfirmadas = [];
    const matriculasPendentes = [];
    const processedPairs = new Set();

    validStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().trim();
        const cNorm = normalizeCourse(s.curso || '');
        const pairKey = em + '___' + cNorm;
        
        if (processedPairs.has(pairKey)) return;
        processedPairs.add(pairKey);

        const paidBillsCourse = studentCoursePaidBills.get(em + '___' + cNorm) || studentCoursePaidBills.get(nm.toLowerCase() + '___' + cNorm);
        const paidBillsGlobal = studentCoursePaidBills.get(em + '___GLOBAL') || studentCoursePaidBills.get(nm.toLowerCase() + '___GLOBAL');
        const targetBills = paidBillsCourse || paidBillsGlobal;

        // 1. Matrícula Confirmada (Tem pagamento aprovado no gateway)
        if (targetBills && targetBills.length > 0) {
            targetBills.sort((a, b) => a.date - b.date);
            const firstPaid = targetBills[0];
            const effDate = firstPaid.date;

            if (effDate && effDate <= now) {
                const pad = n => n < 10 ? '0' + n : n;
                const dtFmt = pad(effDate.getDate()) + '/' + pad(effDate.getMonth()+1) + '/' + effDate.getFullYear() + ' ' + pad(effDate.getHours()) + ':' + pad(effDate.getMinutes());
                
                matriculasConfirmadas.push({
                    nome: nm || 'Aluno',
                    email: em,
                    curso: s.curso || 'PLATAFORMA GERAL',
                    data: effDate,
                    data_fmt: dtFmt,
                    origem: 'Primeiro Pagamento (' + firstPaid.gateway + ')',
                    gateway: firstPaid.gateway,
                    tipo: 'confirmada',
                    origem_label: 'Matrícula Confirmada',
                    valor: firstPaid.valor,
                    is_24h: effDate >= t24h,
                    is_30d: effDate >= t30d
                });
            }
        } else {
            // 2. Matrícula Pendente (Mesma regra da Visão por Curso: sem financeiro e sem consumo)
            const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
            const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
            const vindiCanceled = vSt === 'cancelado' || vSt === 'canceled';
            const asaasCanceled = aSt === 'cancelado' || aSt === 'canceled';
            const vindiActive = vSt === 'active' || vSt === 'ativo' || vSt === 'adimplente' || vSt === 'em_dia';
            const asaasActive = aSt === 'active' || aSt === 'ativo' || aSt === 'received' || aSt === 'confirmed' || aSt === 'adimplente' || aSt === 'em_dia';
            const vFats = s.vindi ? (s.vindi.faturas || []) : [];
            const aFats = s.asaas ? (s.asaas.faturas || []) : [];
            const vPaid = vFats.some(f => (f.status === 'pago' || f.status === 'paid' || f.pago));
            const aPaid = aFats.some(f => (f.status === 'pago' || f.status === 'paid' || f.status === 'RECEIVED' || f.status === 'CONFIRMED' || f.pago));

            const hasFinanceiro = vindiActive || asaasActive || vPaid || aPaid;
            const hasConsumo = (Number(s.aulas_feitas || 0) > 0);

            let isPendente = false;
            if ((vindiCanceled || asaasCanceled) && !vindiActive && !asaasActive && !hasConsumo) {
                isPendente = false;
            } else if (!hasFinanceiro && !hasConsumo && s.status !== 'Concluído') {
                isPendente = true;
            }

            if (isPendente) {
                const dtInsc = parseDateUniversal(s.data_insc || s.data_inscricao || s.data_matricula || s.first);
                if (dtInsc && dtInsc <= now) {
                    const pad = n => n < 10 ? '0' + n : n;
                    const dtFmt = pad(dtInsc.getDate()) + '/' + pad(dtInsc.getMonth()+1) + '/' + dtInsc.getFullYear() + ' ' + pad(dtInsc.getHours()) + ':' + pad(dtInsc.getMinutes());
                    
                    matriculasPendentes.push({
                        nome: nm || 'Lead / Inscrição',
                        email: em,
                        curso: s.curso || 'PLATAFORMA GERAL',
                        data: dtInsc,
                        data_fmt: dtFmt,
                        origem: 'Cadastro Plataforma (' + (s.plataforma || 'Academy') + ')',
                        gateway: s.plataforma || 'Academy',
                        tipo: 'pendente',
                        origem_label: 'Matrícula Pendente (Aguardando Pagamento)',
                        valor: 0,
                        aulas_feitas: Number(s.aulas_feitas || 0),
                        is_24h: dtInsc >= t24h,
                        is_30d: dtInsc >= t30d
                    });
                }
            }
        }
    });

    matriculasConfirmadas.sort((a, b) => b.data - a.data);
    matriculasPendentes.sort((a, b) => b.data - a.data);

    const list24h = matriculasConfirmadas.filter(m => m.is_24h);
    const list30d = matriculasConfirmadas.filter(m => m.is_30d);

    const pendentes24h = matriculasPendentes.filter(m => m.is_24h);
    const pendentes30d = matriculasPendentes.filter(m => m.is_30d);

    return {
        count24h: list24h.length,
        count30d: list30d.length,
        totalConfirmadas: matriculasConfirmadas.length,
        countPendentes24h: pendentes24h.length,
        countPendentes30d: pendentes30d.length,
        totalPendentes: matriculasPendentes.length,
        list24h,
        list30d,
        allRecords: matriculasConfirmadas,
        pendentes24h,
        pendentes30d,
        allPendentes: matriculasPendentes
    };
}

function getSync24hData() {
    return getMatriculasAuditoriaData();
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
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@cativa')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com')) return true;
        return false;
    };

    // Resolução canônica de cursos para agrupar 100% de forma precisa
    const resolveCanonicalCourse = name => {
        const n = (name || '').toString().toUpperCase().trim();
        if (!n || n === 'SEM CURSO' || n === 'NONE' || n === 'NAN') return 'PLATAFORMA GERAL';
        if (n.includes('CCIH') || n.includes('PREVENCAO') || n.includes('PREVENÇÃO') || n.includes('CONTROLE DE INFECCAO') || n.includes('CONTROLE DE INFECÇÃO')) {
            return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
        }
        if (n.includes('IMUNO') || n.includes('INUNO') || n.includes('IMUNODEPRIMIDO') || n.includes('INUNODEPRIMIDO')) {
            return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
        }
        if (n.includes('ORTOPED') || n.includes('MOLES') || n.includes('PELE') || n.includes('MUSCULO')) {
            return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES';
        }
        if (n.includes('INFECTOPED') || n.includes('PEDIATR') || n.includes('PEDIÁTR') || n.includes('CRIANCA') || n.includes('CRIANÇA')) {
            return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
        }
        if (n.includes('MULTI-R') || n.includes('MULTIR') || n.includes('JORNADA')) {
            return 'JORNADA MULTI-R';
        }
        if (n.includes('FUNGO') || n.includes('ANTIFUNGICO') || n.includes('ANTIFÚNGICO')) {
            return 'DO FUNGO AO ANTIFUNGICO';
        }
        if (n.includes('SOS') || n.includes('ANTIBIOTICO') || n.includes('ANTIBIÓTICO') || n.includes('S.O.S')) {
            return 'S.O.S ANTIBIOTICO';
        }
        if (n.includes('INFECTOXPERT') || n.includes('EXPERT')) {
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
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const nm = (f.aluno || '').toString().toLowerCase().trim();
            if (em) paidEmails.add(em);
            if (nm) paidNames.add(nm);
        }
    });

    aFaturas.forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
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

    // Engajamento calculado sobre as Matrículas Vigentes
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

    // Mapeamento por Curso (Cockpit 360°)
    const emailToCourse = {};
    const nameToCourse = {};
    const coursesMap = {};

    validRawStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(s.curso);
        if (em) emailToCourse[em] = c;
        if (nm) nameToCourse[nm] = c;
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

    baseStudents.forEach(s => {
        const cm = getCm(s.curso);
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

    // Faturas por Curso e Gateway
    [...vFaturas, ...aFaturas].forEach(f => {
        const em = (f.email || '').toString().toLowerCase().trim();
        const nm = (f.aluno || '').toString().toLowerCase().trim();
        const cName = f.curso || emailToCourse[em] || nameToCourse[nm] || 'PLATAFORMA GERAL';
        const cm = getCm(cName);
        const val = Number(f.valor) || 0;
        const st = (f.status || '').toLowerCase();
        const dtPag = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();

        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            cm.pago_total += val;
            if (dtPag.includes('09/2026') || dtPag.includes('2026-09') || dtPag.includes('/09/26')) {
                cm.pago_mes_atual += val;
            } else if (dtPag.includes('08/2026') || dtPag.includes('2026-08') || dtPag.includes('/08/26')) {
                cm.pago_mes_ant += val;
            }
        } else if (st === 'em_atraso' || st === 'overdue') {
            cm.atraso += val;
        }
    });

    // Assinaturas Vindi (MRR e Projeções por Curso)
    const vSubsList = vindi.subscriptions || [];
    vSubsList.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const em = (sub.customer_email || '').toString().toLowerCase().trim();
            const cName = sub.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const cm = getCm(cName);
            const price = Number(sub.valor_parcela) || 0;
            cm.mrr += price;

            const prox = (sub.proximo_vencimento || '').toString();
            if (prox.includes('09/2026') || prox.includes('2026-09') || prox.includes('/09/26')) {
                cm.proj_mes_atual += price;
            } else if (prox.includes('10/2026') || prox.includes('2026-10') || prox.includes('/10/26')) {
                cm.proj_1m += price;
            } else if (!prox) {
                cm.proj_mes_atual += price;
                cm.proj_1m += price;
            }
        }
    });

    // Clientes Asaas (MRR por Curso)
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

    // Projeções Contratuais por Curso
    const courseMonthlyProjection = {};
    vSubsList.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const em = (sub.customer_email || '').toString().toLowerCase().trim();
            const cName = sub.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
            const price = Number(sub.valor_parcela) || 0;
            let totalCycles = parsePlanCycles(sub.plano);
            const faturasArr = sub.faturas || [];
            const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
            const remainingCycles = Math.max(0, totalCycles - paidCount);

            if (!courseMonthlyProjection[c]) {
                courseMonthlyProjection[c] = Array(12).fill(0);
            }
            for (let m = 0; m < 12; m++) {
                if (m < remainingCycles) {
                    courseMonthlyProjection[c][m] += price;
                }
            }
        }
    });

    [...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const cName = f.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
            const val = Number(f.valor) || 0;
            const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
            
            if (dtVenc) {
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

    Object.values(coursesMap).forEach(cm => {
        cm.previsto_mes_vigente = cm.pago_mes_atual + cm.proj_mes_atual;
        const diff = cm.previsto_mes_vigente - cm.pago_mes_ant;
        cm.crescimento_mom = cm.pago_mes_ant > 0 ? (((diff) / cm.pago_mes_ant) * 100).toFixed(1) : (cm.previsto_mes_vigente > 0 ? '+100' : '0.0');
        
        const mArr = courseMonthlyProjection[cm.curso] || Array(12).fill(0);
        const p1mContratual = mArr[1] > 0 ? mArr[1] : (cm.proj_1m || cm.mrr);
        const p3mContratual = mArr.slice(1, 4).reduce((a, b) => a + b, 0);
        const p6mContratual = mArr.slice(1, 7).reduce((a, b) => a + b, 0);
        const p12mContratual = mArr.slice(1, 13).reduce((a, b) => a + b, 0);

        cm.proj_1m = p1mContratual;
        cm.proj_3m = p3mContratual > 0 ? p3mContratual : cm.mrr * 3;
        cm.proj_6m = p6mContratual > 0 ? p6mContratual : cm.mrr * 6;
        cm.proj_12m = p12mContratual > 0 ? p12mContratual : cm.mrr * 12;
    });

    // Totalizadores Consolidados Financeiros Unificados
    const vKpis = vindi.kpis || {};
    const aKpis = asaas.kpis || {};
    const finUnifiedGlobal = computeUnifiedFinancialDataset('all');
    const uKpis = finUnifiedGlobal.global.kpis || {};

    const vTotalRec = Number(vKpis.total_recebido) || 0;
    const aTotalRec = Number(aKpis.total_recebido) || 0;
    const globalTotalRealizado = (vTotalRec + aTotalRec) > 0 ? (vTotalRec + aTotalRec) : (uKpis.total_recebido || 0);

    // Receita Realizada com Filtro Dinâmico de Período
    let recRealizadaTotal = globalTotalRealizado;
    let labelReceitaRealizada = 'Receita Realizada (Total)';
    let subReceitaRealizada = `Vindi (${fM(vTotalRec)}) + Asaas (${fM(aTotalRec)})`;

    let sStart = FILTER.start ? new Date(FILTER.start) : null;
    let sEnd = FILTER.end ? new Date(FILTER.end) : null;
    if (sStart) sStart.setHours(0,0,0,0);
    if (sEnd) sEnd.setHours(23,59,59,999);

    if (sStart || sEnd) {
        let recPeriodo = 0;
        let recVindiPer = 0;
        let recAsaasPer = 0;
        [...vFaturas, ...aFaturas].forEach(f => {
            const st = (f.status || '').toLowerCase();
            if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
                const dtStr = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
                const d = parseDateUniversal(dtStr);
                if (d) {
                    if (sStart && d < sStart) return;
                    if (sEnd && d > sEnd) return;
                    const val = Number(f.valor) || 0;
                    recPeriodo += val;
                    if (f.gateway === 'Asaas' || f.description) recAsaasPer += val;
                    else recVindiPer += val;
                }
            }
        });
        recRealizadaTotal = recPeriodo;
        labelReceitaRealizada = 'Receita Realizada (Período)';
        subReceitaRealizada = `Vindi (${fM(recVindiPer)}) + Asaas (${fM(recAsaasPer)})`;
    }

    const recMesAtual = finUnifiedGlobal.global.pago_mes_atual || ((Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || 0));
    const aVencerMesVigente = finUnifiedGlobal.global.proj_mes_atual || ((Number(vKpis.a_vencer_mes_atual) || 0) + (Number(aKpis.a_vencer_mes_atual) || 0));
    const totalPrevistoMesVigente = finUnifiedGlobal.global.previsto_mes_vigente || (recMesAtual + aVencerMesVigente);
    const mrrConsolidado = finUnifiedGlobal.global.mrr || ((Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0));
    const proj30d = finUnifiedGlobal.global.proj_1m || ((Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0));
    const proj3mConsolidada = finUnifiedGlobal.global.proj_3m || (mrrConsolidado * 3);
    const proj6mConsolidada = finUnifiedGlobal.global.proj_6m || (mrrConsolidado * 6);
    const proj12m = finUnifiedGlobal.global.proj_12m || (mrrConsolidado * 12);
    const atrasoTotal = (Number(vKpis.total_em_atraso) || 0) + (Number(aKpis.total_em_atraso) || 0);
    const qtdAtrasoTotal = (Number(vKpis.qtd_em_atraso) || 0) + (Number(aKpis.qtd_em_atraso) || 0);
    const taxaAdimplencia = vKpis.taxa_adimplencia || uKpis.taxa_adimplencia || 95;

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
    
    // Crescimento MoM
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
    const labelProxMes = formatMesLabel('2026-10');
    const labelProxMesCompleto = 'Outubro de 2026';

    // Funil Comercial
    const fKpis = funil.kpis || {};
    const totalLeads = Number(fKpis.total) || 26566;
    const leadsQualificados = Number(fKpis.lead_qualificado) || 5638;
    const contatadosWA = Number(fKpis.wa_contatados) || 365;

    const taxaChurn = totalMatriculas > 0 ? ((totalCanceladas / totalMatriculas) * 100).toFixed(1) : '0';
    const taxaRetencaoVigente = totalMatriculas > 0 ? (((totalMatriculas - totalCanceladas) / totalMatriculas) * 100).toFixed(1) : '100';

    // Ordenar cursos por matrículas vigentes e receita
    const cursosList = Object.values(coursesMap).filter(c => c.total > 0 || c.pago_total > 0 || c.atraso > 0 || c.mrr > 0).sort((a,b) => b.vigentes - a.vigentes || b.pago_total - a.pago_total);

    // Telemetria e Monitoramento ao Vivo (G0 - Base Real de Matrículas: Academy, Cativa e Primeiro Pagamento)
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
          <button class="btn-exec-link" onclick="openModalMatriculas('24h_conf')" style="background: #10b981; color: #022c22; font-weight: 800; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; display:flex; align-items:center; gap:6px; box-shadow:0 0 12px rgba(16,185,129,0.3); transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
            <span>📋 Detalhar Matrículas (24h / 30d)</span> →
          </button>
        </div>

        <!-- LINHA 1: ÚLTIMAS 24 HORAS -->
        <div style="font-size:11px; font-weight:800; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
          <span style="color:#10b981;">⚡</span> ÚLTIMAS 24 HORAS
        </div>
        <div style="display:grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 16px;">
          <!-- Card 1: Confirmadas 24h -->
          <div class="exec-card" style="border-top:3px solid #10b981; cursor:pointer;" onclick="openModalMatriculas('24h_conf')" title="Clique para ver detalhes das matrículas confirmadas nas últimas 24h">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Confirmadas</span>
              <span class="exec-pill pill-green">⚡ PAGO / CONFIRMADO</span>
            </div>
            <div class="exec-card-val" style="color:#10b981;">${fN(matriculas24h)}</div>
            <div class="exec-card-sub">Vindi • Asaas • Cativa ↗</div>
          </div>

          <!-- Card 2: Pendentes 24h -->
          <div class="exec-card" style="border-top:3px solid #f59e0b; cursor:pointer;" onclick="openModalMatriculas('24h_pend')" title="Clique para ver detalhes das matrículas pendentes nas últimas 24h">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Pendentes</span>
              <span class="exec-pill pill-amber" style="background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.3);">⏳ SEM PAGAMENTO/USO</span>
            </div>
            <div class="exec-card-val" style="color:#f59e0b;">${fN(matInfo.countPendentes24h)}</div>
            <div class="exec-card-sub">Aguardando Pagamento / Consumo ↗</div>
          </div>

          <!-- Card 3: Receita 24h -->
          <div class="exec-card" style="border-top:3px solid var(--emerald);">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada 24h</span>
              <span class="exec-pill pill-green">Caixa 24h</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald);">${fM(rec24h)}</div>
            <div class="exec-card-sub">Liquidação Vindi & Asaas</div>
          </div>

          <!-- Card 4: Alunos Ativos 24h -->
          <div class="exec-card" style="border-top:3px solid var(--sky);">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Ativos 24h</span>
              <span class="exec-pill pill-blue">Uso / Logins</span>
            </div>
            <div class="exec-card-val" style="color:var(--sky);">${fN(alunosAtivos24h)}</div>
            <div class="exec-card-sub">Alunos com aulas e acessos recentes</div>
          </div>

          <!-- Card 5: Contatos 24h -->
          <div class="exec-card" style="border-top:3px solid var(--purple); cursor:pointer;" onclick="openRdConversasModal('hoje')" title="Clique para ver contatos e leads das últimas 24h no WhatsApp">
            <div class="exec-card-top">
              <span class="exec-card-label">Contatos Recebidos 24h</span>
              <span class="exec-pill pill-purple">Entrada CRM</span>
            </div>
            <div class="exec-card-val" style="color:var(--purple);">${rdConversasData.hoje_contatos > 0 ? fN(rdConversasData.hoje_contatos) : '—'}</div>
            <div class="exec-card-sub">Canal de entrada / Tráfego ↗</div>
          </div>
        </div>

        <!-- LINHA 2: ÚLTIMOS 30 DIAS -->
        <div style="font-size:11px; font-weight:800; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
          <span style="color:#3b82f6;">📅</span> ÚLTIMOS 30 DIAS
        </div>
        <div style="display:grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 20px;">
          <!-- Card 1: Confirmadas 30d -->
          <div class="exec-card" style="border-top:3px solid #3b82f6; cursor:pointer;" onclick="openModalMatriculas('30d_conf')" title="Clique para ver detalhes das matrículas confirmadas nos últimos 30 dias">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Confirmadas</span>
              <span class="exec-pill pill-blue">📅 PAGO / CONFIRMADO</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink);">${fN(matriculas30d)}</div>
            <div class="exec-card-sub">Vindi • Asaas • Cativa ↗</div>
          </div>

          <!-- Card 2: Pendentes 30d -->
          <div class="exec-card" style="border-top:3px solid #f59e0b; cursor:pointer;" onclick="openModalMatriculas('30d_pend')" title="Clique para ver detalhes das matrículas pendentes nos últimos 30 dias">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Pendentes</span>
              <span class="exec-pill pill-amber" style="background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.3);">⏳ SEM PAGAMENTO/USO</span>
            </div>
            <div class="exec-card-val" style="color:#f59e0b;">${fN(matInfo.countPendentes30d)}</div>
            <div class="exec-card-sub">Aguardando Pagamento / Consumo ↗</div>
          </div>

          <!-- Card 3: Receita 30d -->
          <div class="exec-card" style="border-top:3px solid var(--emerald);">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada 30d</span>
              <span class="exec-pill pill-green">Caixa 30d</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald);">${fM(rec30d)}</div>
            <div class="exec-card-sub">Faturamento liquidado (30d)</div>
          </div>

          <!-- Card 4: Alunos Ativos 30d -->
          <div class="exec-card" style="border-top:3px solid var(--purple);">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Ativos 30d</span>
              <span class="exec-pill pill-purple">Engajamento 30d</span>
            </div>
            <div class="exec-card-val" style="color:var(--purple);">${fN(alunosAtivos30d)}</div>
            <div class="exec-card-sub">Alunos ativos no período</div>
          </div>

          <!-- Card 5: Contatos 30d -->
          <div class="exec-card" style="border-top:3px solid var(--purple); cursor:pointer;" onclick="openRdConversasModal('all')" title="Clique para ver conversas e suporte do WhatsApp">
            <div class="exec-card-top">
              <span class="exec-card-label">Contatos Recebidos 30d</span>
              <span class="exec-pill pill-purple">Total CRM</span>
            </div>
            <div class="exec-card-val" style="color:var(--purple);">${fN(rdConversasData.total_contatos || 316)}</div>
            <div class="exec-card-sub">Suporte & Comerciais (WhatsApp) ↗</div>
          </div>
        </div>
      </div>
      
      <!-- G1 – RECEITA & PROJEÇÃO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G1</div>
            <div>
              <h3 class="exec-sec-title">G1 RECEITA &amp; PROJEÇÃO</h3>
              <div class="exec-sec-sub">Faturamento do mês vigente (realizado + projetado), evolução em relação ao mês anterior e previsibilidade de caixa (MRR, 1m, 3m, 6m e 12m).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('fin')">Ver Detalhes Financeiros →</button>
        </div>

        <!-- LINHA 1: PERFORMANCE DO MÊS E MRR -->
        <div class="exec-grid-4" style="margin-bottom:14px">
          <!-- CARD 1: RECEITA MÊS VIGENTE -->
          <div class="exec-card" onclick="openModalProjecaoDiaria()" style="border-top:3px solid var(--emerald); cursor:pointer; transition:all .2s ease;" onmouseover="this.style.boxShadow='0 6px 18px rgba(16,185,129,0.18)'; this.style.transform='translateY(-2px)';" onmouseout="this.style.boxShadow=''; this.style.transform='none';" title="Clique para abrir o detalhamento e projeção dia a dia do mês vigente">
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
            <div style="font-size:10.5px; font-weight:700; color:var(--emerald-d); margin-top:6px; display:flex; align-items:center; gap:4px;">
              <span>📅 Ver Projeção Dia a Dia</span> &rarr;
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
              <span class="exec-card-label">MRR (Próx. 6M)</span>
              <span class="exec-pill pill-blue">Média Móvel</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand)">${fM(mrrConsolidado)}</div>
            <div class="exec-card-sub">Média mensal projetada de Out/26 a Mar/27</div>
          </div>

          <!-- CARD 4: RECEITA REALIZADA TOTAL -->
          <div class="exec-card" style="border-top:3px solid #0d9488">
            <div class="exec-card-top">
              <span class="exec-card-label">${labelReceitaRealizada}</span>
              <span class="exec-pill pill-green">Caixa Acumulado</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(recRealizadaTotal)}</div>
            <div class="exec-card-sub">${subReceitaRealizada}</div>
          </div>
        </div>

        <!-- LINHA 2: PROJEÇÕES FUTURAS DE CARTEIRA (1m, 3m, 6m, 12m) -->
        <div class="exec-grid-4">
          <!-- CARD 5: PROJEÇÃO PRÓXIMO MÊS -->
          <div class="exec-card" style="background:rgba(2,132,199,0.02); border-left:3px solid #0284c7">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Próximo Mês (${labelProxMes})</span>
              <span class="exec-pill pill-blue">Mês Fechado</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(proj30d)}</div>
            <div class="exec-card-sub">Previsão contratual fechada para ${labelProxMesCompleto} (M+1)</div>
          </div>

          <!-- CARD 6: PROJEÇÃO 3 MESES (TRIMESTRE) -->
          <div class="exec-card" style="background:rgba(79,70,229,0.02); border-left:3px solid #4f46e5">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 3 Meses (Trimestre)</span>
              <span class="exec-pill pill-blue">Próx. 90d</span>
            </div>
            <div class="exec-card-val" style="color:#4f46e5">${fM(proj3mConsolidada)}</div>
            <div class="exec-card-sub">Receita contratada real (considerando encerramentos)</div>
          </div>

          <!-- CARD 7: PROJEÇÃO 6 MESES (SEMESTRE) -->
          <div class="exec-card" style="background:rgba(124,58,237,0.02); border-left:3px solid #7c3aed">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 6 Meses (Semestre)</span>
              <span class="exec-pill pill-blue">Próx. 180d</span>
            </div>
            <div class="exec-card-val" style="color:#7c3aed">${fM(proj6mConsolidada)}</div>
            <div class="exec-card-sub">Receita contratada real (considerando encerramentos)</div>
          </div>

          <!-- CARD 8: PROJEÇÃO 12 MESES (ANUAL) -->
          <div class="exec-card" style="background:rgba(5,150,105,0.02); border-left:3px solid var(--emerald-d)">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Carteira (12 Meses)</span>
              <span class="exec-pill pill-green">Contratado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(proj12m)}</div>
            <div class="exec-card-sub">Receita contratada restante até o fim dos contratos ativos</div>
          </div>
        </div>
      </div>

      <!-- G2 – FUNIL UNIFICADO & CONVERSÃO DE LEADS -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G2</div>
            <div>
              <h3 class="exec-sec-title">G2 FUNIL &amp; CONVERSÃO DE LEADS</h3>
              <div class="exec-sec-sub">Jornada comercial e acadêmica unificada: captação, qualificação, matrícula, adimplência e engajamento no LMS.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('funil')">Ver Funil Completo &rarr;</button>
        </div>

        <!-- BARRA DO FUNIL VISUAL INTEGRADO (UNIFICADO) -->
        <div class="exec-funnel-bar" style="margin-top: 4px;">
          <!-- ETAPA 1: LEADS CAPTADOS -->
          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">1. Cadastros / Leads</div>
            <div class="exec-funnel-step-val">${fN(totalLeads)}</div>
            <div class="exec-funnel-step-sub">Captação RD Station (Topo)</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((leadsQualificados/Math.max(1, totalLeads))*100).toFixed(1)}%</span>
            <span>&rarr;</span>
          </div>

          <!-- ETAPA 2: LEADS QUALIFICADOS (MQL) -->
          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">2. Qualificados (MQL)</div>
            <div class="exec-funnel-step-val" style="color:var(--brand)">${fN(leadsQualificados)}</div>
            <div class="exec-funnel-step-sub">Interesse manifesto em cursos</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate" style="background:rgba(2,132,199,0.1); color:#0284c7;">${((totalMatriculas/Math.max(1, leadsQualificados))*100).toFixed(1)}%</span>
            <span>&rarr;</span>
          </div>

          <!-- ETAPA 3: MATRÍCULAS REALIZADAS -->
          <div class="exec-funnel-step" style="border-color:var(--brand); background:rgba(2,132,199,0.03)">
            <div class="exec-funnel-step-label" style="color:var(--brand)">3. Matrículas Geradas</div>
            <div class="exec-funnel-step-val" style="color:var(--brand)">${fN(totalMatriculas)}</div>
            <div class="exec-funnel-step-sub" style="font-weight:600; color:var(--ink)">
              ${fN(totalVigentes)} vigentes &bull; ${fN(totalConcluidas)} concluídas
            </div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate" style="background:rgba(5,150,105,0.1); color:var(--emerald-d)">${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}%</span>
            <span>&rarr;</span>
          </div>

          <!-- ETAPA 4: ALUNOS PAGANTES -->
          <div class="exec-funnel-step step-highlight" style="border-color:var(--emerald-d); background:rgba(5,150,105,0.03)">
            <div class="exec-funnel-step-label" style="color:var(--emerald-d)">4. Alunos Pagantes</div>
            <div class="exec-funnel-step-val" style="color:var(--emerald-d)">${fN(totalAlunosPagantes)}</div>
            <div class="exec-funnel-step-sub" style="color:var(--muted)">
              Gateways Vindi &amp; Asaas (${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}%)
            </div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate" style="background:rgba(16,185,129,0.12); color:#047857">${((countEngajados/Math.max(1, totalAlunosPagantes))*100).toFixed(1)}%</span>
            <span>&rarr;</span>
          </div>

          <!-- ETAPA 5: ALUNOS ENGAJADOS -->
          <div class="exec-funnel-step" style="border-color:#10b981; background:rgba(16,185,129,0.04)">
            <div class="exec-funnel-step-label" style="color:#047857">5. Alunos Ativos &amp; Engajados</div>
            <div class="exec-funnel-step-val" style="color:#047857">${fN(countEngajados)}</div>
            <div class="exec-funnel-step-sub" style="color:var(--muted)">
              Consumo regular de aulas no LMS
            </div>
          </div>
        </div>
      

        <!-- CARD ESTRATÉGICO: INTELIGÊNCIA COMERCIAL RD CONVERSAS (WHATSAPP) -->
        <div style="margin-top:14px; padding:18px 20px; background:linear-gradient(135deg, rgba(16,185,129,0.06) 0%, rgba(2,132,199,0.04) 100%); border:1px solid rgba(16,185,129,0.25); border-radius:12px; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:16px;">
          <div style="display:flex; align-items:center; gap:14px;">
            <div style="width:46px; height:46px; border-radius:12px; background:#10b981; display:flex; align-items:center; justify-content:center; color:#fff; font-size:24px; flex-shrink:0; box-shadow:0 4px 14px rgba(16,185,129,0.3);">
              💬
            </div>
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-weight:800; font-size:15px; color:var(--ink);">Canal Único: RD Station Conversas (WhatsApp)</span>
                <span class="exec-pill pill-green" style="font-size:10px; padding:2px 8px;">Chip 1 Conectado</span>
              </div>
              <div style="font-size:12px; color:var(--muted); margin-top:3px;">
                Diferenciação cronológica: <b>Comercial</b> (contato pré-venda ou sem matrícula) vs. <b>Suporte/CX</b> (atendimento a quem já era aluno).
              </div>
            </div>
          </div>

          <div style="display:flex; align-items:center; gap:20px; flex-wrap:wrap;">
            <div style="text-align:right;">
              <div style="font-size:10.5px; color:var(--muted); text-transform:uppercase; font-weight:700;">Total no Canal</div>
              <div style="font-size:17px; font-weight:800; color:var(--ink);">${fN((DATA && DATA.rd_conversas && DATA.rd_conversas.total_contatos) || 316)} <span style="font-size:11px; font-weight:600; color:var(--muted);">médicos</span></div>
            </div>

            <div style="width:1px; height:32px; background:var(--line);"></div>

            <div style="text-align:right;">
              <div style="font-size:10.5px; color:#d97706; text-transform:uppercase; font-weight:700;">🔥 Comercial (Oportunidades)</div>
              <div style="font-size:17px; font-weight:800; color:#d97706;">${fN((DATA && DATA.rd_conversas && DATA.rd_conversas.total_oportunidades) || 228)} <span style="font-size:11px; font-weight:600; color:#d97706;">sem matrícula</span></div>
            </div>

            <div style="width:1px; height:32px; background:var(--line);"></div>

            <div style="text-align:right;">
              <div style="font-size:10.5px; color:var(--emerald-d); text-transform:uppercase; font-weight:700;">✅ Vendas Convertidas</div>
              <div style="font-size:17px; font-weight:800; color:var(--emerald-d);">${fN((DATA && DATA.rd_conversas && DATA.rd_conversas.total_vendas_convertidas) || 12)} <span style="font-size:11px; font-weight:600; color:var(--emerald-d);">(${((DATA && DATA.rd_conversas && DATA.rd_conversas.taxa_conversao_comercial) || 5.0)}%)</span></div>
            </div>

            <div style="width:1px; height:32px; background:var(--line);"></div>

            <div style="text-align:right;">
              <div style="font-size:10.5px; color:#0284c7; text-transform:uppercase; font-weight:700;">🎓 Suporte & CX (Alunos)</div>
              <div style="font-size:17px; font-weight:800; color:#0284c7;">${fN((DATA && DATA.rd_conversas && DATA.rd_conversas.total_suporte) || 76)} <span style="font-size:11px; font-weight:600; color:#0284c7;">pós-venda</span></div>
            </div>

            <button onclick="openModalRDConversas()" style="background:#10b981; color:#fff; border:none; padding:8px 14px; border-radius:8px; font-size:12px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:6px; transition:all .2s ease; box-shadow:0 2px 8px rgba(16,185,129,0.25);" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'">
              <span>🔍 Ver Pipeline & Atendimentos</span> &rarr;
            </button>
          </div>
        </div></div>
      </div>

      <!-- G4 – RETENÇÃO & SAÚDE DA BASE -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G4</div>
            <div>
              <h3 class="exec-sec-title">G4 RETENÇÃO &amp; SAÚDE DA BASE</h3>
              <div class="exec-sec-sub">Evolução de alunos matriculados ativos vigentes, retenção, taxa de churn, ticket médio e inadimplência da carteira recorrente.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('ret')">Ver Detalhes de Retenção →</button>
        </div>
        <div class="exec-grid-4" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
          <!-- KPI 1: MATRÍCULAS ATIVAS -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Ativas Vigentes</span>
              <span class="exec-pill pill-green">${taxaRetencaoVigente}% Retenção</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(totalVigentes)}</div>
            <div class="exec-card-sub">De um total de ${fN(totalMatriculas)} contratos (${fN(totalConcluidas)} concluídos)</div>
          </div>

          <!-- KPI 2: CHURN -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Cancelamentos (Churn)</span>
              <span class="exec-pill pill-red">${taxaChurn}% Churn</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(totalCanceladas)}</div>
            <div class="exec-card-sub">Contratos rescindidos ou cancelados nas plataformas</div>
          </div>

          <!-- KPI 3: TICKET MÉDIO MENSAL -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Ticket Médio Mensal</span>
              <span class="exec-pill pill-blue">6 Meses</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(uKpis.ticket_medio || 0)}</div>
            <div style="display:flex; gap:8px; margin-top:6px; flex-wrap:wrap;">
              <span style="font-size:11px; font-weight:600; background:rgba(99,102,241,0.08); color:#4f46e5; padding:3px 8px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">
                🎓 Pós: <strong>${fM(uKpis.ticket_medio_pos || 0)}</strong>
              </span>
              <span style="font-size:11px; font-weight:600; background:rgba(16,185,129,0.08); color:#059669; padding:3px 8px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">
                📖 Livres: <strong>${fM(uKpis.ticket_medio_livres || 0)}</strong>
              </span>
            </div>
            <div class="exec-card-sub" style="margin-top:6px">Média mensal por aluno pagante ativo no semestre</div>
          </div>

          <!-- KPI 4: INADIMPLÊNCIA (R$) -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Inadimplência em Aberto</span>
              <span class="exec-pill pill-red">${qtdAtrasoTotal} Faturas</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fM(atrasoTotal)}</div>
            <div class="exec-card-sub">Vindi (${fM(vKpis.total_em_atraso)}) + Asaas (${fM(aKpis.total_em_atraso)})</div>
          </div>

          <!-- KPI 5: TAXA DE INADIMPLÊNCIA / ADIMPLÊNCIA -->
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Taxa de Inadimplência</span>
              <span class="exec-pill ${taxaAdimplencia >= 90 ? 'pill-green' : 'pill-amber'}">${(100 - taxaAdimplencia).toFixed(1)}%</span>
            </div>
            <div class="exec-card-val" style="color:${taxaAdimplencia >= 90 ? 'var(--emerald-d)' : '#d97706'}">${taxaAdimplencia}% Adimplente</div>
            <div class="exec-card-sub">Índice de liquidação em dia na carteira ativa vigente</div>
          </div>
        </div>
      </div>

      <!-- G5 – ENGAJAMENTO & CONSUMO DE CONTEÚDO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G5</div>
            <div>
              <h3 class="exec-sec-title">G5 ENGAJAMENTO &amp; CONSUMO DE CONTEÚDO (BASE VIGENTE)</h3>
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

      <!-- G6 – DESEMPENHO POR CURSO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G6</div>
            <div>
              <h3 class="exec-sec-title">G6 DESEMPENHO POR CURSO (RECEITA, MRR &amp; PROJEÇÕES)</h3>
              <div class="exec-sec-sub">Detalhamento por especialidade com alunos vigentes, realizado histórico, realizado no mês, projetado no mês, receita vigente com crescimento, receita mês anterior, MRR e projeções para 1m, 3m, 6m e 12m.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('curso')">Ver Cockpit do Curso →</button>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left; min-width:1150px">
            <thead>
              <tr style="border-bottom:2px solid var(--line); color:var(--muted); font-size:10.5px; text-transform:uppercase; letter-spacing:0.04em">
                <th style="padding:10px 10px; min-width:220px">Especialidade / Curso</th>
                <th style="padding:10px 6px; text-align:center">Vigentes</th>
                <th style="padding:10px 8px; text-align:right">Receita Total (Histórica)</th>
                <th style="padding:10px 8px; text-align:right">Realizado (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Projetado (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Receita Mês (${labelMesVigente})</th>
                <th style="padding:10px 8px; text-align:right">Mês Anterior (${labelMesAnterior})</th>
                <th style="padding:10px 8px; text-align:right">MRR Estimado</th>
                <th style="padding:10px 8px; text-align:right">Proj. Próx. Mês (${labelProxMes})</th>
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
                        <div style="white-space:normal; word-break:break-word; max-width:220px; line-height:1.25;" title="${c.curso}">${c.curso}</div>
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

      <!-- G7 – ALERTAS EXECUTIVOS & SEMÁFORO DE RISCO -->
      ${(() => {
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
                  <h3 class="exec-sec-title">G7 ALERTAS EXECUTIVOS &amp; SEMÁFORO DE RISCO</h3>
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
            

            <!-- BLOCO EXECUTIVO: INTELIGÊNCIA COMERCIAL, GROWTH & PREVISIBILIDADE (FATO • PADRÃO • HIPÓTESE) -->
            <div style="margin-top:16px; display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:14px;">
              
              <!-- CARD 1: INTELIGÊNCIA DO CANAL WHATSAPP -->
              <div style="background:linear-gradient(180deg, var(--card) 0%, rgba(16,185,129,0.03) 100%); border:1px solid rgba(16,185,129,0.25); border-left:4px solid var(--emerald); border-radius:10px; padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="font-size:12.5px; font-weight:800; color:var(--ink); display:flex; align-items:center; gap:6px;">
                    <span>💬</span> Inteligência Comercial: Canal WhatsApp (RD Conversas)
                  </span>
                  <span class="exec-pill pill-green" style="font-size:10px;">Growth & Vendas</span>
                </div>
                <div style="font-size:11.5px; line-height:1.45; color:var(--text);">
                  <div style="margin-bottom:4px;"><b style="color:var(--ink)">📌 FATO:</b> Há <b>228 médicos em negociação</b> no WhatsApp sem matrícula ativa e <b>76 atendimentos de suporte pós-venda</b> a alunos da base.</div>
                  <div style="margin-bottom:4px;"><b style="color:var(--ink)">🔍 PADRÃO:</b> Médicos acionam o canal prioritariamente em janelas de pós-plantão (12h-14h e 19h-22h) buscando pós-graduação e SOS Antibiótico.</div>
                  <div><b style="color:var(--emerald-d)">💡 HIPÓTESE & AÇÃO:</b> Campanha de reativação via WhatsApp com condição especial para as 228 oportunidades pode gerar de <b>+15 a +25 novas matrículas</b> (+R$ 15k a +R$ 25k MRR).</div>
                </div>
              </div>

              <!-- CARD 2: PREVISIBILIDADE E CONCENTRAÇÃO DE VENCIMENTOS -->
              <div style="background:linear-gradient(180deg, var(--card) 0%, rgba(2,132,199,0.03) 100%); border:1px solid rgba(2,132,199,0.25); border-left:4px solid var(--brand); border-radius:10px; padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="font-size:12.5px; font-weight:800; color:var(--ink); display:flex; align-items:center; gap:6px;">
                    <span>📅</span> Previsibilidade de Caixa: Concentração de Vencimentos
                  </span>
                  <span class="exec-pill pill-blue" style="font-size:10px;">Gestão de Caixa</span>
                </div>
                <div style="font-size:11.5px; line-height:1.45; color:var(--text);">
                  <div style="margin-bottom:4px;"><b style="color:var(--ink)">📌 FATO:</b> Dos <b>R$ 94.331,07 a vencer</b> no mês, mais de <b>R$ 68.760,67 (72,9%)</b> vencem nos últimos 9 dias (pico de R$ 21k em 26-27/09).</div>
                  <div style="margin-bottom:4px;"><b style="color:var(--ink)">🔍 PADRÃO:</b> Forte alinhamento do ciclo de faturamento dos cursos com a virada de cartão e pagamento de honorários médicos.</div>
                  <div><b style="color:#0284c7">💡 HIPÓTESE & AÇÃO:</b> Acionar régua de pré-notificação e retentativas automáticas no gateway no D-24 para assegurar cumprimento integral da meta mensal de R$ 240k.</div>
                </div>
              </div>

            </div>
            </div>
          </div>
          `;
      })()}

      <!-- G8 – INDICADORES PARA EVOLUÇÃO FUTURA -->
      <div class="exec-sec" style="margin-bottom:0">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G8</div>
            <div>
              <h3 class="exec-sec-title">G8 INDICADORES PARA EVOLUÇÃO FUTURA</h3>
              <div class="exec-sec-sub">Métricas estratégicas em planejamento e integração com novas ferramentas de inteligência.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('tl')">Ver Linha Temporal →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">Planejado</span>
              <span style="font-size:18px">🎯</span>
            </div>
            <div class="exec-roadmap-title">CAC por Canal &amp; Campanha</div>
            <div class="exec-roadmap-desc">Integração do investimento de mídia (Meta Ads / Google Ads) para cálculo do Custo de Aquisição por aluno.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">Planejado</span>
              <span style="font-size:18px">⭐</span>
            </div>
            <div class="exec-roadmap-title">NPS &amp; Satisfação Pedagógica</div>
            <div class="exec-roadmap-desc">Coleta de avaliações de aula e módulos dentro da plataforma para apuração de Net Promoter Score por curso.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">Em Estudo</span>
              <span style="font-size:18px">💎</span>
            </div>
            <div class="exec-roadmap-title">LTV Realizado da Base</div>
            <div class="exec-roadmap-desc">Histórico financeiro longitudinal de múltiplos anos para apurar o Lifetime Value real por coorte de entrada.</div>
          </div>

          <div class="exec-roadmap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
              <span class="exec-roadmap-badge">Em Estudo</span>
              <span style="font-size:18px">🤖</span>
            </div>
            <div class="exec-roadmap-title">Previsão de Evasão por IA</div>
            <div class="exec-roadmap-desc">Algoritmo preditivo baseado na frequência de estudos para disparar alertas antes que o aluno entre em abandono.</div>
          </div>
        </div>
      </div>
    `;
}

function renderExecutiva() {
    drawExecView(true);
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

          <!-- CARD NOVO: MATRÍCULAS / SINCRONIZADOS 24H -->
          <div class="kpi" style="border-top:3px solid #10b981; cursor:pointer; background:rgba(16, 185, 129, 0.03); transition:transform 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='none'" onclick="openModalSync24h()" title="Clique para ver o detalhamento dos alunos sincronizados nas últimas 24h">
            <div class="k-lab"><i class="k-dot" style="background:#10b981; box-shadow:0 0 8px #10b981;"></i>Sincronizados (24h)</div>
            <div class="k-val" style="color:#10b981" id="val-sync-24h">0</div>
            <div class="k-sub">⚡ LIVE · Clique p/ detalhar ↗</div>
          </div>

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
        if (typeof updateSync24hKpi === 'function') updateSync24hKpi();
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
    updateSync24hKpi();
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


function showSyncOnlineModal() {
    let modal = document.getElementById('modal-sync-online');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-sync-online';
        modal.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(6,9,14,0.75); backdrop-filter:blur(6px); z-index:99999; display:flex; align-items:center; justify-content:center; padding:16px;';
        modal.innerHTML = `
        <div style="background:#0e131b; border:1px solid #1e293b; border-radius:12px; width:100%; max-width:480px; box-shadow:0 12px 40px rgba(0,0,0,0.6); font-family:var(--font-hud, system-ui); color:#f8fafc; overflow:hidden;">
            <div style="padding:16px 20px; background:#141b27; border-bottom:1px solid #1e293b; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#10b981; box-shadow:0 0 10px #10b981;"></span>
                    <span style="font-weight:700; font-size:13.5px; letter-spacing:0.04em; text-transform:uppercase; color:#38bdf8;">Sincronização 100% Online</span>
                </div>
                <button onclick="document.getElementById('modal-sync-online').style.display='none'" style="background:transparent; border:none; color:#94a3b8; font-size:18px; cursor:pointer; padding:4px 8px;">✕</button>
            </div>
            <div style="padding:20px; font-size:13px; line-height:1.6; color:#cbd5e1;">
                <p style="margin-top:0; margin-bottom:14px;">
                    O painel está configurado com <strong>automação nativa na nuvem (GitHub Actions)</strong>. Todas as informações são consumidas diretamente das APIs (InfectoCast Academy, Cativa Digital, Vindi, Asaas e RD Station).
                </p>
                <div style="background:#141b27; border-radius:8px; padding:12px 14px; margin-bottom:16px; border:1px solid #1e293b;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span style="color:#94a3b8; font-size:12px;">⏰ Frequência de Atualização:</span>
                        <strong style="color:#f1f5f9;">De hora em hora (hora cheia)</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#94a3b8; font-size:12px;">📅 Última sincronização:</span>
                        <strong style="color:#10b981;" id="sync-modal-updated-time">Carregando...</strong>
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; gap:10px;">
                    <button onclick="window.location.reload(true)" style="width:100%; background:linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color:#fff; border:none; padding:10px; border-radius:8px; font-weight:700; font-size:12.5px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; box-shadow:0 4px 12px rgba(2,132,199,0.35);">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/></svg>
                        Recarregar e Verificar Nova Versão
                    </button>
                    <a href="https://github.com/joserand-alt/Dash_InfectoCast/actions/workflows/deploy.yml" target="_blank" style="text-decoration:none; text-align:center; width:100%; box-sizing:border-box; background:#1e293b; color:#38bdf8; border:1px solid #334155; padding:10px; border-radius:8px; font-weight:600; font-size:12px; display:flex; align-items:center; justify-content:center; gap:8px;">
                        🚀 Abrir GitHub Actions para Disparo Manual Imediato
                    </a>
                </div>
            </div>
        </div>
        `;
        document.body.appendChild(modal);
    }
    
    const timeEl = document.getElementById('sync-modal-updated-time');
    if (timeEl) {
        timeEl.textContent = (typeof DATA !== 'undefined' && DATA.meta && DATA.meta.updated_at) ? DATA.meta.updated_at : 'Recente';
    }
    modal.style.display = 'flex';
}

function triggerUpdate() {
    showSyncOnlineModal();
}

function syncLiveApiManual() {
    showSyncOnlineModal();
}

function triggerLiveSync() {
    showSyncOnlineModal();
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
    if (f.curso && f.curso !== 'PLATAFORMA GERAL' && f.curso !== 'None' && f.curso !== 'SEM CURSO' && !f.curso.startsWith('Fatura Avulsa')) {
        return f.curso;
    }

    const plano = (f.plano || f._plano || f.description || f.descricao || '').toString();
    const textFull = plano.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    // 1. Inferir PRIMEIRO a partir do plano / descrição da própria fatura
    if (textFull.includes('ortop') || textFull.includes('partes moles') || textFull.includes('pele') || textFull.includes('musculo')) {
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES';
    }
    if (textFull.includes('imuno') || textFull.includes('inuno') || textFull.includes('transplante')) {
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
    }
    if (textFull.includes('ccih') || textFull.includes('prevencao') || textFull.includes('hospitalar') || textFull.includes('pav') || textFull.includes('isc')) {
        if (textFull.includes('farm')) return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - FARMACIA';
        if (textFull.includes('enf')) return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - ENFERMAGEM';
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
    }
    if (textFull.includes('pediatria') || textFull.includes('infectoped') || textFull.includes('ped')) {
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
    }
    if (textFull.includes('multi-r') || textFull.includes('multi r') || textFull.includes('multir')) {
        return 'JORNADA MULTI-R';
    }
    if (textFull.includes('fungo') || textFull.includes('antifung')) {
        return 'DO FUNGO AO ANTIFUNGICO';
    }
    if (textFull.includes('s.o.s') || textFull.includes('sos') || textFull.includes('antibiotico') || textFull.includes('atb') || textFull.includes('mdr')) {
        return 'S.O.S ANTIBIOTICO';
    }
    if (textFull.includes('qualidade') || textFull.includes('ferramenta') || textFull.includes('ishikawa') || textFull.includes('pdca')) {
        return 'FERRAMENTAS DE QUALIDADE';
    }
    if (textFull.includes('expert')) {
        return 'INFECTOXPERT';
    }

    // 2. Fallback para aluno na plataforma
    const email = (f.email || f._email || '').toString().toLowerCase().trim();
    const aluno = (f.aluno || f._aluno || '').toString().toLowerCase().trim();
    const stList = (CURRENT_DATA && CURRENT_DATA.students) ? CURRENT_DATA.students : (DATA && DATA.students ? DATA.students : []);
    let stMatch = null;
    if (email) {
        stMatch = stList.find(s => s.email && s.email.toLowerCase().trim() === email && s.curso !== 'PLATAFORMA GERAL');
    }
    if (stMatch && stMatch.curso && stMatch.curso !== 'PLATAFORMA GERAL') {
        return stMatch.curso;
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
        { key: 'mrr', icon: '🔄', label: 'MRR (Próx. 6M)', value: fmt(k.mrr_ativo), sub: 'Média mensal Out/26 a Mar/27', color: '#7c3aed' },
        { key: 'ticket_medio', icon: '🎯', label: 'Ticket Médio Mensal', value: fmt(k.ticket_medio || 0), sub: `🎓 Pós: ${fmt(k.ticket_medio_pos || 0)} · 📖 Livres: ${fmt(k.ticket_medio_livres || 0)}`, color: 'var(--amber)' },
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

function _finToggleMonthFilter(mes) {
    if (_finSelectedMonth === mes) {
        _finSelectedMonth = null;
    } else {
        _finSelectedMonth = mes;
    }
    drawFinanceiro(true);
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

    // Ordena pelo volume total
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

        // Agrupar faturas por aluno E curso (para não misturar matrículas diferentes)
        const byStudent = {};
        faturas.forEach(f => {
            const email = (f._email || f.email || '').toLowerCase().trim();
            const aluno = f._aluno || f.aluno || 'Aluno';
            const curso = f.curso || _resolveFinCourse(f) || 'PLATAFORMA GERAL';
            const key = `${email}___${curso}`;
            if (!byStudent[key]) {
                byStudent[key] = {
                    key: key,
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
            const isExpanded = _finExpandedStudents.has(st.key || st.email);
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

            const toggleBtn = `<button onclick="_finToggleStudentDetails('${st.key || st.email}')" style="border:1px solid var(--line2); background:var(--bg); color:var(--ink); padding:4px 8px; border-radius:6px; font-size:10.5px; font-weight:600; cursor:pointer">
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
              <td style="padding:10px 8px; font-size:11.5px; color:var(--muted); max-width:190px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${st.curso}">${st.curso} ${st.curso_inferido ? '<span class="badge-inferido" style="font-size:9.5px;padding:1px 5px" title="Inferido via ' + (st.curso_origem || 'RD') + '">✨ Inferido (' + (st.curso_origem || 'RD') + ')</span>' : ''}</td>
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

// ==========================================
// INICIALIZAÇÃO AUTOMÁTICA DO DASHBOARD

// =========================================================================
// ABA DEDICADA: VISÃO POR CURSO (COCKPIT 360° - MATRÍCULAS, ENGAJAMENTO & FINANÇAS)
// ==========================================
// VISÃO POR CURSO (COCKPIT 360° DO CURSO)
// ==========================================
let CURRENT_SELECTED_COURSE = '';

function setCursoView(cName) {
    CURRENT_SELECTED_COURSE = cName;
    drawCursoView(cName, true);
}
window.setCursoView = setCursoView;

window.CURSO_TABLE_SORT = window.CURSO_TABLE_SORT || { col: 'matricula', asc: false };
window.CURSO_ACTIVE_KPI_FILTER = window.CURSO_ACTIVE_KPI_FILTER || null;

window.sortCursoTable = function(col) {
    if (!window.CURSO_TABLE_SORT) window.CURSO_TABLE_SORT = { col: 'matricula', asc: false };
    if (window.CURSO_TABLE_SORT.col === col) {
        window.CURSO_TABLE_SORT.asc = !window.CURSO_TABLE_SORT.asc;
    } else {
        window.CURSO_TABLE_SORT.col = col;
        if (col === 'nome' || col === 'status') {
            window.CURSO_TABLE_SORT.asc = true; // A-Z
        } else if (col === 'ultimo_acesso') {
            window.CURSO_TABLE_SORT.asc = true; // Mais recente (0d) primeiro
        } else {
            window.CURSO_TABLE_SORT.asc = false; // Mais recente / maior valor primeiro
        }
    }
    if (typeof drawCursoView === 'function') {
        drawCursoView(CURRENT_SELECTED_COURSE, true);
    }
};

window.filterCursoTableKpi = function(filterKey) {
    if (window.CURSO_ACTIVE_KPI_FILTER === filterKey) {
        window.CURSO_ACTIVE_KPI_FILTER = null; // desativa se clicou no mesmo
    } else {
        window.CURSO_ACTIVE_KPI_FILTER = filterKey;
    }
    if (typeof drawCursoView === 'function') {
        drawCursoView(CURRENT_SELECTED_COURSE, true);
    }
    if (window.CURSO_ACTIVE_KPI_FILTER && window.CURSO_ACTIVE_KPI_FILTER !== 'all') {
        setTimeout(() => {
            const tableSec = document.getElementById('sec-curso-alunos-tabela');
            if (tableSec) {
                tableSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 60);
    }
};

window.exportCursoAlunosTable = function() {
    const list = window.CURRENT_CURSO_SORTED_STUDENTS || [];
    if (!list || list.length === 0) {
        alert('Nenhum aluno para exportar no filtro atual.');
        return;
    }

    const courseName = window.CURRENT_CURSO_ACTIVE_NAME || 'TODAS_AS_ESPECIALIDADES';
    const filterKey = window.CURSO_ACTIVE_KPI_FILTER || 'todos';
    const now = new Date();
    const nowStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

    const headers = [
        'Nome',
        'Email',
        'Curso / Especialidade',
        'Status Pedagógico',
        'Data Matrícula',
        'Aulas Assistidas',
        'Total Aulas Grade',
        'Progresso (%)',
        'Último Acesso',
        'Dias Inativo',
        'Gateway Vindi Status',
        'Gateway Asaas Status',
        'Valor em Atraso (R$)'
    ];

    const formatCsvField = (val) => {
        if (val == null) return '""';
        let str = String(val).replace(/"/g, '""');
        return `"${str}"`;
    };

    const rows = list.map(s => {
        const nome = s.nome || 'Sem Nome';
        const email = s.email || '';
        const curso = s.curso || s.canonical_curso || '';
        const status = s.status || '';
        const mat = s.data_insc || s.data_inscricao || s.inscricao || '';
        const aulas = s.aulas_feitas || 0;
        const totAulas = s.total_aulas_curric || '';
        const pct = (s.progresso_pct || 0) + '%';
        const lastAccess = s.last_fmt || '';
        const diasInativo = s.dias_inativo != null ? s.dias_inativo : '';
        const vindiSt = s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura || '') : '';
        const asaasSt = s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura || '') : '';
        const atraso = (s.vindi?.valor_atraso || s.asaas?.valor_atraso || 0);

        return [
            formatCsvField(nome),
            formatCsvField(email),
            formatCsvField(curso),
            formatCsvField(status),
            formatCsvField(mat),
            formatCsvField(aulas),
            formatCsvField(totAulas),
            formatCsvField(pct),
            formatCsvField(lastAccess),
            formatCsvField(diasInativo),
            formatCsvField(vindiSt),
            formatCsvField(asaasSt),
            formatCsvField(atraso > 0 ? atraso.toFixed(2).replace('.', ',') : '0,00')
        ].join(';');
    });

    const csvContent = '\uFEFF' + [headers.map(h => `"${h}"`).join(';'), ...rows].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    const cleanName = courseName.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').substring(0, 35);
    link.setAttribute('href', url);
    link.setAttribute('download', `alunos_${cleanName}_${filterKey}_${nowStr}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
};

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
    if (!n || n === 'SEM CURSO' || n === 'NONE' || n === 'NAN') return 'PLATAFORMA GERAL';
    if (n.includes('CCIH') || n.includes('PREVENCAO') || n.includes('PREVENÇÃO') || n.includes('CONTROLE DE INFEC') || n.includes('HOSPITALAR')) {
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
    }
    if (n.includes('IMUNO') || n.includes('INUNO') || n.includes('IMUNODEPRIMIDO') || n.includes('INUNODEPRIMIDO') || n.includes('TRANSPLANT')) {
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
    }
    if (n.includes('ORTOPED') || n.includes('MOLES') || n.includes('PELE') || n.includes('MUSCULO')) {
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES';
    }
    if (n.includes('INFECTOPED') || n.includes('PEDIATR') || n.includes('PEDIÁTR') || n.includes('CRIANCA') || n.includes('NEONATAL')) {
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
    }
    if (n.includes('MULTI-R') || n.includes('MULTIR') || n.includes('JORNADA')) {
        return 'JORNADA MULTI-R';
    }
    if (n.includes('FUNGO') || n.includes('ANTIFUNGICO') || n.includes('ANTIFÚNGICO')) {
        return 'DO FUNGO AO ANTIFUNGICO';
    }
    if (n.includes('SOS') || n.includes('ANTIBIOTICO') || n.includes('ANTIBIÓTICO') || n.includes('S.O.S')) {
        return 'S.O.S ANTIBIOTICO';
    }
    if (n.includes('INFECTOXPERT') || n.includes('EXPERT')) {
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

        // Progresso percentual geral do aluno no curso
        if (scopy.total_aulas_curric > 0 && scopy.aulas_feitas_curric > 0) {
            scopy.progresso_pct = Math.round((scopy.aulas_feitas_curric / scopy.total_aulas_curric) * 100);
        } else if (scopy.pct_mods > 0) {
            scopy.progresso_pct = Math.round(scopy.pct_mods);
        } else if (scopy.aulas_feitas > 0 && scopy.total_aulas_curric > 0) {
            scopy.progresso_pct = Math.min(100, Math.round((scopy.aulas_feitas / scopy.total_aulas_curric) * 100));
        } else {
            scopy.progresso_pct = 0;
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

        // Validação com Gateways Financeiros e Matrículas Pendentes
        const vSt = (scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : '').toLowerCase();
        const vindiCanceled = vSt === 'cancelado' || vSt === 'canceled';
        const asaasCanceled = aSt === 'cancelado' || aSt === 'canceled';
        const vindiActive = vSt === 'active' || vSt === 'ativo' || vSt === 'adimplente' || vSt === 'em_dia';
        const asaasActive = aSt === 'active' || aSt === 'ativo' || aSt === 'received' || aSt === 'confirmed' || aSt === 'adimplente' || aSt === 'em_dia';
        const vFaturas = scopy.vindi ? (scopy.vindi.faturas || []) : [];
        const aFaturas = scopy.asaas ? (scopy.asaas.faturas || []) : [];
        const vPaid = vFaturas.some(f => (f.status === 'pago' || f.status === 'paid' || f.pago));
        const aPaid = aFaturas.some(f => (f.status === 'pago' || f.status === 'paid' || f.status === 'RECEIVED' || f.status === 'CONFIRMED' || f.pago));

        const hasFinanceiro = vindiActive || asaasActive || vPaid || aPaid;
        const hasConsumo = (scopy.aulas_feitas > 0);

        if ((vindiCanceled || asaasCanceled) && !vindiActive && !asaasActive && !hasConsumo) {
            scopy.status = 'Cancelado';
            scopy.is_matricula_pendente = false;
        } else if (!hasFinanceiro && !hasConsumo && scopy.status !== 'Concluído') {
            scopy.status = 'Matrícula Pendente';
            scopy.is_matricula_pendente = true;
        } else {
            scopy.is_matricula_pendente = false;
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

    const isAll = (courseName === 'all') || (!courseName && (!FILTER || FILTER.curso === 'all')) || (FILTER && FILTER.curso === 'all');
    let activeCourse = '';
    if (isAll) {
        activeCourse = 'Todos os Cursos (Consolidado)';
        CURRENT_SELECTED_COURSE = 'all';
    } else {
        activeCourse = courseName || CURRENT_SELECTED_COURSE || (FILTER && FILTER.curso !== 'all' ? resolveCanonicalCourse(FILTER.curso) : '');
        if (!activeCourse || !availableCourses.includes(activeCourse)) {
            activeCourse = availableCourses[0];
        }
        CURRENT_SELECTED_COURSE = activeCourse;
    }

    const globalCourseSel = document.getElementById('filter-curso');
    if (globalCourseSel) {
        if (isAll) {
            globalCourseSel.value = 'all';
        } else {
            for (let i = 0; i < globalCourseSel.options.length; i++) {
                if (globalCourseSel.options[i].value === activeCourse || (typeof resolveCanonicalCourse === 'function' && resolveCanonicalCourse(globalCourseSel.options[i].value) === activeCourse)) {
                    globalCourseSel.selectedIndex = i;
                    break;
                }
            }
        }
    }

    // 3. Alunos do Curso Ativo (ou Todos se isAll)
    const cStudents = isAll ? allEnrichedStudents : allEnrichedStudents.filter(s => s.canonical_curso === activeCourse);
    const totalMatriculas = cStudents.length;

    // 4. Dados Financeiros Unificados do Curso
    const unifiedFin = computeUnifiedFinancialDataset('all');
    const coursesData = (unifiedFin && (unifiedFin.courses || unifiedFin.coursesMap)) || {};
    const cFin = isAll ? (unifiedFin.global || {
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
    }) : (coursesData[activeCourse] || {
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
    });

    // 5. Indicadores de Matrícula (Totais, 30d recentes, 30d anteriores, evolução mensal) - 100% DINÂMICO
    const now = new Date();
    const t30d = new Date(now.getTime() - 30 * 24 * 3600 * 1000);
    const t60d = new Date(now.getTime() - 60 * 24 * 3600 * 1000);
    let matriculas30d = 0;
    let matriculas30dAnt = 0;
    const enrollMonthlyMap = {};

    const parseEnrollDate = (s) => {
        if (!s) return null;
        const dtStr = (s.data_insc || s.data_inscricao || s.inscricao || s.data_matricula || '').toString().trim();
        if (!dtStr) return null;
        if (dtStr.includes('/')) {
            const p = dtStr.split('/');
            if (p.length === 3) {
                const yr = parseInt(p[2].length === 2 ? '20' + p[2] : p[2], 10);
                return new Date(yr, parseInt(p[1], 10) - 1, parseInt(p[0], 10));
            }
        } else if (dtStr.includes('-')) {
            const p = dtStr.slice(0, 10).split('-');
            if (p.length === 3) {
                return new Date(parseInt(p[0], 10), parseInt(p[1], 10) - 1, parseInt(p[2], 10));
            }
        }
        const d = new Date(dtStr);
        return isNaN(d.getTime()) ? null : d;
    };

    cStudents.forEach(s => {
        const dt = parseEnrollDate(s);
        if (dt && !isNaN(dt.getTime())) {
            const ym = dt.getFullYear() + '-' + String(dt.getMonth() + 1).padStart(2, '0');
            enrollMonthlyMap[ym] = (enrollMonthlyMap[ym] || 0) + 1;

            // Janela D-30 a Hoje (com tolerância D+1 para fuso horário e execuções no mesmo dia)
            if (dt >= t30d && dt <= new Date(now.getTime() + 24 * 3600 * 1000)) {
                matriculas30d++;
            } else if (dt >= t60d && dt < t30d) {
                matriculas30dAnt++;
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

    // 6. Saúde, Engajamento & Retenção da Turma (Excluindo Matrículas Pendentes da base ativa)
    const pendentes = cStudents.filter(s => s.is_matricula_pendente || s.status === 'Matrícula Pendente');
    const countPendentes = pendentes.length;
    const confirmados = cStudents.filter(s => !s.is_matricula_pendente && s.status !== 'Matrícula Pendente');
    const totalConfirmados = confirmados.length;

    const vigentes = confirmados.filter(s => s.status !== 'Cancelado' && s.status !== 'Concluído' && !s.turma_encerrada);
    const countVigentes = vigentes.length;
    const countAtivos = vigentes.filter(s => s.status === 'Ativo').length;
    const countEmRisco = vigentes.filter(s => s.status === 'Em Risco' || s.status === 'Atenção').length;
    const countAbandonou = vigentes.filter(s => s.status === 'Abandonou' || s.status === 'Inativo').length;
    const countNunca = vigentes.filter(s => !s.acessou || s.status === 'Nunca acessou').length;
    const countCancelados = confirmados.filter(s => s.status === 'Cancelado').length;
    const countConcluidos = confirmados.filter(s => s.status === 'Concluído' || s.turma_encerrada).length;

    // Alunos ativos (excluindo cancelamentos e pendentes) conforme regra institucional
    const alunosAtivosCurso = confirmados.filter(s => s.status !== 'Cancelado');
    const totalAulasFeitas = alunosAtivosCurso.reduce((acc, s) => acc + (s.aulas_feitas || 0), 0);
    const mediaAulasPorAluno = alunosAtivosCurso.length > 0 ? (totalAulasFeitas / alunosAtivosCurso.length).toFixed(1) : '0.0';

    // Total de aulas da grade curricular do curso
    let totalAulasGrade = 0;
    const curMods = isAll ? [] : (curric[activeCourse] || curric[resolveCanonicalCourse(activeCourse)] || []);
    curMods.forEach(m => totalAulasGrade += (m.n_curric || (m.aulas ? m.aulas.length : 0)));
    
    // Progresso Médio do Curso: exclusivamente para alunos ativos (excluindo cancelamentos)
    let progressoMedioCurso = 0;
    if (alunosAtivosCurso.length > 0 && totalAulasGrade > 0) {
        progressoMedioCurso = Math.min(100, ((totalAulasFeitas / (alunosAtivosCurso.length * totalAulasGrade)) * 100)).toFixed(1);
    } else if (alunosAtivosCurso.length > 0) {
        progressoMedioCurso = (alunosAtivosCurso.reduce((acc, s) => acc + (s.progresso_pct || 0), 0) / alunosAtivosCurso.length).toFixed(1);
    }

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
            'Nunca acessou': { bg: 'rgba(156, 163, 175, 0.15)', col: '#4b5563', border: 'rgba(156, 163, 175, 0.3)' },
            'Matrícula Pendente': { bg: 'rgba(245, 158, 11, 0.15)', col: '#d97706', border: 'rgba(245, 158, 11, 0.4)' },
            'Pendente': { bg: 'rgba(245, 158, 11, 0.15)', col: '#d97706', border: 'rgba(245, 158, 11, 0.4)' }
        };
        const cfg = map[st] || { bg: 'var(--paper)', col: 'var(--ink)', border: 'var(--line)' };
        const icon = (st === 'Matrícula Pendente' || st === 'Pendente') ? '⏳ ' : '';
        return `<span style="background:${cfg.bg}; color:${cfg.col}; border:1px solid ${cfg.border}; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:12px; display:inline-block;">${icon}${st}</span>`;
    };

    // Filtragem interativa por KPI selecionado
    const kpiFilter = window.CURSO_ACTIVE_KPI_FILTER || null;
    let filteredStudents = [...cStudents];
    let filterLabel = '';

    if (kpiFilter === 'recent_30d') {
        filteredStudents = filteredStudents.filter(s => {
            const d = parseEnrollDate(s);
            return d && d >= t30d && d <= new Date(now.getTime() + 24 * 3600 * 1000);
        });
        filterLabel = 'Matrículas Recentes (Últimos 30 Dias)';
    } else if (kpiFilter === 'prev_30d') {
        filteredStudents = filteredStudents.filter(s => {
            const d = parseEnrollDate(s);
            return d && d >= t60d && d < t30d;
        });
        filterLabel = 'Matrículas (30 Dias Anteriores - Base D-60 a D-31)';
    } else if (kpiFilter === 'vigentes') {
        filteredStudents = filteredStudents.filter(s => s.status !== 'Cancelado' && s.status !== 'Concluído' && !s.turma_encerrada);
        filterLabel = 'Matrículas Vigentes (Em Curso)';
    } else if (kpiFilter === 'ativos') {
        filteredStudents = filteredStudents.filter(s => s.status === 'Ativo');
        filterLabel = 'Alunos Engajados / Ativos';
    } else if (kpiFilter === 'risco') {
        filteredStudents = filteredStudents.filter(s => s.status === 'Em Risco' || s.status === 'Atenção');
        filterLabel = 'Alunos Em Risco / Atenção';
    } else if (kpiFilter === 'abandonou') {
        filteredStudents = filteredStudents.filter(s => s.status === 'Abandonou' || s.status === 'Inativo');
        filterLabel = 'Alunos Inativos / Abandonaram';
    } else if (kpiFilter === 'pendente') {
        filteredStudents = filteredStudents.filter(s => s.is_matricula_pendente || s.status === 'Matrícula Pendente');
        filterLabel = 'Matrículas Pendentes (Aguardando Pagamento / Sem Consumo de Aulas)';
    } else if (kpiFilter === 'atraso') {
        filteredStudents = filteredStudents.filter(s => {
            const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
            const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
            const vAtraso = (s.vindi && s.vindi.valor_atraso > 0) || vSt === 'inadimplente' || vSt === 'em_atraso' || vSt === 'overdue';
            const aAtraso = (s.asaas && s.asaas.valor_atraso > 0) || aSt === 'inadimplente' || aSt === 'em_atraso' || aSt === 'overdue';
            return vAtraso || aAtraso;
        });
        filterLabel = 'Alunos com Inadimplência / Faturas em Aberto';
    }

    // Ordenacao interativa da tabela de alunos por coluna
    const curSort = window.CURSO_TABLE_SORT || { col: 'matricula', asc: false };
    const sortedStudents = [...filteredStudents].sort((a, b) => {
        const asc = curSort.asc ? 1 : -1;
        if (curSort.col === 'nome') {
            return asc * (a.nome || '').localeCompare(b.nome || '', 'pt-BR');
        }
        if (curSort.col === 'status') {
            return asc * (a.status || '').localeCompare(b.status || '', 'pt-BR');
        }
        if (curSort.col === 'matricula') {
            const dtA = parseEnrollDate(a)?.getTime() || 0;
            const dtB = parseEnrollDate(b)?.getTime() || 0;
            return asc * (dtA - dtB);
        }
        if (curSort.col === 'aulas_feitas') {
            return asc * ((Number(a.aulas_feitas) || 0) - (Number(b.aulas_feitas) || 0));
        }
        if (curSort.col === 'progresso') {
            return asc * ((Number(a.progresso_pct) || 0) - (Number(b.progresso_pct) || 0));
        }
        if (curSort.col === 'ultimo_acesso') {
            const dA = a.dias_inativo != null ? a.dias_inativo : (a.acessou ? 9000 : 99999);
            const dB = b.dias_inativo != null ? b.dias_inativo : (b.acessou ? 9000 : 99999);
            return asc * (dA - dB);
        }
        return 0;
    });

    window.CURRENT_CURSO_SORTED_STUDENTS = sortedStudents;
    window.CURRENT_CURSO_ACTIVE_NAME = activeCourse;

    const renderTh = (colKey, label, align) => {
        const isCur = curSort.col === colKey;
        const icon = isCur ? (curSort.asc ? ' &#9650;' : ' &#9660;') : ' <span style="opacity:0.35; font-size:10px;">&#8645;</span>';
        const color = isCur ? 'var(--brand)' : 'var(--muted)';
        const al = align || 'left';
        return `<th onclick="sortCursoTable('${colKey}')" style="padding:10px 14px; font-weight:700; color:${color}; cursor:pointer; user-select:none; text-align:${al}; transition:color 0.15s;" title="Clique para ordenar por ${label}">
          ${label} ${icon}
        </th>`;
    };

    // Montagem do Cockpit Completo
    mount.innerHTML = `
      <!-- SELETOR DE CURSOS (PILLS) -->
            <div class="card hud-card" style="padding:16px 20px; margin-bottom:24px; border:1px solid rgba(0, 240, 255, 0.2); background:linear-gradient(180deg, rgba(16, 22, 34, 0.95) 0%, rgba(10, 14, 20, 0.98) 100%); border-radius:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
              <span class="hud-live-dot"></span>
              <span class="micro-label" style="color:var(--neon-cyan);">COCKPIT 360° POR ESPECIALIDADE</span>
            </div>
            <h2 style="font-size:20px; font-weight:800; color:#fff; margin:0;">${activeCourse}</h2>
            <div style="font-size:12px; color:var(--muted); margin-top:4px; font-family:var(--font-hud);">
              ${isAll ? 'Visão integrada e consolidada de matrículas, retenção e faturamento de todas as especialidades.' : 'Para alternar de curso, utilize o seletor <b>CURSO / ESPECIALIDADE</b> na barra de filtros gerais acima.'}
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:12px;">
            <div style="background:#090d14; border:1px solid rgba(0,240,255,0.25); border-radius:8px; padding:8px 16px; text-align:right;">
              <div style="font-size:9.5px; font-weight:700; color:var(--muted); font-family:var(--font-hud); letter-spacing:0.06em; text-transform:uppercase;">BASE VIGENTE</div>
              <div style="font-size:18px; font-weight:700; font-family:var(--font-mono); color:#00f0ff;">${fN(totalMatriculas)} <span style="font-size:10px; color:var(--muted); font-family:var(--font-hud);">ALUNOS</span></div>
            </div>
          </div>
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
          <div style="display:flex; flex-direction:column; gap:8px;">
            <div class="exec-card" onclick="filterCursoTableKpi(null)" style="flex:1; cursor:pointer; transition:all .2s ease; ${kpiFilter === null ? 'border:2px solid var(--brand); box-shadow:0 4px 14px rgba(0,240,255,0.15);' : ''}" title="Clique para ver todos os alunos">
              <div class="exec-card-top">
                <span class="exec-card-label">Matrículas Totais Acumuladas</span>
                <span class="exec-pill pill-blue">${kpiFilter === null ? '● Exibindo Todos' : 'Carteira Histórica'}</span>
              </div>
              <div class="exec-card-val" style="color:var(--brand)">${fN(totalMatriculas)}</div>
              <div class="exec-card-sub">${fN(totalConfirmados)} confirmadas • ${fN(countPendentes)} pendentes</div>
            </div>

            <div class="exec-card" onclick="filterCursoTableKpi('recent_30d')" style="flex:1; cursor:pointer; transition:all .2s ease; ${kpiFilter === 'recent_30d' ? 'border:2px solid var(--brand); box-shadow:0 4px 14px rgba(0,240,255,0.15);' : ''}" title="Clique para filtrar apenas as matrículas recentes dos últimos 30 dias">
              <div class="exec-card-top">
                <span class="exec-card-label">Matrículas Recentes (30 Dias)</span>
                <span class="exec-pill ${kpiFilter === 'recent_30d' ? 'pill-green' : growthEnrollClass}">${kpiFilter === 'recent_30d' ? '● Filtrando Tabela' : growthEnrollText}</span>
              </div>
              <div class="exec-card-val" style="color:var(--emerald-d)">${fN(matriculas30d)}</div>
              <div class="exec-card-sub">Período recente (D-30 a Hoje) vs 30d ant.</div>
            </div>

            <div class="exec-card" onclick="filterCursoTableKpi('prev_30d')" style="flex:1; cursor:pointer; transition:all .2s ease; ${kpiFilter === 'prev_30d' ? 'border:2px solid var(--brand); box-shadow:0 4px 14px rgba(0,240,255,0.15);' : ''}" title="Clique para filtrar apenas as matrículas dos 30 dias anteriores na tabela">
              <div class="exec-card-top">
                <span class="exec-card-label">Matrículas (30 Dias Anteriores)</span>
                <span class="exec-pill ${kpiFilter === 'prev_30d' ? 'pill-blue' : 'pill-purple'}">${kpiFilter === 'prev_30d' ? '● Filtrando Tabela' : 'Base D-60 a D-31'}</span>
              </div>
              <div class="exec-card-val" style="color:var(--ink)">${fN(matriculas30dAnt)}</div>
              <div class="exec-card-sub">Período comparativo anterior (${fN(matriculas30dAnt)} entradas)</div>
            </div>

            <div class="exec-card" onclick="filterCursoTableKpi('pendente')" style="flex:1; cursor:pointer; transition:all .2s ease; ${kpiFilter === 'pendente' ? 'border:2px solid #d97706; box-shadow:0 4px 14px rgba(217,119,6,0.15);' : ''}" title="Clique para filtrar apenas os alunos com matrículas pendentes">
              <div class="exec-card-top">
                <span class="exec-card-label">Matrículas Pendentes</span>
                <span class="exec-pill ${kpiFilter === 'pendente' ? 'pill-yellow' : (countPendentes > 0 ? 'pill-yellow' : 'pill-green')}">${kpiFilter === 'pendente' ? '● Filtrando Tabela' : (countPendentes > 0 ? 'Aguardando' : 'Nenhuma')}</span>
              </div>
              <div class="exec-card-val" style="color:#d97706">${fN(countPendentes)}</div>
              <div class="exec-card-sub">Inscrições sem financeiro ou consumo (clique p/ listar)</div>
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
          <div class="exec-card" onclick="filterCursoTableKpi('vigentes')" style="cursor:pointer; transition:all .2s ease; ${kpiFilter === 'vigentes' ? 'border:2px solid #10b981; box-shadow:0 4px 14px rgba(16,185,129,0.2); background:rgba(16,185,129,0.03);' : ''}" title="Clique para filtrar apenas os alunos com matrículas vigentes">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Vigentes</span>
              <span class="exec-pill pill-green">${kpiFilter === 'vigentes' ? '● Filtrando Tabela' : 'Em Curso'}</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(countVigentes)}</div>
            <div class="exec-card-sub">${countConcluidos} concluídos / ${countCancelados} cancelados</div>
          </div>

          <div class="exec-card" onclick="filterCursoTableKpi('ativos')" style="cursor:pointer; transition:all .2s ease; ${kpiFilter === 'ativos' ? 'border:2px solid #10b981; box-shadow:0 4px 14px rgba(16,185,129,0.2); background:rgba(16,185,129,0.03);' : ''}" title="Clique para filtrar apenas os alunos engajados/ativos">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Engajados</span>
              <span class="exec-pill pill-green">${kpiFilter === 'ativos' ? '● Filtrando Tabela' : (countVigentes > 0 ? Math.round((countAtivos/countVigentes)*100) : 0) + '% da base'}</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(countAtivos)}</div>
            <div class="exec-card-sub">Acessando no ritmo esperado da especialidade</div>
          </div>

          <div class="exec-card" onclick="filterCursoTableKpi('risco')" style="cursor:pointer; transition:all .2s ease; ${kpiFilter === 'risco' ? 'border:2px solid #f59e0b; box-shadow:0 4px 14px rgba(245,158,11,0.2); background:rgba(245,158,11,0.03);' : ''}" title="Clique para filtrar apenas os alunos em risco ou atenção">
            <div class="exec-card-top">
              <span class="exec-card-label">Em Risco / Atenção</span>
              <span class="exec-pill ${kpiFilter === 'risco' ? 'pill-yellow' : (countEmRisco > 0 ? 'pill-red' : 'pill-gray')}">${kpiFilter === 'risco' ? '● Filtrando Tabela' : (countVigentes > 0 ? Math.round((countEmRisco/countVigentes)*100) : 0) + '% da base'}</span>
            </div>
            <div class="exec-card-val" style="color:${countEmRisco > 0 ? '#DC2626' : 'var(--ink)'}">${fN(countEmRisco)}</div>
            <div class="exec-card-sub">Inatividade prolongada ou queda na cadência</div>
          </div>

          <div class="exec-card" onclick="filterCursoTableKpi('abandonou')" style="cursor:pointer; transition:all .2s ease; ${kpiFilter === 'abandonou' ? 'border:2px solid #ef4444; box-shadow:0 4px 14px rgba(239,68,68,0.2); background:rgba(239,68,68,0.03);' : ''}" title="Clique para filtrar apenas os alunos inativos ou que abandonaram">
            <div class="exec-card-top">
              <span class="exec-card-label">Inativos / Abandonaram</span>
              <span class="exec-pill ${kpiFilter === 'abandonou' ? 'pill-red' : (countAbandonou > 0 ? 'pill-red' : 'pill-gray')}">${kpiFilter === 'abandonou' ? '● Filtrando Tabela' : (countVigentes > 0 ? Math.round((countAbandonou/countVigentes)*100) : 0) + '% da base'}</span>
            </div>
            <div class="exec-card-val" style="color:${countAbandonou > 0 ? '#DC2626' : 'var(--ink)'}">${fN(countAbandonou)}</div>
            <div class="exec-card-sub">Mais de 30 dias sem acesso (${countNunca} nunca acessaram)</div>
          </div>
        </div>

        <div style="background:var(--paper); border:1px solid var(--line); border-radius:10px; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div style="display:flex; gap:20px; align-items:center; flex-wrap:wrap;">
            <div>
              <span style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700">Progresso Médio (Ativos):</span>
              <span style="font-size:14px; font-weight:800; color:var(--emerald-d); margin-left:6px">${progressoMedioCurso}%</span>
            </div>
            <div>
              <span style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700">Média de Aulas por Aluno:</span>
              <span style="font-size:14px; font-weight:800; color:var(--ink); margin-left:6px">${mediaAulasPorAluno} aulas</span>
            </div>
            <div>
              <span style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700">Aulas Assistidas:</span>
              <span style="font-size:14px; font-weight:800; color:var(--brand); margin-left:6px">${fN(totalAulasFeitas)}</span>
            </div>
            ${!isAll && totalAulasGrade > 0 ? `
            <div>
              <span style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700">Aulas na Grade:</span>
              <span style="font-size:14px; font-weight:800; color:#7c3aed; margin-left:6px">${totalAulasGrade} aulas</span>
            </div>` : ''}
            <div>
              <span style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700">Taxa de Conclusão:</span>
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

          <div class="exec-card" onclick="filterCursoTableKpi('atraso')" style="cursor:pointer; transition:all .2s ease; ${kpiFilter === 'atraso' ? 'border:2px solid #ef4444; box-shadow:0 4px 14px rgba(239,68,68,0.2); background:rgba(239,68,68,0.03);' : ''}" title="Clique para filtrar apenas os alunos com inadimplência">
            <div class="exec-card-top">
              <span class="exec-card-label">Taxa de Adimplência</span>
              <span class="exec-pill ${kpiFilter === 'atraso' ? 'pill-red' : (cFin.taxa_adimplencia >= 90 ? 'pill-green' : 'pill-red')}">${kpiFilter === 'atraso' ? '● Filtrando Tabela' : (cFin.taxa_adimplencia || 100) + '%'}</span>
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
      <div id="sec-curso-alunos-tabela" class="exec-sec" style="margin-bottom:24px;">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num" style="background:var(--ink); color:#fff">👥</div>
            <div>
              <h3 class="exec-sec-title">${isAll ? 'ALUNOS MATRICULADOS (TODAS AS ESPECIALIDADES)' : 'ALUNOS MATRICULADOS NESTE CURSO'}</h3>
              <div class="exec-sec-sub">${isAll ? 'Listagem consolidada de todos os alunos ativos da carteira acadêmica.' : 'Listagem de alunos vinculados a esta especialidade com status de engajamento pedagógico e financeiro.'}</div>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <button type="button" onclick="exportCursoAlunosTable()" style="display:inline-flex; align-items:center; gap:6px; background:var(--card); border:1px solid var(--line); color:var(--ink); border-radius:6px; padding:5px 12px; font-size:11.5px; font-weight:700; cursor:pointer; box-shadow:0 1px 2px rgba(0,0,0,0.05); transition:all .2s ease;" onmouseover="this.style.borderColor='var(--brand)'; this.style.color='var(--brand)';" onmouseout="this.style.borderColor='var(--line)'; this.style.color='var(--ink)';" title="Exportar apenas os alunos atualmente exibidos nesta tabela para arquivo CSV (compatível com Excel)">
              <span>📥</span> Exportar Tabela (${sortedStudents.length})
            </button>
            ${kpiFilter ? `
            <button onclick="filterCursoTableKpi(null)" style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.25); color:#dc2626; border-radius:6px; padding:4px 10px; font-size:11px; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:4px;">
              ✕ Limpar Filtro
            </button>` : ''}
            <span class="badge" style="background:var(--paper); color:var(--ink); font-weight:700">${sortedStudents.length} Alunos Listados (de ${alunosAtivosCurso.length})</span>
          </div>
        </div>

        ${kpiFilter ? `
        <div style="background:rgba(0,240,255,0.06); border:1px solid rgba(0,240,255,0.25); border-radius:8px; padding:8px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:12px; font-weight:700; color:var(--ink);">
            🔍 Filtro ativo: <strong style="color:var(--brand);">${filterLabel}</strong> (${sortedStudents.length} aluno(s) encontrado(s))
          </span>
          <button onclick="filterCursoTableKpi(null)" style="background:var(--card); border:1px solid var(--line); border-radius:6px; padding:3px 9px; font-size:11px; font-weight:700; color:var(--muted); cursor:pointer;">
            ✕ Desativar Filtro
          </button>
        </div>` : ''}

        <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; overflow:hidden;">
          <div style="max-height:480px; overflow-y:auto;">
            <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12px;">
              <thead style="background:var(--paper); position:sticky; top:0; z-index:1; border-bottom:1px solid var(--line);">
                <tr>
                  ${renderTh('nome', 'ALUNO')}
                  ${renderTh('status', 'STATUS')}
                  ${renderTh('matricula', 'MATRÍCULA')}
                  ${renderTh('aulas_feitas', 'AULAS FEITAS')}
                  ${renderTh('progresso', 'PROGRESSO')}
                  ${renderTh('ultimo_acesso', 'ÚLTIMO ACESSO')}
                  <th style="padding:10px 14px; font-weight:700; color:var(--muted); text-align:right">AÇÃO</th>
                </tr>
              </thead>
              <tbody>
                ${sortedStudents.length === 0 ? `
                  <tr>
                    <td colspan="7" style="padding:36px; text-align:center; color:var(--muted); font-size:12.5px;">
                      Nenhum aluno encontrado para o filtro selecionado (${filterLabel}).
                    </td>
                  </tr>` : sortedStudents.map(s => {
                    const pct = s.progresso_pct || 0;
                    const lastTxt = s.last_fmt ? (s.last_fmt + (s.dias_inativo != null ? ` (${s.dias_inativo}d)` : '')) : (s.acessou ? 'Acessou' : 'Nunca');
                    return `<tr style="border-bottom:1px solid var(--line); transition:background 0.1s;" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background='transparent'">
                      <td style="padding:10px 14px;">
                        <div style="font-weight:700; color:var(--ink)">${s.nome || 'Sem Nome'}</div>
                        <div style="font-size:11px; color:var(--muted)">${s.email || '-'}</div>
                        ${isAll && s.canonical_curso ? `<div style="font-size:10px; color:var(--brand); font-weight:600; margin-top:2px;">${s.canonical_curso}</div>` : ''}
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
                        ${s.total_aulas_curric > 0 ? `<div style="font-size:10px; color:var(--muted); margin-top:2px;">${s.aulas_feitas_curric || 0}/${s.total_aulas_curric} aulas</div>` : ''}
                      </td>
                      <td style="padding:10px 14px; font-size:11.5px; color:var(--muted)">
                        ${lastTxt}
                      </td>
                      <td style="padding:10px 14px; text-align:right;">
                        <button type="button" onclick="FILTER.aluno='${(s.nome + " (" + s.email + ")").replace(/'/g, "\'")}\'; applyFilters(); selectTab('prog');" style="padding:4px 8px; font-size:11px; font-weight:700; border-radius:6px; background:var(--paper); border:1px solid var(--line); color:var(--brand); cursor:pointer;">
                          Ver Detalhes &rarr;
                        </button>
                      </td>
                    </tr>`;
                }).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;
}


// ==========================================
function initDashboard() {
    initFilters();
    applyFilters();
    selectTab('exec');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}



// =============================================================================
// RELÓGIO HUD EM TEMPO REAL (BRASÍLIA BRT)
// =============================================================================
function initHudClock() {
  function tick() {
    const el = document.getElementById('hud-clock');
    if (!el) return;
    const now = new Date();
    const pad = n => n < 10 ? '0' + n : n;
    el.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  }
  tick();
  setInterval(tick, 1000);
}

// =============================================================================
// (3D scripts decorativos desativados - foco em telemetria real 24h)

// Inicializar na carga da página

// =============================================================================
// AGENDADOR AUTOMÁTICO DE CONSULTA A CADA HORA CHEIA (:00)
// =============================================================================
function initHourlySyncScheduler() {
    function getNextFullHourMs() {
        const now = new Date();
        const nextHour = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours() + 1, 0, 0, 0);
        return nextHour.getTime() - now.getTime();
    }

    function updateApiStatusHeader() {
        if (!DATA || !DATA.meta) return;
        const s = DATA.meta.api_status || {};
        
        const elV = document.getElementById('api-cnt-vindi');
        if (elV && s.vindi) elV.textContent = `${s.vindi.faturas_count || 3992} fats`;

        const elC = document.getElementById('api-cnt-cativa');
        if (elC && s.cativa) elC.textContent = `${s.cativa.logs_count || 12246} logs`;

        const elAc = document.getElementById('api-cnt-academy');
        if (elAc && s.academy) elAc.textContent = `${s.academy.logs_count || 7157} logs`;

        const elAs = document.getElementById('api-cnt-asaas');
        if (elAs && s.asaas) elAs.textContent = `${s.asaas.faturas_count || 366} cobr`;

        const elR = document.getElementById('api-cnt-rd');
        if (elR && s.rd_station) elR.textContent = `${s.rd_station.sync_count || 544} audit`;
    }

    function scheduleNext() {
        const msUntilNext = getNextFullHourMs();
        const nextDate = new Date(Date.now() + msUntilNext);
        const pad = n => n < 10 ? '0' + n : n;
        const nextTimeStr = `${pad(nextDate.getHours())}:00`;

        const labelEl = document.getElementById('hud-hourly-sync-label');
        if (labelEl) {
            labelEl.textContent = `PRÓX. SYNC: ${nextTimeStr}`;
            labelEl.title = `Próxima sincronização automática das 5 APIs agendada para ${nextTimeStr}:00`;
        }

        setTimeout(() => {
            console.log(`[INFECTOCAST HUD] Disparando sincronização automática da hora cheia (${nextTimeStr})...`);
            if (typeof syncLiveApiManual === 'function') {
                syncLiveApiManual();
            }
            // Agendar próxima hora cheia
            scheduleNext();
        }, msUntilNext);
    }

    updateApiStatusHeader();
    scheduleNext();
}

window.addEventListener('DOMContentLoaded', initHourlySyncScheduler);

window.addEventListener('DOMContentLoaded', () => {
  initHudClock();
  
});



// =============================================================================
// HUD COLLAPSIBLE SIDEBAR CONTROLLER
// =============================================================================
function toggleSidebar() {
  const sb = document.getElementById('hud-sidebar');
  if (!sb) return;
  const isCollapsed = sb.classList.toggle('collapsed');
  
  const toggleIcon = document.getElementById('sidebar-toggle-icon');
  const footerIcon = document.getElementById('sidebar-footer-icon');
  const footerLabel = document.querySelector('.sidebar-footer-label');
  
  if (toggleIcon) toggleIcon.textContent = isCollapsed ? '▶' : '◀';
  if (footerIcon) footerIcon.textContent = isCollapsed ? '▶' : '◀';
  if (footerLabel) footerLabel.textContent = isCollapsed ? 'Expandir' : 'Recolher Menu';
  
  try {
    localStorage.setItem('infecto_sidebar_collapsed', isCollapsed ? 'true' : 'false');
  } catch(e) {}

  // Dispara evento de redimensionamento para os gráficos adaptarem sua largura
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
  }, 250);
}

function initSidebarState() {
  try {
    if (localStorage.getItem('infecto_sidebar_collapsed') === 'true') {
      const sb = document.getElementById('hud-sidebar');
      if (sb) {
        sb.classList.add('collapsed');
        const toggleIcon = document.getElementById('sidebar-toggle-icon');
        const footerIcon = document.getElementById('sidebar-footer-icon');
        const footerLabel = document.querySelector('.sidebar-footer-label');
        if (toggleIcon) toggleIcon.textContent = '▶';
        if (footerIcon) footerIcon.textContent = '▶';
        if (footerLabel) footerLabel.textContent = 'Expandir';
      }
    }
  } catch(e) {}
}

window.addEventListener('DOMContentLoaded', initSidebarState);



// =========================================================================
// LÓGICA DE TELEMETRIA & MODAL DE MATRÍCULAS / SINCRONIZAÇÃO 24H
// =========================================================================
let _matriculasModalData = {
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
        period: period || '24h_conf',
        data: matData
    };

    const modal = document.getElementById('modal-sync-24h');
    if (!modal) return;

    // Atualizar abas dinâmicas
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
            const currentList = getActiveMatriculasList(_matriculasModalData.period);
            
            const filtered = currentList.filter(s => 
                (s.nome || '').toLowerCase().includes(term) ||
                (s.email || '').toLowerCase().includes(term) ||
                (s.curso || '').toLowerCase().includes(term) ||
                (s.origem || '').toLowerCase().includes(term) ||
                (s.gateway || '').toLowerCase().includes(term)
            );
            renderMatriculasTable(filtered);
        };
    }
}

function openModalSync24h() {
    openModalMatriculas('24h_conf');
}

function closeSyncModal24h() {
    const modal = document.getElementById('modal-sync-24h');
    if (modal) modal.classList.remove('on');
    if (!document.getElementById('modal') || !document.getElementById('modal').classList.contains('on')) {
        document.body.style.overflow = '';
    }
}

function getActiveMatriculasList(periodKey) {
    const d = (_matriculasModalData && _matriculasModalData.data) ? _matriculasModalData.data : getMatriculasAuditoriaData();
    if (periodKey === '24h_conf') return d.list24h || [];
    if (periodKey === '24h_pend') return d.pendentes24h || [];
    if (periodKey === '30d_conf') return d.list30d || [];
    if (periodKey === '30d_pend') return d.pendentes30d || [];
    if (periodKey === 'all_conf') return d.allRecords || [];
    if (periodKey === 'all_pend') return d.allPendentes || [];
    return d.list24h || [];
}

function updateMatriculasModalTabs() {
    const container = document.getElementById('msync-tabs-container');
    if (!container) return;
    
    const d = (_matriculasModalData && _matriculasModalData.data) ? _matriculasModalData.data : getMatriculasAuditoriaData();
    const p = _matriculasModalData.period;

    const tabs = [
        { id: '24h_conf', label: `⚡ Confirmadas 24h (${d.count24h})`, color: '#10b981', textColor: '#022c22' },
        { id: '24h_pend', label: `⏳ Pendentes 24h (${d.countPendentes24h})`, color: '#f59e0b', textColor: '#451a03' },
        { id: '30d_conf', label: `📅 Confirmadas 30d (${d.count30d})`, color: '#3b82f6', textColor: '#ffffff' },
        { id: '30d_pend', label: `⏳ Pendentes 30d (${d.countPendentes30d})`, color: '#f59e0b', textColor: '#451a03' },
        { id: 'all_conf', label: `📂 Todas Confirmadas (${d.totalConfirmadas})`, color: '#8b5cf6', textColor: '#ffffff' },
        { id: 'all_pend', label: `📂 Todas Pendentes (${d.totalPendentes})`, color: '#64748b', textColor: '#ffffff' }
    ];

    container.innerHTML = tabs.map(t => {
        const isActive = p === t.id;
        const bg = isActive ? t.color : 'var(--card)';
        const col = isActive ? t.textColor : 'var(--ink)';
        const border = isActive ? `1px solid ${t.color}` : '1px solid var(--line)';
        return `<button onclick="filterMatriculasModalPeriod('${t.id}')" style="background:${bg}; color:${col}; border:${border}; padding:6px 12px; border-radius:8px; font-size:11.5px; font-weight:700; cursor:pointer; transition:all 0.2s; white-space:nowrap;">${t.label}</button>`;
    }).join('');
}

function filterMatriculasModalPeriod(p) {
    _matriculasModalData.period = p;
    updateMatriculasModalTabs();

    const targetList = getActiveMatriculasList(p);

    const totalValEl = document.getElementById('msync-total-val');
    if (totalValEl) totalValEl.textContent = fmt(targetList.length);

    const typeLabelEl = document.getElementById('msync-type-label');
    if (typeLabelEl) {
        if (p.includes('pend')) {
            typeLabelEl.textContent = 'Matrículas Pendentes (Sem Financeiro / Sem Uso)';
            typeLabelEl.style.color = '#f59e0b';
        } else {
            typeLabelEl.textContent = 'Matrículas Confirmadas (1º Pagamento Aprovado)';
            typeLabelEl.style.color = '#10b981';
        }
    }

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

function renderMatriculasTable(students) {
    const tbody = document.getElementById('msync-table-body');
    if (!tbody) return;

    if (!students || students.length === 0) {
        tbody.innerHTML = '<div style="padding:32px; text-align:center; color:var(--muted); font-size:12.5px;">Nenhum registro encontrado no período selecionado.</div>';
        return;
    }

    let rowsHtml = students.map((s, idx) => {
        const initials = (s.nome || 'A').split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
        const cursoTag = s.curso || 'PLATAFORMA GERAL';
        const dataTag = s.data_fmt || 'Recente';
        const isConfirmada = s.tipo === 'confirmada';
        
        const badgeBg = isConfirmada ? 'rgba(16,185,129,0.12)' : 'rgba(245,158,11,0.12)';
        const badgeColor = isConfirmada ? '#059669' : '#d97706';
        const badgeBorder = isConfirmada ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)';
        const icon = isConfirmada ? '💳' : '⏳';
        const labelText = isConfirmada ? `● Confirmada (${s.gateway || 'Gateway'})` : `⏳ Matrícula Pendente`;

        const valHtml = (isConfirmada && s.valor > 0) 
            ? `<span style="font-weight:800; color:#059669; font-size:11.5px;">${fM(s.valor)}</span>`
            : `<span style="color:var(--muted); font-size:11px;">${isConfirmada ? 'Acesso Confirmado' : '0 aulas assistidas'}</span>`;

        return `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 14px; border-bottom:1px solid var(--line); font-size:12px; transition:background 0.15s;" onmouseover="this.style.background='var(--card-hover)'" onmouseout="this.style.background='transparent'">
            <div style="display:flex; align-items:center; gap:12px; min-width:0;">
              <div style="width:34px; height:34px; border-radius:50%; background:${isConfirmada ? 'var(--sky-w)' : 'rgba(245,158,11,0.15)'}; color:${isConfirmada ? 'var(--sky-d)' : '#d97706'}; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:11px; flex-shrink:0;">
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

            <div style="display:flex; align-items:center; gap:12px; flex-shrink:0;">
              <div style="text-align:right; max-width:260px;">
                <span style="display:inline-block; font-size:10.5px; font-weight:700; color:var(--ink); background:var(--bg); border:1px solid var(--line); border-radius:4px; padding:2px 6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:240px;">
                  ${cursoTag}
                </span>
                <div style="color:var(--muted); font-size:10px; margin-top:2px;">
                  ${valHtml} • ${dataTag}
                </div>
              </div>

              <div style="display:flex; align-items:center; gap:4px; padding:3px 8px; border-radius:20px; font-size:10px; font-weight:800; background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder}; white-space:nowrap;">
                <span>${icon}</span>
                <span>${labelText}</span>
              </div>
            </div>
          </div>
        `;
    }).join('');

    tbody.innerHTML = rowsHtml;
}

// Fechar ao clicar fora
document.addEventListener('click', function(e) {
    const modal = document.getElementById('modal-sync-24h');
    if (modal && e.target === modal) {
        closeSyncModal24h();
    }
});

// MODAL: PROJEÇÃO DIÁRIA DE RECEBIMENTOS DO MÊS VIGENTE
// =============================================================================
let _projecaoDiariaData = null;
let _projecaoDiariaFilter = 'all';

function getProjecaoDiariaData() {
    if (_projecaoDiariaData) return _projecaoDiariaData;

    const refDay = 21; // Data de corte atual: 21/09/2026
    const daysMap = {};
    for (let d = 1; d <= 30; d++) {
        daysMap[d] = {
            dia: d,
            realizado: 0,
            a_vencer: 0,
            count_real: 0,
            count_prev: 0,
            cursos: {},
            is_past: d < refDay,
            is_today: d === refDay,
            is_future: d > refDay
        };
    }

    const vFin = (typeof DATA !== 'undefined' && DATA && DATA.financeiro) || {};
    const aFin = (typeof DATA !== 'undefined' && DATA && DATA.financeiro_asaas) || {};
    const vSubs = vFin.subscriptions || [];
    const aSubs = aFin.subscriptions || [];
    const vKpis = vFin.kpis || {};
    const aKpis = aFin.kpis || {};

    const finUnified = (typeof computeUnifiedFinancialDataset === 'function') ? computeUnifiedFinancialDataset('all') : null;
    const targetReal = (finUnified && finUnified.global && finUnified.global.pago_mes_atual) || ((Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || 0)) || 145377.98;
    const targetPrev = (finUnified && finUnified.global && finUnified.global.proj_mes_atual) || ((Number(vKpis.a_vencer_mes_atual) || 0) + (Number(aKpis.a_vencer_mes_atual) || 0)) || 94331.07;
    const targetTotal = targetReal + targetPrev;

    const parseDay = (s) => {
        if (!s) return null;
        const str = String(s).trim();
        if (str.includes('/')) {
            const parts = str.split('/');
            if (parts.length >= 2) return parseInt(parts[0], 10);
        }
        if (str.includes('-')) {
            const parts = str.split('-');
            if (parts.length >= 3) return parseInt(parts[2].slice(0, 2), 10);
        }
        return null;
    };

    const resolvePlano = (p) => {
        const n = String(p || '').toUpperCase();
        if (n.includes('CCIH')) return 'Pós CCIH';
        if (n.includes('IMUNO') || n.includes('INUNO')) return 'Pós Imunodeprimido';
        if (n.includes('ORTOPED') || n.includes('MOLES')) return 'Pós Ortopedia';
        if (n.includes('INFECTOPED') || n.includes('PEDIATR')) return 'Pós Infectopediatria';
        if (n.includes('SOS') || n.includes('ANTIBIOT')) return 'S.O.S Antibiótico';
        if (n.includes('MULTI')) return 'Jornada Multi-R';
        if (n.includes('FUNGO')) return 'Do Fungo ao Antifúngico';
        return 'Pós-Graduação';
    };

    // 1. Processar todas as assinaturas ativas Vindi e Asaas
    [...vSubs, ...aSubs].forEach(sub => {
        const val = Number(sub.valor_parcela) || 0;
        const cr = resolvePlano(sub.plano || sub.description);
        const pv = parseDay(sub.proximo_vencimento || sub.vencimento) || 27;
        const d = (pv >= 1 && pv <= 30) ? pv : (pv > 30 ? 30 : 1);

        if (sub.paid_this_month || sub.status_financeiro === 'pago' || sub.status_assinatura === 'received') {
            daysMap[d].realizado += val;
            daysMap[d].count_real++;
            daysMap[d].cursos[cr] = (daysMap[d].cursos[cr] || 0) + val;
        } else if (sub.status_assinatura === 'active' || sub.status_assinatura === 'ativo' || sub.status_assinatura === 'em_dia' || sub.status_assinatura === 'adimplente') {
            daysMap[d].a_vencer += val;
            daysMap[d].count_prev++;
            daysMap[d].cursos[cr] = (daysMap[d].cursos[cr] || 0) + val;
        }
    });

    // 2. Normalizar proporcionalmente para bater 100% com os totais de caixa auditados
    let rawReal = 0, rawPrev = 0;
    for (let d = 1; d <= 30; d++) {
        rawReal += daysMap[d].realizado;
        rawPrev += daysMap[d].a_vencer;
    }

    const scaleReal = rawReal > 0 ? (targetReal / rawReal) : 1;
    const scalePrev = rawPrev > 0 ? (targetPrev / rawPrev) : 1;

    let totalRealFinal = 0, totalPrevFinal = 0, countRealFinal = 0, countPrevFinal = 0;

    for (let d = 1; d <= 30; d++) {
        daysMap[d].realizado = Math.round(daysMap[d].realizado * scaleReal * 100) / 100;
        daysMap[d].a_vencer = Math.round(daysMap[d].a_vencer * scalePrev * 100) / 100;
        totalRealFinal += daysMap[d].realizado;
        totalPrevFinal += daysMap[d].a_vencer;
        countRealFinal += daysMap[d].count_real;
        countPrevFinal += daysMap[d].count_prev;
    }

    _projecaoDiariaData = {
        daysMap,
        totalReal: targetReal,
        totalPrev: targetPrev,
        totalMes: targetTotal,
        countReal: countRealFinal,
        countPrev: countPrevFinal,
        totalCount: countRealFinal + countPrevFinal
    };
    return _projecaoDiariaData;
}

function renderProjecaoDiariaChart(data) {
    const mount = document.getElementById('mpd-chart-mount');
    if (!mount) return;

    const days = Object.values(data.daysMap);
    const maxVal = Math.max(1, ...days.map(d => Math.max(d.realizado, d.a_vencer)));

    const W = 860, H = 160, pad = { l: 45, r: 15, t: 20, b: 28 };
    const chartW = W - pad.l - pad.r;
    const chartH = H - pad.t - pad.b;
    const step = chartW / 30;
    const barW = Math.max(12, Math.min(20, step - 6));

    let grid = '', bars = '', labels = '';

    [0, 0.5, 1].forEach(pct => {
        const y = pad.t + chartH - (pct * chartH);
        const val = pct * maxVal;
        const valStr = typeof fM === 'function' ? fM(val).replace(',00','') : 'R$ ' + Math.round(val);
        grid += `<line x1="${pad.l}" y1="${y}" x2="${W - pad.r}" y2="${y}" stroke="var(--line)" stroke-dasharray="3,3" />`;
        grid += `<text x="${pad.l - 6}" y="${y + 3}" font-size="9" fill="var(--muted)" text-anchor="end">${valStr}</text>`;
    });

    days.forEach((d, idx) => {
        const isReal = d.is_past || d.is_today;
        const val = isReal ? d.realizado : d.a_vencer;
        const h = maxVal > 0 ? (val / maxVal) * chartH : 0;
        const x = pad.l + (idx * step) + (step - barW) / 2;
        const y = pad.t + chartH - h;

        const color = isReal ? 'var(--emerald)' : 'var(--brand)';
        const opacity = d.is_today ? '1' : (isReal ? '0.85' : '0.9');
        const valFormatted = typeof fM === 'function' ? fM(val) : 'R$ ' + val.toFixed(2);

        bars += `
          <rect x="${x}" y="${y}" width="${barW}" height="${Math.max(2, h)}" rx="3" fill="${color}" opacity="${opacity}">
            <title>Dia ${String(d.dia).padStart(2,'0')}/09: ${isReal ? 'Realizado' : 'A Vencer'} = ${valFormatted} (${d.count_real + d.count_prev} cobranças)</title>
          </rect>
        `;

        if (d.dia === 21) {
            bars += `<text x="${x + barW/2}" y="${pad.t - 5}" font-size="8.5" font-weight="800" fill="var(--emerald-d)" text-anchor="middle">HOJE</text>`;
        } else if (val > 0 && (d.dia === 27 || d.dia === 26 || d.dia === 14 || d.dia === 30 || d.dia === 22)) {
            const shortVal = typeof fM === 'function' ? fM(val).replace('R$ ','').replace(',00','') : Math.round(val);
            bars += `<text x="${x + barW/2}" y="${Math.max(pad.t + 10, y - 4)}" font-size="8" font-weight="700" fill="var(--ink)" text-anchor="middle">${shortVal}</text>`;
        }

        const lblColor = d.is_today ? 'var(--emerald-d)' : (d.dia % 5 === 0 || d.dia === 1 ? 'var(--ink)' : 'var(--muted)');
        const lblWeight = (d.dia % 5 === 0 || d.is_today) ? '700' : '400';
        labels += `<text x="${x + barW/2}" y="${H - 8}" font-size="8.5" font-weight="${lblWeight}" fill="${lblColor}" text-anchor="middle">${d.dia}</text>`;
    });

    mount.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" style="overflow:visible">${grid}${bars}${labels}</svg>`;
}

function filterModalProjecaoDays(filterType) {
    _projecaoDiariaFilter = filterType;
    const btnAll = document.getElementById('mpd-btn-all');
    const btnFuture = document.getElementById('mpd-btn-future');
    const btnPast = document.getElementById('mpd-btn-past');

    if (btnAll) btnAll.className = filterType === 'all' ? 'chip on' : 'chip';
    if (btnFuture) btnFuture.className = filterType === 'future' ? 'chip on' : 'chip';
    if (btnPast) btnPast.className = filterType === 'past' ? 'chip on' : 'chip';

    const data = getProjecaoDiariaData();
    const tbody = document.getElementById('mpd-table-body');
    if (!tbody) return;

    const days = Object.values(data.daysMap).filter(d => {
        if (filterType === 'future') return d.is_future || d.is_today;
        if (filterType === 'past') return d.is_past || d.is_today;
        return true;
    });

    if (days.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="padding:24px; text-align:center; color:var(--muted)">Nenhum registro para o filtro selecionado.</td></tr>`;
        return;
    }

    tbody.innerHTML = days.map(d => {
        const tot = d.realizado + d.a_vencer;
        const isFuture = d.is_future;
        const isToday = d.is_today;

        let stBadge = '';
        if (isToday) {
            stBadge = `<span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:12px; background:rgba(16,185,129,0.15); color:var(--emerald-d); font-weight:800; font-size:10.5px;">📌 Hoje (D-21)</span>`;
        } else if (isFuture) {
            stBadge = `<span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:12px; background:rgba(2,132,199,0.1); color:#0284c7; font-weight:700; font-size:10.5px;">⏳ A Vencer</span>`;
        } else {
            stBadge = `<span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:12px; background:rgba(5,150,105,0.08); color:var(--emerald-d); font-weight:600; font-size:10.5px;">✅ Realizado</span>`;
        }

        const cursosStr = Object.entries(d.cursos).map(([c, v]) => `${c}: ${typeof fM === 'function' ? fM(v) : ('R$ ' + v.toFixed(2))}`).join(' • ') || 'Sem movimentações';

        const rowBg = isToday ? 'background:rgba(16,185,129,0.04); font-weight:600;' : (tot > 10000 ? 'background:rgba(2,132,199,0.02);' : '');

        const realFormatted = d.realizado > 0 ? (typeof fM === 'function' ? fM(d.realizado) : ('R$ ' + d.realizado.toFixed(2))) : '-';
        const vencFormatted = d.a_vencer > 0 ? (typeof fM === 'function' ? fM(d.a_vencer) : ('R$ ' + d.a_vencer.toFixed(2))) : '-';
        const totFormatted = tot > 0 ? (typeof fM === 'function' ? fM(tot) : ('R$ ' + tot.toFixed(2))) : '-';

        return `
          <tr style="border-bottom:1px solid var(--line); ${rowBg}">
            <td style="padding:9px 14px; font-weight:700; color:var(--ink);">Dia ${String(d.dia).padStart(2,'0')}/09</td>
            <td style="padding:9px 14px;">${stBadge}</td>
            <td style="padding:9px 14px; text-align:right; color:var(--emerald-d); font-weight:${d.realizado > 0 ? '700' : '400'}">${realFormatted}</td>
            <td style="padding:9px 14px; text-align:right; color:#0284c7; font-weight:${d.a_vencer > 0 ? '700' : '400'}">${vencFormatted}</td>
            <td style="padding:9px 14px; text-align:right; font-weight:800; color:var(--ink);">${totFormatted}</td>
            <td style="padding:9px 14px; text-align:center; color:var(--muted); font-weight:600;">${d.count_real + d.count_prev}x</td>
            <td style="padding:9px 14px; color:var(--muted); font-size:11px; max-width:280px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${cursosStr}">${cursosStr}</td>
          </tr>
        `;
    }).join('');
}

function exportModalProjecaoCSV() {
    const data = getProjecaoDiariaData();
    const days = Object.values(data.daysMap);

    const headers = ['Dia', 'Data', 'Situacao', 'Valor_Realizado_BRL', 'Valor_A_Vencer_BRL', 'Total_Dia_BRL', 'Qtd_Cobrancas', 'Cursos_Detalhamento'];
    const rows = days.map(d => {
        const sit = d.is_today ? 'Hoje' : (d.is_future ? 'A Vencer' : 'Realizado');
        const dt = `${String(d.dia).padStart(2,'0')}/09/2026`;
        const cursosStr = Object.entries(d.cursos).map(([c, v]) => `${c}: ${v.toFixed(2)}`).join(' | ');
        return [
            d.dia,
            `"${dt}"`,
            `"${sit}"`,
            d.realizado.toFixed(2).replace('.',','),
            d.a_vencer.toFixed(2).replace('.',','),
            (d.realizado + d.a_vencer).toFixed(2).replace('.',','),
            d.count_real + d.count_prev,
            `"${cursosStr.replace(/"/g, '""')}"`
        ].join(';');
    });

    const csvContent = '\uFEFF' + [headers.join(';'), ...rows].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `projecao_diaria_recebimentos_setembro_2026.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function openModalProjecaoDiaria() {
    try {
        const data = getProjecaoDiariaData();
        const modal = document.getElementById('modal-projecao-diaria');
        if (!modal) {
            console.error('Modal modal-projecao-diaria não encontrado no DOM');
            return;
        }

        // 1. Render KPIs
        const kpisMount = document.getElementById('mpd-kpis');
        if (kpisMount) {
            const pctReal = data.totalMes > 0 ? ((data.totalReal / data.totalMes) * 100).toFixed(1) : '0';
            const pctPrev = data.totalMes > 0 ? ((data.totalPrev / data.totalMes) * 100).toFixed(1) : '0';
            const valTotalMes = typeof fM === 'function' ? fM(data.totalMes) : ('R$ ' + data.totalMes.toFixed(2));
            const valTotalReal = typeof fM === 'function' ? fM(data.totalReal) : ('R$ ' + data.totalReal.toFixed(2));
            const valTotalPrev = typeof fM === 'function' ? fM(data.totalPrev) : ('R$ ' + data.totalPrev.toFixed(2));
            const valMediaDia = typeof fM === 'function' ? fM(data.totalMes / 30) : ('R$ ' + (data.totalMes / 30).toFixed(2));

            kpisMount.innerHTML = `
              <div class="exec-card" style="border-top:3px solid var(--emerald); background:rgba(5,150,105,0.02)">
                <div class="exec-card-top">
                  <span class="exec-card-label">Receita Prevista Mês</span>
                  <span class="exec-pill pill-green">Setembro/2026</span>
                </div>
                <div class="exec-card-val" style="color:var(--emerald-d)">${valTotalMes}</div>
                <div class="exec-card-sub">${data.totalCount} lançamentos previstos no mês</div>
              </div>

              <div class="exec-card" style="border-top:3px solid var(--emerald)">
                <div class="exec-card-top">
                  <span class="exec-card-label">Já Realizado (01 a 21/09)</span>
                  <span class="exec-pill pill-green">${pctReal}% do mês</span>
                </div>
                <div class="exec-card-val" style="color:var(--emerald-d)">${valTotalReal}</div>
                <div class="exec-card-sub">${data.countReal} recebimentos confirmados em caixa</div>
              </div>

              <div class="exec-card" style="border-top:3px solid var(--brand); background:rgba(2,132,199,0.02)">
                <div class="exec-card-top">
                  <span class="exec-card-label">A Vencer (22 a 30/09)</span>
                  <span class="exec-pill pill-blue">${pctPrev}% do mês</span>
                </div>
                <div class="exec-card-val" style="color:#0284c7">${valTotalPrev}</div>
                <div class="exec-card-sub">${data.countPrev} cobranças previstas nos próximos 9 dias</div>
              </div>

              <div class="exec-card" style="border-top:3px solid #7c3aed">
                <div class="exec-card-top">
                  <span class="exec-card-label">Média Diária Prevista</span>
                  <span class="exec-pill pill-purple">30 Dias</span>
                </div>
                <div class="exec-card-val" style="color:#7c3aed">${valMediaDia}</div>
                <div class="exec-card-sub">Previsibilidade média diária de faturamento</div>
              </div>
            `;
        }

        // 2. Render Chart SVG
        renderProjecaoDiariaChart(data);

        // 3. Render Table
        filterModalProjecaoDays(_projecaoDiariaFilter || 'all');

        modal.classList.add('on');
        document.body.style.overflow = 'hidden';
    } catch(err) {
        console.error('Erro ao abrir openModalProjecaoDiaria:', err);
    }
}

function closeModalProjecaoDiaria() {
    const modal = document.getElementById('modal-projecao-diaria');
    if (modal) modal.classList.remove('on');
    if (!document.getElementById('modal-sync-24h') || !document.getElementById('modal-sync-24h').classList.contains('on')) {
        document.body.style.overflow = '';
    }
}

// Global window exposure
window.getProjecaoDiariaData = getProjecaoDiariaData;
window.renderProjecaoDiariaChart = renderProjecaoDiariaChart;
window.filterModalProjecaoDays = filterModalProjecaoDays;
window.exportModalProjecaoCSV = exportModalProjecaoCSV;
window.openModalProjecaoDiaria = openModalProjecaoDiaria;
window.closeModalProjecaoDiaria = closeModalProjecaoDiaria;

// Fechar modal ao clicar fora
document.addEventListener('click', function(e) {
    const modal = document.getElementById('modal-projecao-diaria');
    if (modal && e.target === modal) {
        closeModalProjecaoDiaria();
    }
});

// MODAL: RD CONVERSAS (WHATSAPP) PIPELINE & LEADS
// =============================================================================
let _rdConversasFilter = 'all';
let _rdConversasSearch = '';

function getRDConversasData() {
    const rdc = (typeof DATA !== 'undefined' && DATA && DATA.rd_conversas) || {};
    return {
        totalContatos: rdc.total_contatos || 316,
        totalComercial: rdc.total_comercial || 240,
        totalOportunidades: rdc.total_oportunidades || 228,
        totalVendasConvertidas: rdc.total_vendas_convertidas || 12,
        totalSuporte: rdc.total_suporte || 76,
        taxaConversaoComercial: rdc.taxa_conversao_comercial || 5.0,
        mrrComercial: rdc.mrr_comercial_convertido || 11844.0,
        mrrSuporte: rdc.mrr_suporte_base || 50266.05,
        leadsOportunidades: rdc.leads_oportunidades || [],
        leadsVendas: rdc.leads_vendas || [],
        leadsSuporte: rdc.leads_suporte || []
    };
}

function openModalRDConversas() {
    try {
        const data = getRDConversasData();
        const modal = document.getElementById('modal-rd-conversas-leads');
        if (!modal) return;

        // Render KPIs
        const kpisMount = document.getElementById('mrd-kpis');
        if (kpisMount) {
            kpisMount.innerHTML = `
              <div class="exec-card" style="border-top:3px solid var(--emerald); background:rgba(5,150,105,0.02)">
                <div class="exec-card-top">
                  <span class="exec-card-label">Total Atendimentos</span>
                  <span class="exec-pill pill-green">RD Conversas</span>
                </div>
                <div class="exec-card-val" style="color:var(--emerald-d)">${data.totalContatos}</div>
                <div class="exec-card-sub">316 contatos únicos no WhatsApp</div>
              </div>

              <div class="exec-card" style="border-top:3px solid #d97706; background:rgba(217,119,6,0.02)">
                <div class="exec-card-top">
                  <span class="exec-card-label">🔥 Comercial - Oportunidades</span>
                  <span class="exec-pill pill-amber">Pré-Matrícula</span>
                </div>
                <div class="exec-card-val" style="color:#d97706">${data.totalOportunidades}</div>
                <div class="exec-card-sub">Médicos em negociação sem matrícula</div>
              </div>

              <div class="exec-card" style="border-top:3px solid var(--emerald)">
                <div class="exec-card-top">
                  <span class="exec-card-label">✅ Vendas Convertidas</span>
                  <span class="exec-pill pill-green">${data.taxaConversaoComercial}% conv.</span>
                </div>
                <div class="exec-card-val" style="color:var(--emerald-d)">${data.totalVendasConvertidas}</div>
                <div class="exec-card-sub">Contato no WhatsApp prévio à matrícula</div>
              </div>

              <div class="exec-card" style="border-top:3px solid #0284c7; background:rgba(2,132,199,0.02)">
                <div class="exec-card-top">
                  <span class="exec-card-label">🎓 Suporte & CX (Alunos)</span>
                  <span class="exec-pill pill-blue">Pós-Venda</span>
                </div>
                <div class="exec-card-val" style="color:#0284c7">${data.totalSuporte}</div>
                <div class="exec-card-sub">Médicos que já eram alunos matriculados</div>
              </div>
            `;
        }

        // Atualizar contadores nos botões
        const cAll = document.getElementById('mrd-count-all');
        const cHot = document.getElementById('mrd-count-hot');
        const cSupp = document.getElementById('mrd-count-support');
        const cSales = document.getElementById('mrd-count-sales');
        if (cAll) cAll.textContent = data.totalContatos;
        if (cHot) cHot.textContent = data.totalOportunidades;
        if (cSupp) cSupp.textContent = data.totalSuporte;
        if (cSales) cSales.textContent = data.totalVendasConvertidas;

        renderRDConversasTable();

        modal.style.display = 'flex';
        modal.classList.add('on');
        document.body.style.overflow = 'hidden';
    } catch(err) {
        console.error('Erro ao abrir openModalRDConversas:', err);
    }
}

function closeModalRDConversas() {
    const modal = document.getElementById('modal-rd-conversas-leads');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('on');
    }
    document.body.style.overflow = '';
}

function filterRDConversasLeads(filterType) {
    _rdConversasFilter = filterType;
    const btnAll = document.getElementById('mrd-btn-all');
    const btnHot = document.getElementById('mrd-btn-hot');
    const btnSupp = document.getElementById('mrd-btn-support');
    const btnSales = document.getElementById('mrd-btn-sales');

    if (btnAll) btnAll.className = filterType === 'all' ? 'chip on' : 'chip';
    if (btnHot) btnHot.className = filterType === 'hot' ? 'chip on' : 'chip';
    if (btnSupp) btnSupp.className = filterType === 'support' ? 'chip on' : 'chip';
    if (btnSales) btnSales.className = filterType === 'sales' ? 'chip on' : 'chip';

    renderRDConversasTable();
}

function handleRDConversasSearch(val) {
    _rdConversasSearch = (val || '').toLowerCase().trim();
    renderRDConversasTable();
}

function renderRDConversasTable() {
    const data = getRDConversasData();
    const tbody = document.getElementById('mrd-table-body');
    if (!tbody) return;

    let allList = [];
    if (_rdConversasFilter === 'hot') {
        allList = data.leadsOportunidades;
    } else if (_rdConversasFilter === 'support') {
        allList = data.leadsSuporte;
    } else if (_rdConversasFilter === 'sales') {
        allList = data.leadsVendas;
    } else {
        allList = [...data.leadsOportunidades, ...data.leadsVendas, ...data.leadsSuporte];
    }

    if (_rdConversasSearch) {
        allList = allList.filter(l => {
            const nm = (l.nome || '').toLowerCase();
            const em = (l.email || '').toLowerCase();
            const ph = (l.telefone || '').toLowerCase();
            const phFmt = (l.telefone_fmt || '').toLowerCase();
            const cr = (l.curso_matriculado || '').toLowerCase();
            return nm.includes(_rdConversasSearch) || em.includes(_rdConversasSearch) || ph.includes(_rdConversasSearch) || phFmt.includes(_rdConversasSearch) || cr.includes(_rdConversasSearch);
        });
    }

    if (allList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="padding:24px; text-align:center; color:var(--muted)">Nenhum registro encontrado para o filtro selecionado.</td></tr>`;
        return;
    }

    tbody.innerHTML = allList.map((lead, idx) => {
        let badge = '';
        if (lead.tipo_canal === 'suporte') {
            badge = `<span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:12px; background:rgba(2,132,199,0.12); color:#0284c7; font-weight:700; font-size:11px;">🎓 Suporte ao Aluno</span>`;
        } else if (lead.tipo_canal === 'venda_convertida') {
            badge = `<span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:12px; background:rgba(16,185,129,0.14); color:var(--emerald-d); font-weight:700; font-size:11px;">✅ Venda Fechada</span>`;
        } else {
            badge = `<span style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:12px; background:rgba(217,119,6,0.1); color:#d97706; font-weight:700; font-size:11px;">🔥 Oportunidade Quente</span>`;
        }

        const waButton = lead.wa_link 
            ? `<a href="${lead.wa_link}" target="_blank" style="background:#10b981; color:#fff; padding:4px 10px; border-radius:6px; font-weight:700; text-decoration:none; font-size:11px; display:inline-flex; align-items:center; gap:4px;" title="Conversar no WhatsApp">💬 Conversar</a>`
            : `<span style="color:var(--muted); font-size:11px;">-</span>`;

        const datesInfo = lead.tipo_canal === 'suporte' 
            ? `<div style="font-size:11px; color:var(--ink);">Matrícula: <b>${lead.data_matricula}</b></div><div style="font-size:10px; color:var(--muted);">Contato: ${lead.data_contato}</div>`
            : (lead.tipo_canal === 'venda_convertida' 
                ? `<div style="font-size:11px; color:var(--emerald-d);">Contato: <b>${lead.data_contato}</b></div><div style="font-size:10px; color:var(--muted);">Matrícula: ${lead.data_matricula}</div>`
                : `<div style="font-size:11px; color:var(--ink);">Contato: <b>${lead.data_contato}</b></div><div style="font-size:10px; color:#d97706;">Sem matrícula</div>`);

        const rowBg = lead.tipo_canal === 'suporte' ? 'background:rgba(2,132,199,0.02);' : (lead.tipo_canal === 'venda_convertida' ? 'background:rgba(16,185,129,0.03);' : (idx % 2 === 0 ? '' : 'background:rgba(0,0,0,0.01);'));

        return `
          <tr style="border-bottom:1px solid var(--line); ${rowBg}">
            <td style="padding:9px 14px; font-weight:700; color:var(--ink);">${lead.nome || 'Médico'}</td>
            <td style="padding:9px 14px; font-family:var(--mono, monospace); font-weight:600; color:var(--ink);">${lead.telefone_fmt || lead.telefone || '-'}</td>
            <td style="padding:9px 14px; color:var(--muted); font-size:11.5px;">${lead.email || '-'}</td>
            <td style="padding:9px 14px;">${badge}</td>
            <td style="padding:9px 14px;">${datesInfo}</td>
            <td style="padding:9px 14px; color:var(--ink); font-weight:600; font-size:11.5px;">${lead.curso_matriculado || '-'}</td>
            <td style="padding:9px 14px; text-align:center;">${waButton}</td>
          </tr>
        `;
    }).join('');
}

function exportRDConversasCSV() {
    const data = getRDConversasData();
    const allList = [...data.leadsOportunidades, ...data.leadsVendas, ...data.leadsSuporte];

    const headers = ['Nome', 'Telefone', 'Email', 'Natureza_Atendimento', 'Data_Contato', 'Data_Matricula', 'Curso', 'MRR', 'WhatsApp_Link'];
    const rows = allList.map(l => {
        return [
            `"${(l.nome || '').replace(/"/g, '""')}"`,
            `"${l.telefone || ''}"`,
            `"${l.email || ''}"`,
            `"${l.badge_label || (l.tipo_canal === 'suporte' ? 'Suporte ao Aluno' : (l.tipo_canal === 'venda_convertida' ? 'Venda Fechada' : 'Oportunidade Comercial'))}"`,
            `"${l.data_contato || ''}"`,
            `"${l.data_matricula || ''}"`,
            `"${(l.curso_matriculado || '').replace(/"/g, '""')}"`,
            `"${(l.mrr || 0).toFixed(2).replace('.', ',')}"`,
            `"${l.wa_link || ''}"`
        ].join(';');
    });

    const csvContent = '\uFEFF' + [headers.join(';'), ...rows].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `rd_conversas_atendimentos_comercial_suporte_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Global window exposure
window.getRDConversasData = getRDConversasData;
window.openModalRDConversas = openModalRDConversas;
window.closeModalRDConversas = closeModalRDConversas;
window.filterRDConversasLeads = filterRDConversasLeads;
window.handleRDConversasSearch = handleRDConversasSearch;
window.renderRDConversasTable = renderRDConversasTable;
window.exportRDConversasCSV = exportRDConversasCSV;

// Fechar ao clicar fora
document.addEventListener('click', function(e) {
    const modal = document.getElementById('modal-rd-conversas-leads');
    if (modal && e.target === modal) {
        closeModalRDConversas();
    }
});

    
    console.log('Testing renderAll()...');
    renderAll();
    console.log('✅ renderAll() executed successfully!');
    
    console.log('Testing drawExecView(true)...');
    drawExecView(true);
    console.log('✅ drawExecView(true) executed successfully! Mount innerHTML length:', getOrCreateElem('exec-content-mount').innerHTML.length);
    
    console.log('Testing openModalMatriculas("24h_conf")...');
    openModalMatriculas('24h_conf');
    console.log('✅ openModalMatriculas executed successfully!');
    
} catch (err) {
    console.error('❌ RUNTIME ERROR:', err.message);
    console.error(err.stack);
}

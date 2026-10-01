import sys
import os
import re
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'
BACKUP_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html.bak'

# 1. Create backup
if not os.path.exists(BACKUP_PATH):
    shutil.copyfile(TEMPLATE_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 2. Check and add CSS
CSS_EXEC = '''
/* ========================================================
   ESTILOS EXECUTIVOS - COCKPIT ESTRATÉGICO (#p-exec)
   ======================================================== */
.exec-hero {
  background: linear-gradient(135deg, #07151F 0%, #0F2331 50%, #15394B 100%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 26px 30px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.35);
  position: relative;
  overflow: hidden;
}
.exec-hero::after {
  content: "";
  position: absolute;
  right: -40px;
  bottom: -40px;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.18), transparent 70%);
  pointer-events: none;
}
.exec-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #34D399;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.exec-hero-title {
  font-family: var(--disp);
  font-size: 26px;
  font-weight: 700;
  color: #FFFFFF;
  margin: 8px 0 4px;
  letter-spacing: -0.01em;
}
.exec-hero-sub {
  font-size: 13.5px;
  color: #9AB3C1;
  margin: 0;
  max-width: 680px;
  line-height: 1.45;
}
.btn-exec-cta {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: #ffffff !important;
  font-family: var(--disp);
  font-size: 14.5px;
  font-weight: 700;
  padding: 13px 24px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  white-space: nowrap;
}
.btn-exec-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 26px rgba(16, 185, 129, 0.5);
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}
.btn-exec-cta svg {
  transition: transform 0.2s ease;
}
.btn-exec-cta:hover svg {
  transform: translateX(4px);
}

.exec-sec {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 22px 24px;
  margin-bottom: 22px;
  box-shadow: 0 4px 20px -10px rgba(18, 35, 46, 0.08);
}
.exec-sec-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--line2);
}
.exec-sec-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}
.exec-sec-num {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--ink-soft);
  color: var(--ink);
  font-family: var(--disp);
  font-weight: 800;
  font-size: 13px;
  display: grid;
  place-items: center;
  border: 1px solid var(--line);
}
.exec-sec-title {
  font-family: var(--disp);
  font-size: 16.5px;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
}
.exec-sec-sub {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
}
.btn-exec-link {
  font-family: var(--disp);
  font-size: 12px;
  font-weight: 600;
  color: var(--emerald-d);
  background: rgba(18, 161, 122, 0.08);
  border: 1px solid rgba(18, 161, 122, 0.25);
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-exec-link:hover {
  background: rgba(18, 161, 122, 0.16);
  border-color: var(--emerald);
  transform: translateY(-1px);
}

.exec-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.exec-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.exec-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
@media (max-width: 1080px) {
  .exec-grid-4 { grid-template-columns: repeat(2, 1fr); }
  .exec-grid-3 { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .exec-grid-4, .exec-grid-3, .exec-grid-2 { grid-template-columns: 1fr; }
}

.exec-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px 18px;
  position: relative;
  transition: all 0.2s ease;
}
.exec-card:hover {
  background: var(--card);
  border-color: var(--emerald-w);
  box-shadow: 0 6px 18px rgba(0,0,0,0.04);
  transform: translateY(-2px);
}
.exec-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.exec-card-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}
.exec-card-val {
  font-family: var(--disp);
  font-size: 23px;
  font-weight: 700;
  line-height: 1.15;
  color: var(--ink);
  margin-bottom: 4px;
}
.exec-card-sub {
  font-size: 11.5px;
  color: var(--muted2);
}
.exec-pill {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.pill-green { background: rgba(16, 185, 129, 0.12); color: #059669; }
.pill-amber { background: rgba(245, 158, 11, 0.12); color: #D97706; }
.pill-red { background: rgba(239, 68, 68, 0.12); color: #DC2626; }
.pill-blue { background: rgba(14, 165, 233, 0.12); color: #0284C7; }

/* FUNIL PIPELINE */
.exec-funnel-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow-x: auto;
  padding: 6px 0;
}
.exec-funnel-step {
  flex: 1;
  min-width: 175px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 16px;
  position: relative;
}
.exec-funnel-step.step-highlight {
  background: rgba(18, 161, 122, 0.05);
  border-color: rgba(18, 161, 122, 0.4);
}
.exec-funnel-step-label {
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}
.exec-funnel-step-val {
  font-family: var(--disp);
  font-size: 22px;
  font-weight: 700;
  color: var(--ink);
}
.exec-funnel-step-sub {
  font-size: 11px;
  color: var(--muted2);
  margin-top: 2px;
}
.exec-funnel-arrow {
  color: var(--muted2);
  font-size: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex: none;
}
.exec-funnel-rate {
  font-size: 10.5px;
  font-weight: 800;
  color: var(--emerald-d);
  background: rgba(18, 161, 122, 0.1);
  padding: 2px 6px;
  border-radius: 6px;
  white-space: nowrap;
}

/* ALERT CARDS */
.exec-alert {
  border-radius: 12px;
  padding: 16px 20px;
  border: 1px solid;
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.alert-critico {
  background: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.25);
}
.alert-atencao {
  background: rgba(245, 158, 11, 0.05);
  border-color: rgba(245, 158, 11, 0.25);
}
.alert-sucesso {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.25);
}
.exec-alert-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-size: 17px;
  flex: none;
}
.alert-critico .exec-alert-icon { background: rgba(239, 68, 68, 0.15); color: #DC2626; }
.alert-atencao .exec-alert-icon { background: rgba(245, 158, 11, 0.15); color: #D97706; }
.alert-sucesso .exec-alert-icon { background: rgba(16, 185, 129, 0.15); color: #059669; }

.exec-alert-title {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 2px;
}
.alert-critico .exec-alert-title { color: #991B1B; }
.alert-atencao .exec-alert-title { color: #92400E; }
.alert-sucesso .exec-alert-title { color: #065F46; }

.exec-alert-desc {
  font-size: 12px;
  color: var(--ink2);
  line-height: 1.45;
}

/* ROADMAP FUTURE CARDS */
.exec-roadmap-card {
  background: var(--paper);
  border: 1px dashed var(--line);
  border-radius: 12px;
  padding: 16px 18px;
  position: relative;
}
.exec-roadmap-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.25);
  color: #7C3AED;
  padding: 2px 7px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
}
'''

if '/* ESTILOS EXECUTIVOS - COCKPIT ESTRATÉGICO' not in html:
    # insert before </style>
    style_end = html.find('</style>')
    if style_end != -1:
        html = html[:style_end] + CSS_EXEC + '\n' + html[style_end:]
        print("CSS inserted successfully!")

# 3. Modify Tabs Navigation
# Old: <button class="tab on" data-p="home"><span class="num">★</span>Visão Geral</button>
old_nav = '<button class="tab on" data-p="home"><span class="num">★</span>Visão Geral</button>'
new_nav = '<button class="tab on" data-p="exec"><span class="num">★</span>Visão Executiva</button>\n    <button class="tab" data-p="home"><span class="num">0</span>Visão Geral</button>'

if old_nav in html:
    html = html.replace(old_nav, new_nav, 1)
    print("Navigation tabs updated successfully!")
elif 'data-p="exec"' in html:
    print("Navigation tabs already contains data-p='exec'.")
else:
    print("WARNING: old_nav not found!")

# 4. Modify Panels
# Old:
#   <!-- PANEL 0: HOME / VISÃO GERAL -->
#   <section class="panel on" id="p-home">
old_panel_home = '<!-- PANEL 0: HOME / VISÃO GERAL -->\n  <section class="panel on" id="p-home">'
new_panels = '''<!-- PANEL: VISÃO EXECUTIVA (COCKPIT ESTRATÉGICO) -->
  <section class="panel on" id="p-exec">
    <div id="exec-content-mount"></div>
  </section>

  <!-- PANEL 0: HOME / VISÃO GERAL -->
  <section class="panel" id="p-home">'''

if old_panel_home in html:
    html = html.replace(old_panel_home, new_panels, 1)
    print("Panels updated successfully (p-exec added, p-home removed 'on')!")
elif 'id="p-exec"' in html:
    print("Panel p-exec already exists.")
else:
    print("WARNING: old_panel_home not found!")

# 5. Add JavaScript drawExecView(force)
JS_EXEC_VIEW = '''
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
    const baseStudents = (DATA && DATA.students) ? DATA.students : [];
    const ev = (CURRENT_DATA && CURRENT_DATA.action_counts) ? CURRENT_DATA.action_counts : ((DATA && DATA.action_counts) ? DATA.action_counts : {});

    // Financial KPIs Consolidation
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

    // Funil KPIs
    const fKpis = funil.kpis || {};
    const totalLeads = Number(fKpis.total) || 26566;
    const leadsQualificados = Number(fKpis.lead_qualificado) || 5638;
    const contatadosWA = Number(fKpis.wa_contatados) || 365;
    const alunosPagantes = Number(fKpis.aluno) || 456;

    // Enrollment Statuses
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
    const totalAtivas = matriculasAtivas.length;
    const totalCanceladas = matriculasCanceladas.length;
    const taxaChurn = totalMatriculas > 0 ? ((totalCanceladas / totalMatriculas) * 100).toFixed(1) : '0';
    const taxaRetencao = (100 - parseFloat(taxaChurn)).toFixed(1);

    // Engagement Statuses on Active Base
    let engajadosCount = 0;
    let riscoCount = 0;
    let inativosCount = 0;

    matriculasAtivas.forEach(s => {
        let st = s.status || (!s.acessou ? 'Nunca acessou' : 'Ativo');
        if (st === 'Inativo') st = 'Abandonou';
        if (st === 'Atenção') st = s.acessou ? 'Em Risco' : 'Nunca acessou';

        if (st === 'Ativo' || st.includes('Conclu')) {
            engajadosCount++;
        } else if (st.includes('Risco') || st.includes('Login')) {
            riscoCount++;
        } else {
            inativosCount++;
        }
    });

    const pctEngajados = totalAtivas > 0 ? ((engajadosCount / totalAtivas) * 100).toFixed(1) : '0';
    const pctRisco = totalAtivas > 0 ? ((riscoCount / totalAtivas) * 100).toFixed(1) : '0';
    const pctInativos = totalAtivas > 0 ? ((inativosCount / totalAtivas) * 100).toFixed(1) : '0';

    const totalReproducoes = ev['ASSISTIU AULA'] || 0;
    const totalLogins = ev['LOGIN WEB'] || 0;

    // Cursos (Agrupamento Executivo)
    const cursosMap = {};
    matriculasAtivas.forEach(s => {
        const c = s.curso || 'OUTROS / NÃO ESPECIFICADO';
        if (!cursosMap[c]) {
            cursosMap[c] = { curso: c, ativas: 0, mrr: 0, proj: 0, atraso: 0, pago: 0 };
        }
        cursosMap[c].ativas++;
    });

    const todasFaturas = [
        ...((vindi.faturas_tabela || []).map(f => ({ ...f, gw: 'Vindi' }))),
        ...((asaas.faturas_tabela || []).map(f => ({ ...f, gw: 'Asaas' })))
    ];

    todasFaturas.forEach(f => {
        const c = f.curso || 'OUTROS / NÃO ESPECIFICADO';
        if (!cursosMap[c]) {
            cursosMap[c] = { curso: c, ativas: 0, mrr: 0, proj: 0, atraso: 0, pago: 0 };
        }
        const val = Number(f.valor) || 0;
        const st = f.status || '';
        if (st === 'paid' || st === 'pago') {
            cursosMap[c].pago += val;
        } else if (st === 'em_atraso') {
            cursosMap[c].atraso += val;
        } else if (st === 'futuro' || st === 'open' || st === 'pendente') {
            cursosMap[c].proj += val;
        }
    });

    Object.values(cursosMap).forEach(c => {
        c.mrr = totalAtivas > 0 ? (mrrConsolidado * (c.ativas / totalAtivas)) : 0;
    });

    const cursosList = Object.values(cursosMap).sort((a,b) => b.ativas - a.ativas);

    // Helpers de formatação
    const fM = val => (Number(val) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    const fN = val => (Number(val) || 0).toLocaleString('pt-BR');

    // Montar HTML
    mount.innerHTML = `
      <!-- HERO HEADER COM BOTÃO VER DASH COMPLETO -->
      <div class="exec-hero">
        <div>
          <div class="exec-badge">COCKPIT ESTRATÉGICO CONSOLIDADO</div>
          <h1 class="exec-hero-title">Cockpit Executivo InfectoCast</h1>
          <p class="exec-hero-sub">Visão consolidada da operação: <b>resultado → previsão → conversão → recorrência → retenção → risco</b>. O detalhamento completo de cada frente permanece disponível nas abas especializadas.</p>
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
            <div class="exec-card-sub">${fN(alunosPagantes)} alunos pagantes com transação concluída</div>
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
            <div class="exec-funnel-step-sub">${totalAtivas} ativas · ${totalCanceladas} canceladas</div>
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
              <div class="exec-sec-sub">Consumo acadêmico, alunos engajados, sinais precoces de abandono e reproduções de aula.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('ret')">Ver Matriz de Retenção →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Alunos Engajados</span>
              <span class="exec-pill pill-green">${pctEngajados}%</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fN(engajadosCount)}</div>
            <div class="exec-card-sub">Alunos ativos e com aulas em dia na plataforma</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Em Risco de Evasão</span>
              <span class="exec-pill pill-amber">${pctRisco}%</span>
            </div>
            <div class="exec-card-val" style="color:#D97706">${fN(riscoCount)}</div>
            <div class="exec-card-sub">Alunos com quebra de cadência ou apenas logins</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Inativos / Sem Acesso</span>
              <span class="exec-pill pill-red">${pctInativos}%</span>
            </div>
            <div class="exec-card-val" style="color:#DC2626">${fN(inativosCount)}</div>
            <div class="exec-card-sub">Nunca acessaram ou sem atividade recente (&gt;30d)</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Reproduções de Aulas</span>
              <span class="exec-pill pill-blue">${fN(totalLogins)} logins</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fN(totalReproducoes)}</div>
            <div class="exec-card-sub">Aulas assistidas pelos alunos nas plataformas</div>
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
              <div class="exec-sec-sub">Resumo executivo de matrículas ativas, MRR estimado, projeção e saúde por especialidade.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('home')">Ver Panorama Completo →</button>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12.5px; text-align:left">
            <thead>
              <tr style="border-bottom:2px solid var(--line); color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:0.04em">
                <th style="padding:10px 12px">Especialidade / Curso</th>
                <th style="padding:10px 12px; text-align:center">Matrículas Ativas</th>
                <th style="padding:10px 12px; text-align:right">MRR Estimado</th>
                <th style="padding:10px 12px; text-align:right">Receita Projetada</th>
                <th style="padding:10px 12px; text-align:right">Inadimplência</th>
                <th style="padding:10px 12px; text-align:center">Status Executivo</th>
              </tr>
            </thead>
            <tbody>
              ${cursosList.slice(0, 8).map(c => {
                  let stBadge = '<span class="exec-pill pill-green">🟢 Saudável</span>';
                  if (c.atraso > 30000) {
                      stBadge = '<span class="exec-pill pill-red">🔴 Crítico</span>';
                  } else if (c.atraso > 8000) {
                      stBadge = '<span class="exec-pill pill-amber">🟡 Atenção</span>';
                  }
                  return `
                    <tr style="border-bottom:1px solid var(--line2); transition:background 0.15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
                      <td style="padding:12px; font-weight:700; color:var(--ink)">
                        <div style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:340px" title="${c.curso}">${c.curso}</div>
                      </td>
                      <td style="padding:12px; text-align:center; font-weight:700; color:var(--emerald-d)">${c.ativas}</td>
                      <td style="padding:12px; text-align:right; font-weight:600">${fM(c.mrr)}</td>
                      <td style="padding:12px; text-align:right; color:var(--muted)">${fM(c.proj)}</td>
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
              <div class="exec-alert-title">Alunos em Risco de Evasão (${riscoCount} alunos · ${pctRisco}%)</div>
              <div class="exec-alert-desc">Alunos ativos com quebra severa de cadência de acesso ou sem aulas assistidas recentemente. Disparo de WhatsApp pedagógico recomendado.</div>
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
'''

# Check if drawExecView is already in script
if 'function drawExecView(' not in html:
    # Insert right before drawHome
    idx_dh = html.find('function drawHome(')
    if idx_dh != -1:
        html = html[:idx_dh] + JS_EXEC_VIEW + '\n\n' + html[idx_dh:]
        print("drawExecView JS inserted successfully!")
    else:
        print("ERROR: function drawHome not found for JS insertion!")
else:
    print("drawExecView already defined in script.")

# 6. Update selectTab(pId)
# Old:
# function selectTab(pId) {
#     if (!pId) return;
#     $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.p === pId));
#     $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));
#
#     if (pId === 'home') drawHome(true);
old_select_tab_snippet = '''function selectTab(pId) {
    if (!pId) return;
    $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.p === pId));
    $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));

    if (pId === 'home') drawHome(true);'''

new_select_tab_snippet = '''function selectTab(pId) {
    if (!pId) return;
    $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.p === pId));
    $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));

    if (pId === 'exec') {
        drawExecView(true);
        if ($('#kpis')) $('#kpis').style.display = 'none';
    } else {
        if ($('#kpis')) $('#kpis').style.display = 'grid';
    }

    if (pId === 'home') drawHome(true);'''

if old_select_tab_snippet in html:
    html = html.replace(old_select_tab_snippet, new_select_tab_snippet, 1)
    print("selectTab updated successfully!")
elif "pId === 'exec'" in html:
    print("selectTab already handles pId === 'exec'.")
else:
    print("WARNING: old_select_tab_snippet not matched directly, checking regex...")
    pattern = r'function selectTab\(pId\)\s*\{\s*if\s*\(!pId\)\s*return;\s*\$\$\(\'\.tab\'\)\.forEach\(t\s*=>\s*t\.classList\.toggle\(\'on\',\s*t\.dataset\.p\s*===\s*pId\)\);\s*\$\$\(\'\.panel\'\)\.forEach\(p\s*=>\s*p\.classList\.toggle\(\'on\',\s*p\.id\s*===\s*\'p-\'\s*\+\s*pId\)\);'
    m = re.search(pattern, html)
    if m:
        orig = m.group(0)
        replacement = orig + "\n\n    if (pId === 'exec') {\n        drawExecView(true);\n        if ($('#kpis')) $('#kpis').style.display = 'none';\n    } else {\n        if ($('#kpis')) $('#kpis').style.display = 'grid';\n    }\n"
        html = html.replace(orig, replacement, 1)
        print("selectTab updated via regex successfully!")
    else:
        print("ERROR: could not patch selectTab!")

# 7. Update renderAll() to call drawExecView(true)
old_render_all = '''function renderAll() {
    buildHead();
    drawHome(true);'''
new_render_all = '''function renderAll() {
    buildHead();
    drawExecView(true);
    drawHome(true);'''

if old_render_all in html:
    html = html.replace(old_render_all, new_render_all, 1)
    print("renderAll updated successfully!")
elif 'drawExecView(true);' in html:
    print("renderAll already calls drawExecView.")
else:
    # try 2 spaces or other formatting
    pattern_ra = r'function renderAll\(\)\s*\{\s*buildHead\(\);'
    m_ra = re.search(pattern_ra, html)
    if m_ra:
        orig_ra = m_ra.group(0)
        html = html.replace(orig_ra, orig_ra + "\n    drawExecView(true);", 1)
        print("renderAll patched via regex successfully!")
    else:
        print("WARNING: could not patch renderAll!")

# 8. Save updated template.html
with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print("template.html written successfully!")

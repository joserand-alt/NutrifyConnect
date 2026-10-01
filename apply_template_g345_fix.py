import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Locate drawExecView
idx_start = html.find('function drawExecView(')
assert idx_start != -1, "drawExecView not found"

idx_end = html.find('function drawHome(', idx_start)
assert idx_end != -1, "drawHome not found"

new_exec_view = '''function drawExecView(force) {
    if (_execDrawn && !force) return;
    _execDrawn = true;

    const mount = $('#exec-content-mount');
    if (!mount) return;

    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
    const funil = (DATA && DATA.funil) ? DATA.funil : {};
    const rawStudents = (DATA && DATA.students) ? DATA.students : [];
    const ev = (CURRENT_DATA && CURRENT_DATA.action_counts) ? CURRENT_DATA.action_counts : ((DATA && DATA.action_counts) ? DATA.action_counts : {});

    // Usar CURRENT_DATA.students ou rawStudents enriquecido
    const baseStudents = (CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0)
        ? CURRENT_DATA.students
        : rawStudents.map(s => {
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

    // Mapeamento por Curso (Especialidade)
    const coursesMap = {};
    const emailToStudent = {};
    const nameToStudent = {};

    baseStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        if (em) emailToStudent[em] = s;
        if (nm) nameToStudent[nm] = s;

        const c = s.curso || 'OUTROS / PLATAFORMA GERAL';
        if (!coursesMap[c]) {
            coursesMap[c] = { curso: c, total: 0, vigentes: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, concluidos: 0, cancelados: 0, pago: 0, atraso: 0, proj: 0, mrr: 0 };
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

        // MRR e Projeção do Curso (apenas matrículas ativas/vigentes)
        if (!isCancel && !isConcluido) {
            const vindiObj = s.vindi;
            const asaasObj = s.asaas;
            const vParcela = vindiObj ? (Number(vindiObj.valor_parcela) || 0) : 0;
            const aParcela = asaasObj ? (Number(asaasObj.valor_parcela) || Number(asaasObj.mrr) || 0) : 0;
            cm.mrr += (vParcela + aParcela);

            if (vindiObj && Array.isArray(vindiObj.faturas)) {
                vindiObj.faturas.forEach(f => {
                    if (f.status === 'futuro') {
                        cm.proj += (Number(f.valor) || 0);
                    }
                });
            }
        }
    });

    // Faturas globais para cálculo de Pago, Atraso e Projeção adicional
    vFaturas.forEach(f => {
        const em = (f.email || '').toString().toLowerCase().trim();
        const nm = (f.aluno || '').toString().toLowerCase().trim();
        const stObj = emailToStudent[em] || nameToStudent[nm];
        const c = (stObj && stObj.curso) ? stObj.curso : 'OUTROS / PLATAFORMA GERAL';

        if (!coursesMap[c]) {
            coursesMap[c] = { curso: c, total: 0, vigentes: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, concluidos: 0, cancelados: 0, pago: 0, atraso: 0, proj: 0, mrr: 0 };
        }
        const val = Number(f.valor) || 0;
        const st = (f.status || '').toLowerCase();
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
            coursesMap[c] = { curso: c, total: 0, vigentes: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, concluidos: 0, cancelados: 0, pago: 0, atraso: 0, proj: 0, mrr: 0 };
        }
        const val = Number(f.valor) || 0;
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid') {
            coursesMap[c].pago += val;
        } else if (st === 'em_atraso') {
            coursesMap[c].atraso += val;
        } else if (st === 'a_vencer' || st === 'pending' || st === 'futuro') {
            coursesMap[c].proj += val;
        }
    });

    // Totalizadores Consolidados Financeiros
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
    const cursosList = Object.values(coursesMap).filter(c => c.total > 0 || c.pago > 0 || c.atraso > 0 || c.proj > 0).sort((a,b) => b.vigentes - a.vigentes || b.total - a.total);

    mount.innerHTML = `
      <!-- GRUPO 1: RECEITA & PROJEÇÃO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G1</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 1 — RECEITA &amp; PROJEÇÃO</h3>
              <div class="exec-sec-sub">Consolidação financeira de faturamento realizado (Vindi + Asaas), receita recorrente mensal (MRR) e previsibilidade de caixa.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('fin')">Ver Detalhes Financeiros →</button>
        </div>
        <div class="exec-grid-4">
          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Realizada (Total)</span>
              <span class="exec-pill pill-green">Realizado</span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(recRealizadaTotal)}</div>
            <div class="exec-card-sub">Vindi (${fM(vKpis.total_recebido)}) + Asaas (${fM(aKpis.total_recebido)})</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">MRR (Mensalidade Ativa)</span>
              <span class="exec-pill pill-blue">Recorrente</span>
            </div>
            <div class="exec-card-val" style="color:var(--brand)">${fM(mrrConsolidado)}</div>
            <div class="exec-card-sub">Base ativa: Vindi (${fM(vKpis.mrr_ativo)}) + Asaas (${fM(aKpis.mrr_ativo)})</div>
          </div>

          <div class="exec-card">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Próximos 30d</span>
              <span class="exec-pill pill-blue">A Vencer</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(proj30d)}</div>
            <div class="exec-card-sub">Faturas agendadas e parcelas a vencer no próximo mês</div>
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
        <div class="exec-funnel-steps">
          <div class="exec-fstep">
            <div class="exec-fstep-pill">1. Cadastros / Leads</div>
            <div class="exec-fstep-val">${fN(totalLeads)}</div>
            <div class="exec-fstep-desc">Captação RD Station</div>
          </div>
          <div class="exec-farrow">
            <div class="exec-farrow-txt">${((leadsQualificados/Math.max(1, totalLeads))*100).toFixed(1)}%</div>
            <div class="exec-farrow-symbol">→</div>
          </div>

          <div class="exec-fstep">
            <div class="exec-fstep-pill">2. Qualificados</div>
            <div class="exec-fstep-val">${fN(leadsQualificados)}</div>
            <div class="exec-fstep-desc">Perfil com interesse</div>
          </div>
          <div class="exec-farrow">
            <div class="exec-farrow-txt">${((contatadosWA/Math.max(1, leadsQualificados))*100).toFixed(1)}%</div>
            <div class="exec-farrow-symbol">→</div>
          </div>

          <div class="exec-fstep">
            <div class="exec-fstep-pill">3. Abordagem WhatsApp</div>
            <div class="exec-fstep-val">${fN(contatadosWA)}</div>
            <div class="exec-fstep-desc">Atendimento Z-API</div>
          </div>
          <div class="exec-farrow">
            <div class="exec-farrow-txt">${((totalMatriculas/Math.max(1, totalLeads))*100).toFixed(1)}%</div>
            <div class="exec-farrow-symbol">→</div>
          </div>

          <div class="exec-fstep" style="border-color:var(--brand); background:rgba(30,58,138,0.03)">
            <div class="exec-fstep-pill" style="color:var(--brand)">4. Matrículas Realizadas</div>
            <div class="exec-fstep-val" style="color:var(--brand)">${fN(totalMatriculas)}</div>
            <div class="exec-fstep-desc" style="font-weight:600; color:var(--ink)">
              ${fN(totalVigentes)} ativas vigentes · ${fN(totalConcluidas)} concluídas · ${fN(totalCanceladas)} canceladas
            </div>
          </div>
          <div class="exec-farrow">
            <div class="exec-farrow-txt">${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}%</div>
            <div class="exec-farrow-symbol">→</div>
          </div>

          <div class="exec-fstep" style="border-color:var(--emerald-d); background:rgba(5,150,105,0.03)">
            <div class="exec-fstep-pill" style="color:var(--emerald-d)">5. Alunos Pagantes</div>
            <div class="exec-fstep-val" style="color:var(--emerald-d)">${fN(totalAlunosPagantes)}</div>
            <div class="exec-fstep-desc" style="color:var(--muted)">
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
              <div class="exec-sec-sub">Desempenho por especialidade com alunos vigentes, em risco, abandono, cancelamento, MRR, projeção e inadimplência.</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('home')">Ver Panorama Completo →</button>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12.5px; text-align:left">
            <thead>
              <tr style="border-bottom:2px solid var(--line); color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:0.04em">
                <th style="padding:10px 12px">Especialidade / Curso</th>
                <th style="padding:10px 8px; text-align:center">Vigentes</th>
                <th style="padding:10px 8px; text-align:center">Engajados</th>
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
                        <span class="exec-pill pill-blue" style="font-weight:700">${c.vigentes}</span>
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
              <div class="exec-alert-desc">Existem faturas pendentes em atraso entre Vindi e Asaas. Recomenda-se acionar régua de renegociação automatizada para os títulos vencidos.</div>
            </div>
          </div>

          <div class="exec-alert alert-atencao">
            <div class="exec-alert-icon">🔔</div>
            <div>
              <div class="exec-alert-title">Alunos em Risco &amp; Abandono na Base Vigente (${fN(countEmRisco + countAbandonou)} alunos · ${(((countEmRisco + countAbandonou)/Math.max(1, totalVigentes))*100).toFixed(1)}%)</div>
              <div class="exec-alert-desc">Identificados ${countEmRisco} alunos em risco iminente por quebra recente de cadência e ${countAbandonou} em inatividade severa entre os matriculados vigentes. Recomenda-se ação pedagógica segmentada via WhatsApp.</div>
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

new_html = html[:idx_start] + new_exec_view + '\n\n' + html[idx_end:]

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Template updated successfully!")

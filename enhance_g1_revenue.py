import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# Locate the financial KPIs calculations in drawExecView
old_calc_marker = '''    const recRealizadaTotal = (Number(vKpis.total_recebido) || 0) + (Number(aKpis.total_recebido) || 0);
    const recMesAtual = (Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || 0);
    const mrrConsolidado = (Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0);
    const proj30d = (Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0);
    const proj12m = (Number(vKpis.projecao_12m) || 2651945.16);
    const atrasoTotal = (Number(vKpis.total_em_atraso) || 0) + (Number(aKpis.total_em_atraso) || 0);
    const qtdAtrasoTotal = (Number(vKpis.qtd_em_atraso) || 0) + (Number(aKpis.qtd_em_atraso) || 0);
    const taxaAdimplencia = vKpis.taxa_adimplencia || 96;'''

new_calc_marker = '''    const recRealizadaTotal = (Number(vKpis.total_recebido) || 0) + (Number(aKpis.total_recebido) || 0);
    const recMesAtual = (Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || 0);
    const mrrConsolidado = (Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0);
    const proj30d = (Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0);
    const proj12m = (Number(vKpis.projecao_12m) || 2663789.16);
    const atrasoTotal = (Number(vKpis.total_em_atraso) || 0) + (Number(aKpis.total_em_atraso) || 0);
    const qtdAtrasoTotal = (Number(vKpis.qtd_em_atraso) || 0) + (Number(aKpis.qtd_em_atraso) || 0);
    const taxaAdimplencia = vKpis.taxa_adimplencia || 96;

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
    const totalPrevistoMesVigente = recMesAtual + proj30d;
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
    const labelMesAnterior = formatMesLabel(mesAnteriorKey);'''

assert old_calc_marker in text, "old_calc_marker not found in template.html"
text = text.replace(old_calc_marker, new_calc_marker)

# Replace Grupo 1 Markup
old_g1_markup = '''      <!-- GRUPO 1: RECEITA & PROJEÇÃO -->
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
      </div>'''

new_g1_markup = '''      <!-- GRUPO 1: RECEITA & PROJEÇÃO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G1</div>
            <div>
              <h3 class="exec-sec-title">GRUPO 1 — RECEITA &amp; PROJEÇÃO</h3>
              <div class="exec-sec-sub">Faturamento do mês vigente (realizado + projetado), evolução em relação ao mês anterior e previsibilidade de caixa (MRR e Carteira 12m).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="selectTab('fin')">Ver Detalhes Financeiros →</button>
        </div>
        <div class="exec-grid-4">
          <!-- CARD 1: RECEITA MÊS VIGENTE (REALIZADA + PROJETADA) -->
          <div class="exec-card" style="border-top:3px solid var(--emerald)">
            <div class="exec-card-top">
              <span class="exec-card-label">Receita Mês Vigente (${labelMesVigente})</span>
              <span class="exec-pill ${isCrescimentoPositivo ? 'pill-green' : 'pill-amber'}">
                ${isCrescimentoPositivo ? '+' : ''}${pctCrescimentoMoM}% vs ${labelMesAnterior}
              </span>
            </div>
            <div class="exec-card-val" style="color:var(--emerald-d)">${fM(totalPrevistoMesVigente)}</div>
            <div class="exec-card-sub">
              <b>${fM(recMesAtual)}</b> realizado (${pctRealizadoMes}%) + <b>${fM(proj30d)}</b> a vencer
            </div>
          </div>

          <!-- CARD 2: RECEITA MÊS ANTERIOR (COMPARATIVO REALIZADO) -->
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

          <!-- CARD 4: PROJEÇÃO CARTEIRA (12 MESES) -->
          <div class="exec-card" style="border-top:3px solid #7c3aed">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Carteira (12m)</span>
              <span class="exec-pill pill-green">Contratado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(proj12m)}</div>
            <div class="exec-card-sub">Previsão contratual · Total histórico: ${fM(recRealizadaTotal)}</div>
          </div>
        </div>
      </div>'''

assert old_g1_markup in text, "old_g1_markup not found in template.html"
text = text.replace(old_g1_markup, new_g1_markup)

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated Grupo 1 with current month realization + projection and MoM growth in template.html!")

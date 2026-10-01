import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's locate the G7 section inside drawExecView
g7_target = """      <!-- GRUPO 7: ALERTAS EXECUTIVOS -->
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
              <div class="exec-alert-desc">A carteira principal de alunos apresenta taxa de adimplência de 96% e receita recorrente robusta com mais de R$ 2,66M contratados nos próximos 12 meses.</div>
            </div>
          </div>
        </div>
      </div>"""

# Let's write the dynamic replacement for G7
# Note: In template string, we compute the classes, titles, and descriptions dynamically based on the real metrics!
g7_dynamic = """      <!-- GRUPO 7: ALERTAS EXECUTIVOS & SEMÁFORO DE RISCO (DINÂMICO) -->
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
      })()}"""

if g7_target in text:
    text = text.replace(g7_target, g7_dynamic)
    print("Found exact G7 target and replaced with dynamic G7!")
else:
    # Try regex match
    pattern = r'<!-- GRUPO 7: ALERTAS EXECUTIVOS -->\s*<div class="exec-sec">.*?</div>\s*</div>\s*</div>'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        text = text[:match.start()] + g7_dynamic + text[match.end():]
        print("Replaced G7 via regex match!")
    else:
        print("Could not find G7 section in template.html!")

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'w', encoding='utf-8') as f:
    f.write(text)

# Extract JS and test with node
scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_g7.js', 'w', encoding='utf-8') as f:
        f.write(scripts[0])
    res = subprocess.run(['node', '-c', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_g7.js'], capture_output=True, text=True)
    print("Node syntax returncode:", res.returncode)
    if res.returncode != 0:
        print("Node error:", res.stderr)
    else:
        print("SUCCESS! template.html syntax verified 100% CLEAN!")

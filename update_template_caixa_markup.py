import re

with open("template.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Navigation Bar
nav_button = '<button class="tab" data-p="caixa" onclick="selectTab(\'caixa\')" id="btn-tab-caixa" title="Fluxo de Caixa & DRE"><span class="num">💸</span><span class="tab-label">Fluxo de Caixa &amp; DRE</span></button>'

if 'data-p="caixa"' not in html:
    # insert after btn-tab-fin
    html = html.replace(
        '<button class="tab" data-p="fin" onclick="selectTab(\'fin\')" id="btn-tab-fin" title="Financeiro & Projeção"><span class="num">$</span><span class="tab-label">Financeiro &amp; Projeção</span></button>',
        '<button class="tab" data-p="fin" onclick="selectTab(\'fin\')" id="btn-tab-fin" title="Financeiro & Projeção"><span class="num">$</span><span class="tab-label">Financeiro &amp; Projeção</span></button>\n      ' + nav_button
    )
    print("Added nav button to #tabs")
else:
    print("Nav button already present")

# 2. Add Section #p-caixa
section_caixa = """
  <!-- PANEL: FLUXO DE CAIXA & DRE REALIZADA (EXTRATO & PREVISÃO DE LIQUIDEZ) -->
  <section class="panel" id="p-caixa">
    <div class="sec-head" style="margin-bottom:22px">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; width:100%">
        <div>
          <div style="display:flex; align-items:center; gap:8px">
            <h2 style="font-size:22px; font-weight:800; color:var(--ink); margin:0">💸 Fluxo de Caixa &amp; DRE Gerencial</h2>
            <span style="font-size:11px; font-weight:700; padding:2px 10px; border-radius:12px; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.25)">Extrato Bancário &amp; Previsão</span>
          </div>
          <p style="margin:4px 0 0; font-size:13px; color:var(--muted)">Análise detalhada de saídas de caixa dia a dia, DRE contábil, extrato itemizado e modelo de projeção de liquidez futura.</p>
        </div>
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap">
          <div style="display:flex; align-items:center; gap:6px; background:var(--card); border:1px solid var(--line2); padding:5px 8px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.03)">
            <span style="font-size:11px; font-weight:700; color:var(--muted); margin-right:2px">Visão:</span>
            <button class="chip on" id="caixa-tab-btn-diario" onclick="_caixaSwitchSubTab('diario')" style="font-size:11px; padding:4px 10px; font-weight:700">📊 Evolução Diária</button>
            <button class="chip" id="caixa-tab-btn-dre" onclick="_caixaSwitchSubTab('dre')" style="font-size:11px; padding:4px 10px; font-weight:700">📑 DRE &amp; Categorias</button>
            <button class="chip" id="caixa-tab-btn-projecao" onclick="_caixaSwitchSubTab('projecao')" style="font-size:11px; padding:4px 10px; font-weight:700">🔮 Previsão 6 Meses</button>
            <button class="chip" id="caixa-tab-btn-diagnostico" onclick="_caixaSwitchSubTab('diagnostico')" style="font-size:11px; padding:4px 10px; font-weight:700">🚨 Riscos &amp; Alertas</button>
            <button class="chip" id="caixa-tab-btn-extrato" onclick="_caixaSwitchSubTab('extrato')" style="font-size:11px; padding:4px 10px; font-weight:700">📋 Extrato Itemizado</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 1. KPIS GERAIS DE CAIXA -->
    <div id="caixa-kpis-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr)); gap:12px; margin-bottom:22px"></div>

    <!-- 2. SUB-PAINEL 1: EVOLUÇÃO DIÁRIA & BURN RATE -->
    <div id="caixa-view-diario" class="caixa-subview">
      <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; margin-bottom:22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; margin-bottom:18px">
          <div>
            <div style="display:flex; align-items:center; gap:8px">
              <h3 style="font-size:16px; font-weight:800; color:var(--ink); margin:0">Curva Diária de Entradas vs Saídas &amp; Saldo de Caixa</h3>
              <span style="font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:12px; background:rgba(2,132,199,0.1); color:#0284c7; border:1px solid rgba(2,132,199,0.25)">Setembro/2026</span>
            </div>
            <div style="font-size:11.5px; color:var(--muted); margin-top:3px">
              Comparativo dia a dia dos desembolsos, entradas de gateways e curva de liquidez da conta PJ.
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:14px; font-size:11.5px; font-weight:600; flex-wrap:wrap">
            <div style="display:flex; align-items:center; gap:6px">
              <span style="display:inline-block; width:12px; height:12px; border-radius:3px; background:#10b981"></span>
              <span>Entradas (Yapay/Pix)</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px">
              <span style="display:inline-block; width:12px; height:12px; border-radius:3px; background:#f43f5e"></span>
              <span>Saídas (Desembolsos)</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px">
              <span style="display:inline-block; width:18px; height:3px; background:#06b6d4"></span>
              <span>Saldo de Caixa</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px">
              <span style="display:inline-block; width:18px; height:2px; border-top:2px dashed #eab308"></span>
              <span>Colchão de Segurança (R$ 50k)</span>
            </div>
          </div>
        </div>

        <div id="caixa-daily-chart-container" style="height:280px; position:relative"></div>

        <div style="margin-top:14px; padding:12px 14px; background:rgba(239,68,68,0.05); border:1px solid rgba(239,68,68,0.18); border-radius:8px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; font-size:11.5px">
          <div style="display:flex; align-items:center; gap:8px">
            <span style="font-size:16px">🚨</span>
            <span style="color:var(--ink)"><b>Dias Críticos de Liquidez:</b> No dia <b>21/09</b> (saída de R$ 80,9k) e no dia <b>25/09</b> (saída de R$ 35,5k), o saldo desceu para <b>R$ 13.023,47</b>, operando próximo da margem limite.</span>
          </div>
          <button onclick="_caixaSwitchSubTab('diagnostico')" style="background:#ef4444; color:#fff; border:none; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:700; cursor:pointer">Ver Diagnóstico Completo →</button>
        </div>
      </div>

      <!-- TABELA CRONOLÓGICA DIÁRIA -->
      <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px">
          <h3 style="font-size:15px; font-weight:800; color:var(--ink); margin:0">📅 Movimentação Financeira Dia a Dia (Setembro/2026)</h3>
          <span style="font-size:11px; color:var(--muted)">22 dias com movimentação bancária registrada</span>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left">
            <thead>
              <tr style="border-bottom:2px solid var(--line2); color:var(--muted); font-size:11px; text-transform:uppercase">
                <th style="padding:10px 8px">Data</th>
                <th style="padding:10px 8px; text-align:right">Entradas (R$)</th>
                <th style="padding:10px 8px; text-align:right">Saídas (R$)</th>
                <th style="padding:10px 8px; text-align:right">Resultado Líquido</th>
                <th style="padding:10px 8px; text-align:right">Saldo em Conta</th>
                <th style="padding:10px 8px; text-align:center">Nível de Pressão</th>
              </tr>
            </thead>
            <tbody id="caixa-daily-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 3. SUB-PAINEL 2: DRE GERENCIAL & CATEGORIAS -->
    <div id="caixa-view-dre" class="caixa-subview" style="display:none">
      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap:20px; margin-bottom:22px">
        <!-- DRE Demonstrativo -->
        <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
            <h3 style="font-size:16px; font-weight:800; color:var(--ink); margin:0">📑 DRE de Caixa Realizada (Setembro/2026)</h3>
            <span style="font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:12px; background:rgba(18,161,122,0.1); color:var(--emerald-d); border:1px solid rgba(18,161,122,0.2)">Regime de Caixa</span>
          </div>
          <div id="caixa-dre-content" style="font-size:12.5px"></div>
        </div>

        <!-- Gráfico de Distribuição por Categoria -->
        <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
            <h3 style="font-size:16px; font-weight:800; color:var(--ink); margin:0">🥧 Onde o Dinheiro Foi Gasto (Categorias)</h3>
            <span style="font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:12px; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2)">Total: R$ 470,8k</span>
          </div>
          <div id="caixa-category-bars" style="display:flex; flex-direction:column; gap:12px"></div>
        </div>
      </div>

      <!-- TOP BENEFICIÁRIOS / DESTINATÁRIOS DE SAÍDA -->
      <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px">
          <div>
            <h3 style="font-size:15.5px; font-weight:800; color:var(--ink); margin:0">👥 Maiores Beneficiários e Destinos de Saída</h3>
            <p style="margin:2px 0 0; font-size:11.5px; color:var(--muted)">Ranking consolidado de pagamentos para docentes, parceiros, fornecedores e sócios.</p>
          </div>
          <span style="font-size:11px; font-weight:700; color:var(--muted)">Top 25 Destinos</span>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left">
            <thead>
              <tr style="border-bottom:2px solid var(--line2); color:var(--muted); font-size:11px; text-transform:uppercase">
                <th style="padding:10px 8px">#</th>
                <th style="padding:10px 8px">Beneficiário / Destino</th>
                <th style="padding:10px 8px">Categoria</th>
                <th style="padding:10px 8px; text-align:center">Qtd Lançamentos</th>
                <th style="padding:10px 8px; text-align:right">Total Pago (R$)</th>
                <th style="padding:10px 8px; text-align:right">% do Total</th>
              </tr>
            </thead>
            <tbody id="caixa-beneficiarios-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 4. SUB-PAINEL 3: PREVISÃO DE LIQUIDEZ (6 MESES) -->
    <div id="caixa-view-projecao" class="caixa-subview" style="display:none">
      <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; margin-bottom:22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; margin-bottom:18px">
          <div>
            <div style="display:flex; align-items:center; gap:8px">
              <h3 style="font-size:16px; font-weight:800; color:var(--ink); margin:0">🔮 Modelo de Previsão de Liquidez &amp; Desembolsos (Out/26 a Mar/27)</h3>
              <span style="font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:12px; background:rgba(99,102,241,0.1); color:#6366f1; border:1px solid rgba(99,102,241,0.25)">Projeção Dinâmica</span>
            </div>
            <div style="font-size:11.5px; color:var(--muted); margin-top:3px">
              Cruzamento dos recebíveis futuros de assinaturas ativas (Vindi + Asaas) com a taxa mensal projetada de despesas operacionais.
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:14px; font-size:11.5px; font-weight:600">
            <div style="display:flex; align-items:center; gap:6px">
              <span style="display:inline-block; width:12px; height:12px; border-radius:3px; background:#3b82f6"></span>
              <span>Recebíveis Projetados</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px">
              <span style="display:inline-block; width:12px; height:12px; border-radius:3px; background:#f43f5e"></span>
              <span>Desembolsos Estimados</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px">
              <span style="display:inline-block; width:18px; height:3px; background:#10b981"></span>
              <span>Saldo Projetado</span>
            </div>
          </div>
        </div>

        <div id="caixa-forecast-chart-container" style="height:260px; position:relative"></div>
      </div>

      <!-- TABELA DE PROJEÇÃO MENSAL -->
      <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px">
          <h3 style="font-size:15px; font-weight:800; color:var(--ink); margin:0">📋 Cronograma de Liquidez Projetada (6 Meses)</h3>
          <span style="font-size:11px; color:var(--muted)">Saldo Inicial Base: R$ 55.730,86 (Fechamento Set/26)</span>
        </div>
        <div style="overflow-x:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left">
            <thead>
              <tr style="border-bottom:2px solid var(--line2); color:var(--muted); font-size:11px; text-transform:uppercase">
                <th style="padding:10px 8px">Mês</th>
                <th style="padding:10px 8px; text-align:right">Recebíveis Previstos (R$)</th>
                <th style="padding:10px 8px; text-align:right">Desembolsos Estimados (R$)</th>
                <th style="padding:10px 8px; text-align:right">Resultado do Mês</th>
                <th style="padding:10px 8px; text-align:right">Saldo Final Projetado</th>
                <th style="padding:10px 8px; text-align:center">Status de Risco</th>
              </tr>
            </thead>
            <tbody id="caixa-forecast-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 5. SUB-PAINEL 4: DIAGNÓSTICO E RECOMENDAÇÕES -->
    <div id="caixa-view-diagnostico" class="caixa-subview" style="display:none">
      <div id="caixa-diagnosticos-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap:16px; margin-bottom:22px"></div>
    </div>

    <!-- 6. SUB-PAINEL 5: EXTRATO ITEMIZADO COMPLETO -->
    <div id="caixa-view-extrato" class="caixa-subview" style="display:none">
      <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 22px; box-shadow:0 2px 10px rgba(0,0,0,0.03)">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px">
          <div>
            <h3 style="font-size:15.5px; font-weight:800; color:var(--ink); margin:0">📋 Extrato Completo de Saídas (90 Lançamentos)</h3>
            <p style="margin:2px 0 0; font-size:11.5px; color:var(--muted)">Busca rápida e filtragem por categoria, fornecedor ou modalidade de pagamento.</p>
          </div>
          <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap">
            <input type="text" id="caixa-extrato-search" oninput="_caixaFilterExtrato()" placeholder="🔍 Buscar beneficiário ou descrição..." style="background:var(--paper); border:1px solid var(--line); border-radius:8px; padding:6px 12px; font-size:12px; color:var(--ink); min-width:240px">
            <select id="caixa-extrato-cat-filter" onchange="_caixaFilterExtrato()" style="background:var(--paper); border:1px solid var(--line); border-radius:8px; padding:6px 10px; font-size:12px; color:var(--ink)">
              <option value="all">Todas as Categorias</option>
              <option value="Professores & Prestadores PF">Professores &amp; Prestadores PF</option>
              <option value="Cartão de Crédito / Fatura">Cartão de Crédito PJ</option>
              <option value="Corpo Docente & Especialistas">Corpo Docente / PJs Médicas</option>
              <option value="Sócios / Distribuição">Sócios / Distribuição</option>
              <option value="Produção Audiovisual & Marketing">Audiovisual &amp; Marketing</option>
              <option value="Parcerias Acadêmicas & Certificação">Parcerias Acadêmicas (FFM)</option>
              <option value="Impostos & Tributos">Impostos &amp; Tributos</option>
              <option value="Aluguel & Infraestrutura">Aluguel &amp; Sede</option>
            </select>
          </div>
        </div>

        <div style="overflow-x:auto; max-height:550px; overflow-y:auto">
          <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left">
            <thead style="position:sticky; top:0; background:var(--card); z-index:2; border-bottom:2px solid var(--line2)">
              <tr style="color:var(--muted); font-size:11px; text-transform:uppercase">
                <th style="padding:10px 8px">Data</th>
                <th style="padding:10px 8px">Tipo</th>
                <th style="padding:10px 8px">Beneficiário / Descrição</th>
                <th style="padding:10px 8px">Categoria</th>
                <th style="padding:10px 8px; text-align:right">Valor (R$)</th>
              </tr>
            </thead>
            <tbody id="caixa-extrato-tbody"></tbody>
          </table>
        </div>
        <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center; font-size:11.5px; color:var(--muted)">
          <span id="caixa-extrato-count">Exibindo lançamentos</span>
          <span>Fonte: Extrato Bancário Nubank PJ Oficial</span>
        </div>
      </div>
    </div>
  </section>
"""

if 'id="p-caixa"' not in html:
    html = html.replace('</section>\n\n\n<!-- MODAL DE AUDITORIA', '</section>\n' + section_caixa + '\n\n<!-- MODAL DE AUDITORIA')
    if 'id="p-caixa"' not in html:
        # try without newlines
        html = html.replace('</section>\n\n<!-- MODAL DE AUDITORIA', '</section>\n' + section_caixa + '\n\n<!-- MODAL DE AUDITORIA')
    print("Added #p-caixa section to HTML")
else:
    print("#p-caixa section already present")

# 3. Update selectTab(pId)
if "if (pId === 'caixa')" not in html:
    html = html.replace(
        "if (pId === 'fin') { try { drawFinanceiro(true); } catch(e) { console.error('Erro drawFinanceiro:', e); } }",
        "if (pId === 'fin') { try { drawFinanceiro(true); } catch(e) { console.error('Erro drawFinanceiro:', e); } }\n        if (pId === 'caixa') { try { drawCaixaView(true); } catch(e) { console.error('Erro drawCaixaView:', e); } }"
    )
    print("Updated selectTab for 'caixa'")

# 4. Update renderAll()
if "if (typeof drawCaixaView === 'function')" not in html:
    html = html.replace(
        "drawFinanceiro(true);",
        "drawFinanceiro(true);\n  if (typeof drawCaixaView === 'function') { drawCaixaView(true); }"
    )
    print("Updated renderAll for drawCaixaView")

with open("template.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Saved template.html structure updates")

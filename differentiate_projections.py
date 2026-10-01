import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the Course projection calculation
old_course_proj = '''        cm.proj_1m = cm.proj_mes_atual > 0 ? cm.proj_mes_atual : (cm.mrr * 0.9);
        cm.proj_3m = cm.mrr * 3;
        cm.proj_6m = cm.mrr * 6;
        cm.proj_12m = cm.mrr * 12;'''

new_course_proj = '''        cm.proj_1m = cm.mrr;
        cm.proj_3m = cm.mrr * 3;
        cm.proj_6m = cm.mrr * 6;
        cm.proj_12m = cm.mrr * 12;'''

if old_course_proj in text:
    text = text.replace(old_course_proj, new_course_proj)
    print("Updated course proj_1m to cm.mrr")

# Replace Projections in Grupo 1 HTML
old_proj_cards = '''        <!-- LINHA 2: PROJEÇÕES FUTURAS DE CARTEIRA (1m, 3m, 6m, 12m) -->
        <div class="exec-grid-4">
          <!-- CARD 5: PROJEÇÃO 1 MÊS (30 DIAS) -->
          <div class="exec-card" style="background:rgba(2,132,199,0.02); border-left:3px solid #0284c7">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 1 Mês (30 dias)</span>
              <span class="exec-pill pill-blue">A Vencer (30d)</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(proj30d)}</div>
            <div class="exec-card-sub">Faturas agendadas com vencimento nos próximos 30 dias</div>
          </div>

          <!-- CARD 6: PROJEÇÃO 3 MESES (TRIMESTRE) -->
          <div class="exec-card" style="background:rgba(79,70,229,0.02); border-left:3px solid #4f46e5">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 3 Meses (Trimestre)</span>
              <span class="exec-pill pill-blue">Próx. 90d</span>
            </div>
            <div class="exec-card-val" style="color:#4f46e5">${fM(proj3mConsolidada)}</div>
            <div class="exec-card-sub">Previsão contratual da carteira para os próximos 3 meses</div>
          </div>

          <!-- CARD 7: PROJEÇÃO 6 MESES (SEMESTRE) -->
          <div class="exec-card" style="background:rgba(124,58,237,0.02); border-left:3px solid #7c3aed">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 6 Meses (Semestre)</span>
              <span class="exec-pill pill-blue">Próx. 180d</span>
            </div>
            <div class="exec-card-val" style="color:#7c3aed">${fM(proj6mConsolidada)}</div>
            <div class="exec-card-sub">Previsão contratual da carteira para os próximos 6 meses</div>
          </div>

          <!-- CARD 8: PROJEÇÃO 12 MESES (ANUAL) -->
          <div class="exec-card" style="background:rgba(5,150,105,0.02); border-left:3px solid var(--emerald-d)">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Carteira (12 Meses)</span>
              <span class="exec-pill pill-green">Contratado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(proj12m)}</div>
            <div class="exec-card-sub">Previsão contratual de faturamento anual da carteira</div>
          </div>
        </div>'''

new_proj_cards = '''        <!-- LINHA 2: PROJEÇÕES FUTURAS DE CARTEIRA (1m, 3m, 6m, 12m) -->
        <div class="exec-grid-4">
          <!-- CARD 5: PROJEÇÃO 1 MÊS (30 DIAS) -->
          <div class="exec-card" style="background:rgba(2,132,199,0.02); border-left:3px solid #0284c7">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 1 Mês (30 dias)</span>
              <span class="exec-pill pill-blue">Ciclo Mensal</span>
            </div>
            <div class="exec-card-val" style="color:#0284c7">${fM(mrrConsolidado)}</div>
            <div class="exec-card-sub">Faturamento projetado de 1 ciclo mensal completo da carteira ativa (MRR)</div>
          </div>

          <!-- CARD 6: PROJEÇÃO 3 MESES (TRIMESTRE) -->
          <div class="exec-card" style="background:rgba(79,70,229,0.02); border-left:3px solid #4f46e5">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 3 Meses (Trimestre)</span>
              <span class="exec-pill pill-blue">Próx. 90d</span>
            </div>
            <div class="exec-card-val" style="color:#4f46e5">${fM(proj3mConsolidada)}</div>
            <div class="exec-card-sub">Previsão contratual da carteira para os próximos 3 meses</div>
          </div>

          <!-- CARD 7: PROJEÇÃO 6 MESES (SEMESTRE) -->
          <div class="exec-card" style="background:rgba(124,58,237,0.02); border-left:3px solid #7c3aed">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção 6 Meses (Semestre)</span>
              <span class="exec-pill pill-blue">Próx. 180d</span>
            </div>
            <div class="exec-card-val" style="color:#7c3aed">${fM(proj6mConsolidada)}</div>
            <div class="exec-card-sub">Previsão contratual da carteira para os próximos 6 meses</div>
          </div>

          <!-- CARD 8: PROJEÇÃO 12 MESES (ANUAL) -->
          <div class="exec-card" style="background:rgba(5,150,105,0.02); border-left:3px solid var(--emerald-d)">
            <div class="exec-card-top">
              <span class="exec-card-label">Projeção Carteira (12 Meses)</span>
              <span class="exec-pill pill-green">Contratado</span>
            </div>
            <div class="exec-card-val" style="color:var(--ink)">${fM(proj12m)}</div>
            <div class="exec-card-sub">Previsão contratual de faturamento anual da carteira</div>
          </div>
        </div>'''

assert old_proj_cards in text, "old_proj_cards not found in template.html"
text = text.replace(old_proj_cards, new_proj_cards)

# Also update the card 1 subtitle to be very clear that R$ 152k is specifically the amount due in the remainder of September
old_card1_sub = '<b>${fM(recMesAtual)}</b> realizado (${pctRealizadoMes}%) + <b>${fM(proj30d)}</b> a vencer'
new_card1_sub = '<b>${fM(recMesAtual)}</b> realizado (${pctRealizadoMes}%) + <b>${fM(proj30d)}</b> a vencer em ${labelMesVigente}'

if old_card1_sub in text:
    text = text.replace(old_card1_sub, new_card1_sub)
    print("Updated card 1 subtitle to clarify remaining days in current month.")

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("Template updated successfully!")

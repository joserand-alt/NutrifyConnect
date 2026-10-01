import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace Funnel markup
old_funnel_markup = '''        <div class="exec-funnel-steps">
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
        </div>'''

new_funnel_markup = '''        <div class="exec-funnel-bar">
          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">1. Cadastros / Leads</div>
            <div class="exec-funnel-step-val">${fN(totalLeads)}</div>
            <div class="exec-funnel-step-sub">Captação RD Station</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((leadsQualificados/Math.max(1, totalLeads))*100).toFixed(1)}%</span>
            <span>→</span>
          </div>

          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">2. Qualificados</div>
            <div class="exec-funnel-step-val">${fN(leadsQualificados)}</div>
            <div class="exec-funnel-step-sub">Perfil com interesse</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((contatadosWA/Math.max(1, leadsQualificados))*100).toFixed(1)}%</span>
            <span>→</span>
          </div>

          <div class="exec-funnel-step">
            <div class="exec-funnel-step-label">3. Abordagem WhatsApp</div>
            <div class="exec-funnel-step-val">${fN(contatadosWA)}</div>
            <div class="exec-funnel-step-sub">Atendimento Z-API</div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate">${((totalMatriculas/Math.max(1, totalLeads))*100).toFixed(1)}%</span>
            <span>→</span>
          </div>

          <div class="exec-funnel-step" style="border-color:var(--brand); background:rgba(30,58,138,0.03)">
            <div class="exec-funnel-step-label" style="color:var(--brand)">4. Matrículas Realizadas</div>
            <div class="exec-funnel-step-val" style="color:var(--brand)">${fN(totalMatriculas)}</div>
            <div class="exec-funnel-step-sub" style="font-weight:600; color:var(--ink)">
              ${fN(totalVigentes)} ativas vigentes · ${fN(totalConcluidas)} concluídas · ${fN(totalCanceladas)} canceladas
            </div>
          </div>

          <div class="exec-funnel-arrow">
            <span class="exec-funnel-rate" style="background:rgba(5,150,105,0.1); color:var(--emerald-d)">${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}%</span>
            <span>→</span>
          </div>

          <div class="exec-funnel-step step-highlight" style="border-color:var(--emerald-d); background:rgba(5,150,105,0.03)">
            <div class="exec-funnel-step-label" style="color:var(--emerald-d)">5. Alunos Pagantes</div>
            <div class="exec-funnel-step-val" style="color:var(--emerald-d)">${fN(totalAlunosPagantes)}</div>
            <div class="exec-funnel-step-sub" style="color:var(--muted)">
              Com fatura paga confirmada (${((totalAlunosPagantes/Math.max(1, totalMatriculas))*100).toFixed(1)}% da base)
            </div>
          </div>
        </div>'''

assert old_funnel_markup in text, "old_funnel_markup not found in template.html"
text = text.replace(old_funnel_markup, new_funnel_markup)

# Ensure CSS aliases for both classes exist
css_marker = '/* FUNIL PIPELINE */'
css_enhancement = '''/* FUNIL PIPELINE */
.exec-funnel-bar, .exec-funnel-steps {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow-x: auto;
  padding: 6px 0;
  width: 100%;
}
.exec-funnel-step, .exec-fstep {
  flex: 1;
  min-width: 170px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 16px;
  position: relative;
}
.exec-funnel-step.step-highlight, .exec-fstep.step-highlight {
  background: rgba(18, 161, 122, 0.05);
  border-color: rgba(18, 161, 122, 0.4);
}
.exec-funnel-step-label, .exec-fstep-pill {
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}
.exec-funnel-step-val, .exec-fstep-val {
  font-family: var(--disp);
  font-size: 22px;
  font-weight: 700;
  color: var(--ink);
}
.exec-funnel-step-sub, .exec-fstep-desc {
  font-size: 11px;
  color: var(--muted2);
  margin-top: 2px;
}
.exec-funnel-arrow, .exec-farrow {
  color: var(--muted2);
  font-size: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex: none;
}
.exec-funnel-rate, .exec-farrow-txt {
  font-size: 10.5px;
  font-weight: 800;
  color: var(--emerald-d);
  background: rgba(18, 161, 122, 0.1);
  padding: 2px 6px;
  border-radius: 6px;
  white-space: nowrap;
}
'''

idx_css = text.find('/* FUNIL PIPELINE */')
idx_css_end = text.find('/* ALERT CARDS */', idx_css)
assert idx_css != -1 and idx_css_end != -1, "css markers not found"

text = text[:idx_css] + css_enhancement + '\n' + text[idx_css_end:]

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("Funnel markup and CSS classes updated successfully in template.html!")

import os, re

target_paths = [
    r"c:\Users\DELL\Desktop\Dash_InfectoCast\template.html",
    r"c:\Users\DELL\Desktop\Acompanhamento de acessos\template.html"
]

clean_modal_html = """<!-- ============================================================================= -->
<!-- MODAL: PIPELINE DE LEADS & ATENDIMENTOS RD CONVERSAS (WHATSAPP) -->
<!-- ============================================================================= -->
<div id="modal-rd-conversas-leads" class="modal-ov" style="z-index:10005; align-items:flex-start; justify-content:center; padding:24px 16px; overflow-y:auto;">
  <div style="background:var(--card); border:1px solid var(--line); border-radius:16px; width:100%; max-width:1180px; max-height:90vh; display:flex; flex-direction:column; box-shadow:0 25px 50px -12px rgba(0,0,0,0.35); overflow:hidden; animation:pop .22s cubic-bezier(.2,.9,.3,1.2); margin:auto;">
    
    <!-- HEADER DO MODAL -->
    <div style="padding:18px 24px; border-bottom:1px solid var(--line2); display:flex; justify-content:space-between; align-items:center; background:linear-gradient(180deg, var(--card) 0%, rgba(16,185,129,0.03) 100%); flex-shrink:0;">
      <div style="display:flex; align-items:center; gap:14px;">
        <div style="width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg, #10b981 0%, #059669 100%); display:flex; align-items:center; justify-content:center; color:#fff; font-size:22px; box-shadow:0 4px 12px rgba(16,185,129,0.3);">
          💬
        </div>
        <div>
          <h3 style="font-family:var(--disp); font-size:18px; font-weight:800; color:var(--ink); margin:0; display:flex; align-items:center; gap:8px;">
            RD Station Conversas (WhatsApp) · Gestão de Atendimentos
            <span class="exec-pill pill-green" id="mrd-badge-total" style="font-size:10.5px;">316 Contatos</span>
          </h3>
          <div style="font-size:12px; color:var(--muted); margin-top:3px;">
            Segmentação precisa entre <b>Oportunidades Comerciais</b> (pré-matrícula), <b>Vendas Fechadas</b> e <b>Suporte/CX</b> (atendimento a alunos já matriculados).
          </div>
        </div>
      </div>
      <button onclick="closeModalRDConversas()" style="background:rgba(0,0,0,0.05); border:1px solid var(--line); color:var(--ink); font-size:18px; cursor:pointer; width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; line-height:1; transition:all .15s;" onmouseover="this.style.background='rgba(0,0,0,0.1)'" onmouseout="this.style.background='rgba(0,0,0,0.05)'">&times;</button>
    </div>

    <!-- CORPO DO MODAL (SCROLL PRINCIPAL) -->
    <div style="padding:20px 24px; overflow-y:auto; -webkit-overflow-scrolling:touch; overscroll-behavior:contain; flex:1 1 auto; min-height:0; display:flex; flex-direction:column; gap:16px;">
      
      <!-- KPIS DO MODAL -->
      <div id="mrd-kpis" style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; flex-shrink:0;"></div>

      <!-- CONTROLES, FILTROS E BUSCA -->
      <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; padding:12px 16px; background:var(--bg); border:1px solid var(--line2); border-radius:10px; flex-shrink:0;">
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          <button id="mrd-btn-all" class="chip on" onclick="filterRDConversasLeads('all')">Todos (<span id="mrd-count-all">316</span>)</button>
          <button id="mrd-btn-hot" class="chip" onclick="filterRDConversasLeads('hot')">🔥 Comercial - Oportunidades (<span id="mrd-count-hot">228</span>)</button>
          <button id="mrd-btn-support" class="chip" onclick="filterRDConversasLeads('support')">🎓 Suporte & CX ao Aluno (<span id="mrd-count-support">76</span>)</button>
          <button id="mrd-btn-sales" class="chip" onclick="filterRDConversasLeads('sales')">✅ Vendas Convertidas (<span id="mrd-count-sales">12</span>)</button>
        </div>

        <div style="display:flex; align-items:center; gap:10px;">
          <input type="text" id="mrd-search" placeholder="🔍 Buscar por nome, telefone ou e-mail..." oninput="handleRDConversasSearch(this.value)" style="padding:8px 14px; border:1px solid var(--line); border-radius:8px; font-size:12px; width:270px; background:var(--card); color:var(--ink); outline:none;" />
          <button onclick="exportRDConversasCSV()" style="background:var(--brand); color:#fff; border:none; padding:8px 16px; border-radius:8px; font-size:11.5px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:6px; transition:opacity .15s;" onmouseover="this.style.opacity='.9'" onmouseout="this.style.opacity='1'">
            📥 Exportar CSV
          </button>
        </div>
      </div>

      <!-- TABELA DE LEADS COM SCROLL INTERNO E HEADER FIXO -->
      <div style="border:1px solid var(--line); border-radius:10px; overflow-y:auto; overflow-x:auto; -webkit-overflow-scrolling:touch; overscroll-behavior:contain; max-height:48vh; min-height:260px; background:var(--card); flex:1 1 auto;">
        <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left;">
          <thead>
            <tr style="position:sticky; top:0; z-index:5; background:var(--card-hover); backdrop-filter:blur(8px); border-bottom:1px solid var(--line); color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:0.5px;">
              <th style="padding:10px 14px; background:inherit;">Médico / Contato</th>
              <th style="padding:10px 14px; background:inherit;">WhatsApp</th>
              <th style="padding:10px 14px; background:inherit;">E-mail</th>
              <th style="padding:10px 14px; background:inherit;">Natureza do Atendimento</th>
              <th style="padding:10px 14px; background:inherit;">Data Contato vs Matrícula</th>
              <th style="padding:10px 14px; background:inherit;">Curso / Detalhes</th>
              <th style="padding:10px 14px; text-align:center; background:inherit;">Ação</th>
            </tr>
          </thead>
          <tbody id="mrd-table-body"></tbody>
        </table>
      </div>

    </div>

    <!-- FOOTER DO MODAL -->
    <div style="padding:14px 24px; border-top:1px solid var(--line2); background:var(--bg); display:flex; justify-content:space-between; align-items:center; flex-shrink:0;">
      <div style="font-size:11.5px; color:var(--muted);">
        Integração Oficial RD Station Conversas (Tallos v2) · Classificação cronológica auditada.
      </div>
      <button onclick="closeModalRDConversas()" style="background:var(--card); color:var(--ink); border:1px solid var(--line); padding:7px 20px; border-radius:8px; font-size:12px; font-weight:700; cursor:pointer; transition:all .15s;" onmouseover="this.style.background='var(--card-hover)'" onmouseout="this.style.background='var(--card)'">
        Fechar
      </button>
    </div>

  </div>
</div>
"""

for target_path in target_paths:
    if not os.path.exists(target_path):
        continue
    with open(target_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove old modal that was at the end of the file
    old_modal_pattern = r'<!-- =+ -->\s*<!-- MODAL: PIPELINE DE LEADS & ATENDIMENTOS RD CONVERSAS[\s\S]*?</div>\s*</div>\s*$'
    content_clean = re.sub(old_modal_pattern, '', content)
    
    # 2. Also remove any dangling modal-rd-conversas-leads if present
    content_clean = re.sub(r'<div id="modal-rd-conversas-leads"[\s\S]*?</div>\s*</div>\s*</div>', '', content_clean)

    # 3. Insert the clean modal HTML right after <div class="modal-ov" id="modal-sync-24h">...</div> (around line 2087)
    target_marker = '</div>\n</div>\n\n<div class="modal-ov" id="modal">'
    if target_marker in content_clean:
        content_clean = content_clean.replace(target_marker, '</div>\n</div>\n\n' + clean_modal_html + '\n\n<div class="modal-ov" id="modal">', 1)
    else:
        # Fallback: before </body>
        content_clean = content_clean.replace('</body>', clean_modal_html + '\n</body>', 1)

    # 4. Ensure openModalRDConversas uses modal.classList.add('on') and handles body scroll
    old_js_open = """        modal.style.display = 'flex';
        modal.classList.add('on');
        document.body.style.overflow = 'hidden';"""
    new_js_open = """        modal.style.display = 'flex';
        modal.classList.add('on');
        document.body.style.overflow = 'hidden';"""

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content_clean)
    print(f"Updated {target_path} successfully!")

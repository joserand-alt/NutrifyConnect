import re

template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# -------------------------------------------------------------
# 1. Update Status Logic in applyFilters (Lines ~1140)
# -------------------------------------------------------------
p_status = re.compile(
    r"const vindiStatus = scopy\.vindi \? \(scopy\.vindi\.status_financeiro \|\| scopy\.vindi\.status_assinatura\) : null;\s*"
    r"if \(vindiStatus === ['\"]cancelado['\"] \|\| vindiStatus === ['\"]canceled['\"]\) \{\s*"
    r"scopy\.status = ['\"]Cancelado['\"];\s*"
    r"scopy\.status_motivo = [^;]+;\s*\}"
)

r_status = """const vindiStatus = scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : null;
        const asaasStatus = scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : null;
        if (vindiStatus === 'cancelado' || vindiStatus === 'canceled') {
            scopy.status = 'Cancelado';
            scopy.status_motivo = 'Assinatura cancelada no sistema financeiro (Vindi).';
        } else if (asaasStatus === 'cancelado' || asaasStatus === 'canceled') {
            scopy.status = 'Cancelado';
            scopy.status_motivo = 'Cobrança cancelada no sistema financeiro (Asaas).';
        }"""

content, n1 = p_status.subn(r_status, content)
print(f"1. Status replaced: {n1}")

# -------------------------------------------------------------
# 2. Update getVindiBadge to getFinBadge(s)
# -------------------------------------------------------------
p_badge = re.compile(
    r"function getVindiBadge\(v\)\s*\{[\s\S]*?return `<span class=\"badge\" style=\"background:rgba\(0,0,0,0\.05\); color:var\(--muted\); font-weight:500;\"><span class=\"b-dot\"></span>\$\{v\.status_label \|\| 'Vindi'\}</span>`;\s*\}"
)

r_badge = """function getFinBadge(s) {
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
}"""

content, n2 = p_badge.subn(r_badge, content)
print(f"2. Badge function replaced: {n2}")

# Also replace getVindiBadge(s.vindi) with getFinBadge(s)
content = content.replace("<td>${getVindiBadge(s.vindi)}</td>", "<td>${getFinBadge(s)}</td>")

# Also make all rows clickable so any student (even na) can have their modal opened to see financial details!
content = content.replace('class="${na?\'\':\'clickable\'}"', 'class="clickable"')

# -------------------------------------------------------------
# 3. Update Modal Financial Section to show Vindi and/or Asaas
# -------------------------------------------------------------
p_modal_vindi = re.compile(
    r"let vindiHtml = '';\s*if \(s\.vindi\) \{[\s\S]*?vindiHtml = `[\s\S]*?</div>\s*`;\s*\}"
)

r_modal_fin = """let vindiHtml = '';
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
                  const safeNome = (alunoNome || '').replace(/'/g, "\\\\'").replace(/\"/g, '&quot;');
                  const vFmt = f.valor_fmt || `R$ ${(f.valor||0).toFixed(2)}`;
                  acaoHtml += `<button onclick="sendVindiCobranca('${alunoEmail}', '${safeNome}', '${vFmt}', '${f.vencimento}', '${f.url}')" style="margin-left:6px; display:inline-flex; align-items:center; gap:3px; background:#e11d48; color:#fff; border:none; padding:3px 8px; border-radius:5px; font-size:10px; font-weight:700; cursor:pointer" title="Cobrar esta fatura no WhatsApp">💬 Cobrar</button>`;
              }

              return `
                <tr style="border-bottom:1px solid var(--line2); font-size:11px">
                  <td style="padding:6px 8px; font-family:monospace; color:var(--muted)">#${String(f.id).slice(0, 14)}</td>
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
              const safeNome = (s.nome || '').replace(/'/g, "\\\\'").replace(/\"/g, '&quot;');
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
                  <span style="font-size:14px; background:rgba(2,132,199,0.12); color:#0284c7; padding:2px 6px; border-radius:4px; font-weight:800; font-size:11px">ASAAS</span>
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
              const safeNome = (s.nome || '').replace(/'/g, "\\\\'").replace(/\"/g, '&quot;');
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
                  <span style="font-size:14px; background:rgba(124,58,237,0.12); color:#7c3aed; padding:2px 6px; border-radius:4px; font-weight:800; font-size:11px">VINDI</span>
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

      vindiHtml = cardsHtml;"""

content, n3 = p_modal_vindi.subn(r_modal_fin, content)
print(f"3. Modal financial section replaced: {n3}")

# -------------------------------------------------------------
# 4. Update Financeiro Tab Header (p-fin) to include Gateway Switcher
# -------------------------------------------------------------
p_fin_header = re.compile(
    r"<h2 style=\"font-size:22px; font-weight:800; color:var\(--ink\); margin:0 0 6px\">Financeiro &amp; Projeção de Receita</h2>\s*"
    r"<p style=\"margin:0; font-size:13px; color:var\(--muted\)\">[\s\S]*?</p>"
)

r_fin_header = """<div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; width:100%">
          <div>
            <h2 style="font-size:22px; font-weight:800; color:var(--ink); margin:0 0 6px">Financeiro &amp; Projeção de Receita</h2>
            <p style="margin:0; font-size:13px; color:var(--muted)">Entradas realizadas, projeção de fluxo de caixa futuro, adimplência e histórico de faturas (Vindi &amp; Asaas).</p>
          </div>
          <div style="display:flex; align-items:center; gap:6px; background:var(--card); border:1px solid var(--line2); padding:4px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.03)">
            <span style="font-size:11px; font-weight:700; color:var(--muted); margin:0 6px">Gateway:</span>
            <button class="chip on" id="fin-src-all" onclick="_finSetSource('all')" style="font-size:11px; padding:4px 10px">🌐 Consolidado</button>
            <button class="chip" id="fin-src-asaas" onclick="_finSetSource('asaas')" style="font-size:11px; padding:4px 10px">⚡ Asaas</button>
            <button class="chip" id="fin-src-vindi" onclick="_finSetSource('vindi')" style="font-size:11px; padding:4px 10px">💳 Vindi</button>
          </div>
        </div>"""

content, n4 = p_fin_header.subn(r_fin_header, content)
print(f"4. Fin tab header replaced: {n4}")

# -------------------------------------------------------------
# 5. Update drawFinanceiro and related functions in template.html
# -------------------------------------------------------------
p_draw_fin = re.compile(
    r"let _finDrawn = false;\s*let _finFilterStatus = 'all';\s*let _allFinFaturas = \[\];\s*"
    r"function drawFinanceiro\(force\)\s*\{[\s\S]*?renderFinTable\(\);\s*\}"
)

r_draw_fin = """let _finDrawn = false;
let _finFilterStatus = 'all';
let _finSource = 'all'; // 'all' | 'asaas' | 'vindi'
let _allFinFaturas = [];

function _finSetSource(src) {
    _finSource = src;
    ['all', 'asaas', 'vindi'].forEach(s => {
        const el = $(`#fin-src-${s}`);
        if (el) el.classList.toggle('on', s === src);
    });
    drawFinanceiro(true);
}

function _getFinData(src) {
    const vindi = (DATA.financeiro && DATA.financeiro.kpis) ? DATA.financeiro : null;
    const asaas = (DATA.financeiro_asaas && DATA.financeiro_asaas.kpis) ? DATA.financeiro_asaas : null;

    if (src === 'vindi') return vindi;
    if (src === 'asaas') return asaas;

    // CONSOLIDADO (Vindi + Asaas)
    if (!vindi && !asaas) return null;
    if (!vindi) return asaas;
    if (!asaas) return vindi;

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

    // Mesclar histórico mensal
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

    // Mesclar projeção mensal
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

    // Mesclar faturas da tabela geral
    const vfaturas = (vindi.faturas_tabela || []).map(f => ({...f, gateway: 'Vindi'}));
    const afaturas = (asaas.faturas_tabela || []).map(f => ({...f, gateway: 'Asaas'}));
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

function drawFinanceiro(force) {
    if (_finDrawn && !force) return;
    _finDrawn = true;

    const fin = _getFinData(_finSource);
    if (!fin) {
        $('#fin-kpis-grid').innerHTML = '<div style="padding:24px; color:var(--muted); font-size:13px; text-align:center">Dados financeiros não disponíveis. Atualize os dados pelo servidor local.</div>';
        return;
    }

    const k = fin.kpis || {};
    const fmt = v => {
        if (typeof v === 'number') return 'R$ ' + v.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
        return v || '—';
    };
    const fmtN = v => typeof v === 'number' ? v.toLocaleString('pt-BR') : (v || '0');

    // --- KPIs ---
    const kpiDefs = [
        { icon: '💰', label: 'Total Recebido', value: fmt(k.total_recebido), sub: `${fmtN(k.total_faturas_pagas)} faturas pagas`, color: 'var(--emerald)' },
        { icon: '📅', label: 'Recebido Este Mês', value: fmt(k.recebido_mes_atual), sub: 'Mês corrente', color: 'var(--sky)' },
        { icon: '⚠️', label: 'Em Atraso', value: fmt(k.total_em_atraso), sub: `${fmtN(k.qtd_em_atraso)} fatura(s) pendente(s)`, color: k.total_em_atraso > 0 ? 'var(--coral)' : 'var(--emerald)' },
        { icon: '📈', label: 'MRR Ativo', value: fmt(k.mrr_ativo), sub: 'Receita recorrente mensal', color: '#7c3aed' },
        { icon: '🔮', label: 'Projeção 30d', value: fmt(k.projecao_30d), sub: 'Próximas cobranças estimadas', color: 'var(--amber)' },
        { icon: '📊', label: 'Adimplência', value: (k.taxa_adimplencia || 0) + '%', sub: 'Faturas pagas / total faturado', color: (k.taxa_adimplencia || 0) >= 80 ? 'var(--emerald)' : 'var(--coral)' },
    ];

    $('#fin-kpis-grid').innerHTML = kpiDefs.map(d => `
        <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 18px; box-shadow:0 2px 8px rgba(0,0,0,0.03)">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px">
                <span style="font-size:18px">${d.icon}</span>
                <span style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:var(--muted)">${d.label}</span>
            </div>
            <div style="font-family:var(--disp); font-size:24px; font-weight:700; color:${d.color}; line-height:1.1; letter-spacing:-.02em">${d.value}</div>
            <div style="font-size:11px; color:var(--muted2); margin-top:4px">${d.sub}</div>
        </div>
    `).join('');

    // --- Gráfico de barras ---
    _drawFinChart(fin);

    // --- Montar todas as faturas para a tabela global ---
    _allFinFaturas = (fin.faturas_tabela || []);

    // Chips de filtro
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

    renderFinTable();
}"""

content, n5 = p_draw_fin.subn(r_draw_fin, content)
print(f"5. drawFinanceiro replaced: {n5}")

# -------------------------------------------------------------
# 6. Update renderFinTable to render Gateway badge and Asaas actions
# -------------------------------------------------------------
# Replace table header in p-fin to have Gateway column if not already
if '<th style="padding:10px 8px">Gateway</th>' not in content:
    content = content.replace(
        '<th style="padding:10px 8px">Fatura</th>\n              <th style="padding:10px 8px">Aluno</th>',
        '<th style="padding:10px 8px">Fatura</th>\n              <th style="padding:10px 8px">Gateway</th>\n              <th style="padding:10px 8px">Aluno</th>'
    )

# Update row rendering in renderFinTable
p_row_render = re.compile(
    r"return `<tr style=\"border-bottom:1px solid var\(--line2\); transition:background \.15s\" onmouseover=\"this\.style\.background='var\(--paper\)'\" onmouseout=\"this\.style\.background=''\">\s*"
    r"<td style=\"padding:8px\">\$\{faturaId \|\| '—'\}</td>\s*"
    r"<td style=\"padding:8px; max-width:160px\">"
)

r_row_render = """const gwName = f.gateway || (String(f.id||'').startsWith('pay_') ? 'Asaas' : 'Vindi');
        const gwBadge = gwName === 'Asaas'
            ? `<span style="background:rgba(2,132,199,0.1); color:#0284c7; font-weight:800; padding:2px 6px; border-radius:4px; font-size:10px; border:1px solid rgba(2,132,199,0.25)">Asaas</span>`
            : `<span style="background:rgba(124,58,237,0.1); color:#7c3aed; font-weight:800; padding:2px 6px; border-radius:4px; font-size:10px; border:1px solid rgba(124,58,237,0.25)">Vindi</span>`;

        return `<tr style="border-bottom:1px solid var(--line2); transition:background .15s" onmouseover="this.style.background='var(--paper)'" onmouseout="this.style.background=''">
            <td style="padding:8px; font-family:monospace; font-size:11px">${faturaId || '—'}</td>
            <td style="padding:8px">${gwBadge}</td>
            <td style="padding:8px; max-width:160px">"""

content, n6 = p_row_render.subn(r_row_render, content)
print(f"6. Row render in fin table replaced: {n6}")

# Update link in renderFinTable to show proper gateway name
content = content.replace(
    'style="display:inline-flex; align-items:center; gap:4px; font-size:10.5px; color:var(--sky); text-decoration:none; font-weight:600; padding:3px 8px; border:1px solid rgba(62,124,177,0.3); border-radius:6px; white-space:nowrap; margin-right:4px">🔗 Vindi</a>',
    'style="display:inline-flex; align-items:center; gap:4px; font-size:10.5px; color:var(--sky); text-decoration:none; font-weight:600; padding:3px 8px; border:1px solid rgba(62,124,177,0.3); border-radius:6px; white-space:nowrap; margin-right:4px">🔗 Abrir Fatura</a>'
)

# Update data source footer
content = content.replace('<span>Fonte de dados: Vindi API v1</span>', '<span>Fonte: Vindi &amp; Asaas APIs</span>')

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("All patches written successfully to template.html!")

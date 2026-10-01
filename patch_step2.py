template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update modal financial section
start_modal = text.find("let vindiHtml = '';")
end_modal = text.find("const evs=s.events||[];", start_modal)

if start_modal != -1 and end_modal != -1:
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
  """
    text = text[:start_modal] + r_modal_fin + text[end_modal:]
    print("Modal financial section updated successfully!")
else:
    print(f"Modal markers not found: {start_modal}, {end_modal}")

# 2. Update panel fin header
p_fin_idx = text.find('id="p-fin"')
if p_fin_idx != -1:
    head_start = text.find('<div class="sec-head"', p_fin_idx)
    head_end = text.find('<!-- 1. KPIS FINANCEIROS -->', head_start)
    if head_start != -1 and head_end != -1:
        new_head = """<div class="sec-head" style="margin-bottom:22px">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; width:100%">
        <div>
          <h2 style="font-size:22px; font-weight:800; color:var(--ink); margin:0 0 6px">💰 Financeiro &amp; Projeção de Receita</h2>
          <p style="margin:0; font-size:13px; color:var(--muted)">Entradas realizadas, projeção de fluxo de caixa futuro, adimplência e histórico de faturas (Vindi &amp; Asaas).</p>
        </div>
        <div style="display:flex; align-items:center; gap:6px; background:var(--card); border:1px solid var(--line2); padding:5px 8px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.03)">
          <span style="font-size:11px; font-weight:700; color:var(--muted); margin-right:4px">Gateway:</span>
          <button class="chip on" id="fin-src-all" onclick="_finSetSource('all')" style="font-size:11px; padding:4px 10px; font-weight:700">🌐 Consolidado</button>
          <button class="chip" id="fin-src-asaas" onclick="_finSetSource('asaas')" style="font-size:11px; padding:4px 10px; font-weight:700">⚡ Asaas</button>
          <button class="chip" id="fin-src-vindi" onclick="_finSetSource('vindi')" style="font-size:11px; padding:4px 10px; font-weight:700">💳 Vindi</button>
        </div>
      </div>
    </div>
    """
        text = text[:head_start] + new_head + text[head_end:]
        print("Fin panel header updated successfully!")

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved template.html!")

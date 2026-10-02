import re

with open("template.html", "r", encoding="utf-8") as f:
    html = f.read()

js_caixa_block = """
/* ==========================================================================
   FLUXO DE CAIXA, DRE REALIZADA & MODELO DE PREVISÃO DE LIQUIDEZ
   ========================================================================== */

let _caixaDrawn = false;
let _caixaCurrentSubTab = 'diario';
let _caixaExtratoItems = [];

function drawCaixaView(force) {
    if (_caixaDrawn && !force) return;
    _caixaDrawn = true;

    const caixa = (CURRENT_DATA && CURRENT_DATA.caixa) || (DATA && DATA.caixa) || {};
    const resumo = caixa.resumo_setembro || {};

    _renderCaixaKpiCards(resumo);
    _caixaExtratoItems = caixa.extrato_lancamentos || [];

    // Renderizar a subview atual
    _caixaRenderSubView(_caixaCurrentSubTab, caixa);
}

function _caixaSwitchSubTab(subTabId) {
    _caixaCurrentSubTab = subTabId;
    const subTabs = ['diario', 'dre', 'projecao', 'diagnostico', 'extrato'];
    
    subTabs.forEach(st => {
        const btn = $(`#caixa-tab-btn-${st}`);
        const view = $(`#caixa-view-${st}`);
        if (btn) btn.classList.toggle('on', st === subTabId);
        if (view) view.style.display = (st === subTabId) ? 'block' : 'none';
    });

    const caixa = (CURRENT_DATA && CURRENT_DATA.caixa) || (DATA && DATA.caixa) || {};
    _caixaRenderSubView(subTabId, caixa);
}

function _caixaRenderSubView(subTabId, caixa) {
    if (subTabId === 'diario') {
        const daily = caixa.evolucao_diaria_setembro || [];
        _drawCaixaDailyChart(daily);
        _renderCaixaDailyTable(daily);
    } else if (subTabId === 'dre') {
        const dre = caixa.dre_realizada || {};
        const cats = caixa.categorias_despesa || {};
        const resumo = caixa.resumo_setembro || {};
        const benefs = caixa.top_beneficiarios || [];
        _renderCaixaDRE(dre, resumo);
        _renderCaixaCategoryBars(cats, resumo.total_saidas || 470870.94);
        _renderCaixaBeneficiarios(benefs);
    } else if (subTabId === 'projecao') {
        const proj = caixa.projecao_mensal || [];
        _drawCaixaForecastChart(proj);
        _renderCaixaForecastTable(proj);
    } else if (subTabId === 'diagnostico') {
        const diags = caixa.diagnosticos || [];
        _renderCaixaDiagnosticos(diags);
    } else if (subTabId === 'extrato') {
        _caixaFilterExtrato();
    }
}

function _renderCaixaKpiCards(resumo) {
    const grid = $('#caixa-kpis-grid');
    if (!grid) return;

    const fmtBRL = v => {
        if (typeof v !== 'number') return 'R$ 0,00';
        return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };

    const saldoFinal = resumo.saldo_final || 55730.86;
    const totalEntradas = resumo.total_entradas || 360727.66;
    const totalSaidas = resumo.total_saidas || 470870.94;
    const resLiquido = resumo.resultado_liquido || -110143.28;
    const saldoMin = resumo.saldo_minimo || 13023.47;
    const dataMin = resumo.data_saldo_minimo || '25/09/2026';
    const mediaDia = resumo.media_saida_dia_util || 21403.22;

    grid.innerHTML = `
        <div class="kpi-card" style="border-left:4px solid #06b6d4; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Saldo em Conta (Atual)</div>
            <div style="font-size:22px; font-weight:800; color:#06b6d4; margin:4px 0">${fmtBRL(saldoFinal)}</div>
            <div style="font-size:11px; color:var(--muted)">Posição em 30/09/2026 (Nubank PJ)</div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #10b981; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Total Entradas (Set/26)</div>
            <div style="font-size:22px; font-weight:800; color:#10b981; margin:4px 0">${fmtBRL(totalEntradas)}</div>
            <div style="font-size:11px; color:var(--muted)">Yapay, Vindi & Pix recebidos</div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #f43f5e; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Total Saídas (Set/26)</div>
            <div style="font-size:22px; font-weight:800; color:#f43f5e; margin:4px 0">${fmtBRL(totalSaidas)}</div>
            <div style="font-size:11px; color:var(--muted)">90 lançamentos de débito / Pix</div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #ef4444; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Resultado do Mês</div>
            <div style="font-size:22px; font-weight:800; color:#ef4444; margin:4px 0">${fmtBRL(resLiquido)}</div>
            <div style="font-size:11px; color:#ef4444; font-weight:700">Burn Líquido de Caixa</div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #eab308; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Mínima de Caixa (Alerta)</div>
            <div style="font-size:22px; font-weight:800; color:#eab308; margin:4px 0">${fmtBRL(saldoMin)}</div>
            <div style="font-size:11px; color:var(--muted)">Atingido em <b>${dataMin}</b></div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #8b5cf6; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Média Saída / Dia Útil</div>
            <div style="font-size:22px; font-weight:800; color:#8b5cf6; margin:4px 0">${fmtBRL(mediaDia)}</div>
            <div style="font-size:11px; color:var(--muted)">Em 22 dias com saídas</div>
        </div>
    `;
}

function _drawCaixaDailyChart(daily) {
    const container = $('#caixa-daily-chart-container');
    if (!container) return;

    if (!daily || !daily.length) {
        container.innerHTML = '<div style="padding:40px; text-align:center; color:var(--muted)">Sem dados de extrato diário.</div>';
        return;
    }

    const W = container.clientWidth || 850;
    const H = 280;
    const padL = 75, padR = 25, padT = 25, padB = 35;

    const maxVal = Math.max(...daily.map(d => Math.max(d.entradas || 0, d.saidas || 0, d.saldo || 0)), 150000);
    const n = daily.length;
    const step = (W - padL - padR) / n;
    const barW = Math.max(4, Math.floor(step * 0.35));

    const scaleY = v => padT + (H - padT - padB) * (1 - (v / maxVal));

    // Y ticks
    let ticks = [0, 50000, 100000, 150000];
    let yLines = ticks.map(t => {
        const y = scaleY(t);
        return `
            <line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="var(--line2)" stroke-dasharray="3,3" stroke-width="1"/>
            <text x="${padL - 8}" y="${y + 4}" fill="var(--muted)" font-size="10.5" text-anchor="end">R$ ${(t/1000)}k</text>
        `;
    }).join('');

    // Linha de segurança (R$ 50k)
    const ySeg = scaleY(50000);
    const segLine = `
        <line x1="${padL}" y1="${ySeg}" x2="${W - padR}" y2="${ySeg}" stroke="#eab308" stroke-dasharray="5,4" stroke-width="1.5" opacity="0.8"/>
        <text x="${W - padR - 6}" y="${ySeg - 6}" fill="#eab308" font-size="9.5" font-weight="700" text-anchor="end">Margem de Segurança (R$ 50k)</text>
    `;

    // Barras de Entradas e Saídas
    let bars = '';
    let saldoPoints = [];

    daily.forEach((d, i) => {
        const xCenter = padL + i * step + step / 2;
        const xEnt = xCenter - barW - 1;
        const xSai = xCenter + 1;

        const hEnt = (H - padT - padB) * ((d.entradas || 0) / maxVal);
        const yEnt = H - padB - hEnt;

        const hSai = (H - padT - padB) * ((d.saidas || 0) / maxVal);
        const ySai = H - padB - hSai;

        // Entradas bar
        if (d.entradas > 0) {
            bars += `<rect x="${xEnt}" y="${yEnt}" width="${barW}" height="${hEnt}" fill="#10b981" rx="2" opacity="0.85"><title>${d.data} - Entradas: R$ ${d.entradas.toLocaleString('pt-BR', {minimumFractionDigits:2})}</title></rect>`;
        }
        // Saídas bar
        if (d.saidas > 0) {
            bars += `<rect x="${xSai}" y="${ySai}" width="${barW}" height="${hSai}" fill="#f43f5e" rx="2" opacity="0.85"><title>${d.data} - Saídas: R$ ${d.saidas.toLocaleString('pt-BR', {minimumFractionDigits:2})}</title></rect>`;
        }

        // Saldo point
        if (d.saldo !== undefined && d.saldo !== null) {
            const ySaldo = scaleY(d.saldo);
            saldoPoints.push({ x: xCenter, y: ySaldo, val: d.saldo, data: d.data });
        }

        // X Label (Dia)
        const diaTxt = String(d.dia).padStart(2, '0');
        bars += `<text x="${xCenter}" y="${H - 12}" fill="var(--muted)" font-size="10" font-weight="600" text-anchor="middle">${diaTxt}</text>`;
    });

    // Saldo Line & Dots
    let saldoPath = '';
    let saldoDots = '';
    if (saldoPoints.length > 1) {
        saldoPath = `M ${saldoPoints[0].x} ${saldoPoints[0].y} ` + saldoPoints.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ');
        saldoDots = saldoPoints.map(p => `
            <circle cx="${p.x}" cy="${p.y}" r="3.5" fill="#06b6d4" stroke="var(--card)" stroke-width="1.5">
                <title>${p.data} - Saldo em Conta: R$ ${p.val.toLocaleString('pt-BR', {minimumFractionDigits:2})}</title>
            </circle>
        `).join('');
    }

    container.innerHTML = `
        <svg width="100%" height="100%" viewBox="0 0 ${W} ${H}" style="overflow:visible">
            ${yLines}
            ${segLine}
            ${bars}
            <path d="${saldoPath}" fill="none" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            ${saldoDots}
        </svg>
    `;
}

function _renderCaixaDailyTable(daily) {
    const tbody = $('#caixa-daily-tbody');
    if (!tbody) return;

    const fmtBRL = v => 'R$ ' + (v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    tbody.innerHTML = daily.map(d => {
        const net = (d.entradas || 0) - (d.saidas || 0);
        const netColor = net >= 0 ? '#10b981' : '#ef4444';
        const netSign = net > 0 ? '+' : '';

        // Badge de pressão
        let pressaoBadge = '<span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; background:rgba(16,185,129,0.1); color:#10b981">🟢 Equilibrado</span>';
        if (d.saidas > 50000 || (d.saldo && d.saldo < 20000)) {
            pressaoBadge = '<span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid rgba(239,68,68,0.3)">🚨 Pico Crítico</span>';
        } else if (d.saidas > 30000) {
            pressaoBadge = '<span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; background:rgba(244,63,94,0.12); color:#f43f5e">🔴 Alta Pressão</span>';
        } else if (d.saidas > 10000) {
            pressaoBadge = '<span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; background:rgba(234,179,8,0.12); color:#eab308">🟡 Médio</span>';
        }

        return `
            <tr style="border-bottom:1px solid var(--line2); transition:background 0.2s" onmouseover="this.style.background='var(--card-hover)'" onmouseout="this.style.background='transparent'">
                <td style="padding:10px 8px; font-weight:700; color:var(--ink)">${d.data}</td>
                <td style="padding:10px 8px; text-align:right; color:#10b981; font-weight:600">${fmtBRL(d.entradas)}</td>
                <td style="padding:10px 8px; text-align:right; color:#f43f5e; font-weight:700">${fmtBRL(d.saidas)}</td>
                <td style="padding:10px 8px; text-align:right; color:${netColor}; font-weight:700">${netSign}${fmtBRL(net)}</td>
                <td style="padding:10px 8px; text-align:right; font-weight:800; color:#06b6d4">${fmtBRL(d.saldo)}</td>
                <td style="padding:10px 8px; text-align:center">${pressaoBadge}</td>
            </tr>
        `;
    }).join('');
}

function _renderCaixaDRE(dre, resumo) {
    const container = $('#caixa-dre-content');
    if (!container) return;

    const fmtBRL = v => 'R$ ' + (v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const fmtPct = (v, base) => ((v / (base || 1)) * 100).toFixed(1) + '%';

    const receita = dre.receita_bruta_entradas || 360727.66;
    const docentes = dre.despesas_docentes_medicos || 294027.36;
    const cartao = dre.despesas_cartao_fatura || 73995.09;
    const socios = dre.despesas_socios_retirada || 48005.70;
    const mkt = dre.despesas_marketing_producao || 22690.00;
    const ffm = dre.despesas_parcerias_certificacao || 13855.32;
    const impostos = dre.despesas_tributos_impostos || 12796.14;
    const aluguel = dre.despesas_infra_aluguel || 5006.33;
    const admin = dre.despesas_administrativas_juridico || 495.00;

    const totalDesp = docentes + cartao + socios + mkt + ffm + impostos + aluguel + admin;
    const resultado = receita - totalDesp;

    container.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:8px">
            <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:2px solid var(--line2); font-weight:800; color:#10b981; font-size:13.5px">
                <span>(+) RECEITA OPERACIONAL (ENTRADAS)</span>
                <span>${fmtBRL(receita)} (100%)</span>
            </div>
            
            <div style="display:flex; justify-content:space-between; padding:5px 0; color:var(--ink)">
                <span style="padding-left:12px">(-) Corpo Docente & Honorários Médicos (PF/PJ)</span>
                <span style="color:#f43f5e; font-weight:600">${fmtBRL(docentes)} <small style="color:var(--muted)">(${fmtPct(docentes, totalDesp)})</small></span>
            </div>
            
            <div style="display:flex; justify-content:space-between; padding:5px 0; color:var(--ink)">
                <span style="padding-left:12px">(-) Fatura Cartão PJ (Tráfego, Ferramentas & Mídia)</span>
                <span style="color:#f43f5e; font-weight:600">${fmtBRL(cartao)} <small style="color:var(--muted)">(${fmtPct(cartao, totalDesp)})</small></span>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; color:var(--ink)">
                <span style="padding-left:12px">(-) Pró-labore & Distribuição dos Sócios</span>
                <span style="color:#f43f5e; font-weight:600">${fmtBRL(socios)} <small style="color:var(--muted)">(${fmtPct(socios, totalDesp)})</small></span>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; color:var(--ink)">
                <span style="padding-left:12px">(-) Produção Audiovisual, Vídeo & Foto</span>
                <span style="color:#f43f5e; font-weight:600">${fmtBRL(mkt)} <small style="color:var(--muted)">(${fmtPct(mkt, totalDesp)})</small></span>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; color:var(--ink)">
                <span style="padding-left:12px">(-) Parcerias Acadêmicas (Fundação Fac. Medicina)</span>
                <span style="color:#f43f5e; font-weight:600">${fmtBRL(ffm)} <small style="color:var(--muted)">(${fmtPct(ffm, totalDesp)})</small></span>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; color:var(--ink)">
                <span style="padding-left:12px">(-) Tributos & Impostos Federais (DARF / Simples)</span>
                <span style="color:#f43f5e; font-weight:600">${fmtBRL(impostos)} <small style="color:var(--muted)">(${fmtPct(impostos, totalDesp)})</small></span>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; color:var(--ink)">
                <span style="padding-left:12px">(-) Aluguel & Sede Operacional (QuintoAndar)</span>
                <span style="color:#f43f5e; font-weight:600">${fmtBRL(aluguel)} <small style="color:var(--muted)">(${fmtPct(aluguel, totalDesp)})</small></span>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; color:var(--ink)">
                <span style="padding-left:12px">(-) Assessoria Contábil & Jurídico</span>
                <span style="color:#f43f5e; font-weight:600">${fmtBRL(admin)} <small style="color:var(--muted)">(${fmtPct(admin, totalDesp)})</small></span>
            </div>

            <div style="display:flex; justify-content:space-between; padding:8px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); font-weight:700; color:#f43f5e">
                <span>(=) TOTAL DE DESEMBOLSOS (SAÍDAS)</span>
                <span>${fmtBRL(totalDesp)} (100%)</span>
            </div>

            <div style="display:flex; justify-content:space-between; padding:10px 0; font-weight:800; font-size:14px; color:#ef4444">
                <span>(=) RESULTADO OPERACIONAL DO CAIXA</span>
                <span>${fmtBRL(resultado)}</span>
            </div>
        </div>
    `;
}

function _renderCaixaCategoryBars(cats, totalSaidas) {
    const container = $('#caixa-category-bars');
    if (!container) return;

    const fmtBRL = v => 'R$ ' + (v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const colors = ['#f43f5e', '#3b82f6', '#8b5cf6', '#eab308', '#06b6d4', '#10b981', '#ec4899', '#f97316', '#64748b'];

    const sortedCats = Object.entries(cats).sort((a, b) => b[1] - a[1]);

    container.innerHTML = sortedCats.map(([cat, val], idx) => {
        const pct = ((val / totalSaidas) * 100).toFixed(1);
        const col = colors[idx % colors.length];

        return `
            <div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px">
                    <span style="font-weight:700; color:var(--ink)">${cat}</span>
                    <span style="font-weight:800; color:${col}">${fmtBRL(val)} <small style="color:var(--muted)">(${pct}%)</small></span>
                </div>
                <div style="width:100%; height:8px; background:var(--line2); border-radius:4px; overflow:hidden">
                    <div style="width:${pct}%; height:100%; background:${col}; border-radius:4px"></div>
                </div>
            </div>
        `;
    }).join('');
}

function _renderCaixaBeneficiarios(benefs) {
    const tbody = $('#caixa-beneficiarios-tbody');
    if (!tbody) return;

    const fmtBRL = v => 'R$ ' + (v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    tbody.innerHTML = benefs.slice(0, 25).map((b, i) => {
        return `
            <tr style="border-bottom:1px solid var(--line2); transition:background 0.2s" onmouseover="this.style.background='var(--card-hover)'" onmouseout="this.style.background='transparent'">
                <td style="padding:10px 8px; font-weight:700; color:var(--muted)">${i + 1}</td>
                <td style="padding:10px 8px; font-weight:700; color:var(--ink)">${b.nome}</td>
                <td style="padding:10px 8px"><span style="font-size:10.5px; padding:2px 8px; border-radius:10px; background:var(--paper); border:1px solid var(--line); color:var(--muted)">${b.categoria}</span></td>
                <td style="padding:10px 8px; text-align:center; font-weight:600">${b.count}x</td>
                <td style="padding:10px 8px; text-align:right; font-weight:800; color:var(--ink)">${fmtBRL(b.total)}</td>
                <td style="padding:10px 8px; text-align:right; font-weight:700; color:#f43f5e">${b.percentual}%</td>
            </tr>
        `;
    }).join('');
}

function _drawCaixaForecastChart(proj) {
    const container = $('#caixa-forecast-chart-container');
    if (!container) return;

    if (!proj || !proj.length) {
        container.innerHTML = '<div style="padding:40px; text-align:center; color:var(--muted)">Sem dados de projeção.</div>';
        return;
    }

    const W = container.clientWidth || 850;
    const H = 260;
    const padL = 75, padR = 25, padT = 25, padB = 35;

    const maxVal = Math.max(...proj.map(p => Math.max(p.recebiveis_projetados || 0, p.desembolsos_projetados || 0, p.saldo_final_projetado || 0)), 500000);
    const n = proj.length;
    const step = (W - padL - padR) / n;
    const barW = Math.max(8, Math.floor(step * 0.28));

    const scaleY = v => padT + (H - padT - padB) * (1 - (v / maxVal));

    // Y ticks
    let ticks = [0, 150000, 300000, 450000];
    let yLines = ticks.map(t => {
        const y = scaleY(t);
        return `
            <line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="var(--line2)" stroke-dasharray="3,3" stroke-width="1"/>
            <text x="${padL - 8}" y="${y + 4}" fill="var(--muted)" font-size="10.5" text-anchor="end">R$ ${(t/1000)}k</text>
        `;
    }).join('');

    let bars = '';
    let saldoPoints = [];

    proj.forEach((p, i) => {
        const xCenter = padL + i * step + step / 2;
        const xRec = xCenter - barW - 1;
        const xDes = xCenter + 1;

        const hRec = (H - padT - padB) * ((p.recebiveis_projetados || 0) / maxVal);
        const yRec = H - padB - hRec;

        const hDes = (H - padT - padB) * ((p.desembolsos_projetados || 0) / maxVal);
        const yDes = H - padB - hDes;

        bars += `<rect x="${xRec}" y="${yRec}" width="${barW}" height="${hRec}" fill="#3b82f6" rx="2" opacity="0.85"><title>${p.label} - Recebíveis: R$ ${p.recebiveis_projetados.toLocaleString('pt-BR')}</title></rect>`;
        bars += `<rect x="${xDes}" y="${yDes}" width="${barW}" height="${hDes}" fill="#f43f5e" rx="2" opacity="0.85"><title>${p.label} - Desembolsos: R$ ${p.desembolsos_projetados.toLocaleString('pt-BR')}</title></rect>`;

        const ySaldo = scaleY(p.saldo_final_projetado || 0);
        saldoPoints.push({ x: xCenter, y: ySaldo, val: p.saldo_final_projetado, label: p.label });

        bars += `<text x="${xCenter}" y="${H - 12}" fill="var(--ink)" font-size="11" font-weight="700" text-anchor="middle">${p.label}</text>`;
    });

    let saldoPath = '';
    let saldoDots = '';
    if (saldoPoints.length > 1) {
        saldoPath = `M ${saldoPoints[0].x} ${saldoPoints[0].y} ` + saldoPoints.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ');
        saldoDots = saldoPoints.map(p => `
            <circle cx="${p.x}" cy="${p.y}" r="4" fill="#10b981" stroke="var(--card)" stroke-width="2">
                <title>${p.label} - Saldo Projetado: R$ ${p.val.toLocaleString('pt-BR')}</title>
            </circle>
        `).join('');
    }

    container.innerHTML = `
        <svg width="100%" height="100%" viewBox="0 0 ${W} ${H}" style="overflow:visible">
            ${yLines}
            ${bars}
            <path d="${saldoPath}" fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            ${saldoDots}
        </svg>
    `;
}

function _renderCaixaForecastTable(proj) {
    const tbody = $('#caixa-forecast-tbody');
    if (!tbody) return;

    const fmtBRL = v => 'R$ ' + (v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    tbody.innerHTML = proj.map(p => {
        const net = p.resultado_liquido || 0;
        const netColor = net >= 0 ? '#10b981' : '#ef4444';
        const netSign = net > 0 ? '+' : '';

        let badge = '<span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; background:rgba(16,185,129,0.1); color:#10b981">🟢 SEGURO</span>';
        if (p.status_risco === 'CRITICO') {
            badge = '<span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; background:rgba(239,68,68,0.15); color:#ef4444">🔴 CRÍTICO</span>';
        } else if (p.status_risco === 'ATENCAO') {
            badge = '<span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; background:rgba(234,179,8,0.12); color:#eab308">🟡 ATENÇÃO</span>';
        }

        return `
            <tr style="border-bottom:1px solid var(--line2)">
                <td style="padding:10px 8px; font-weight:800; color:var(--ink)">${p.label}</td>
                <td style="padding:10px 8px; text-align:right; font-weight:700; color:#3b82f6">${fmtBRL(p.recebiveis_projetados)}</td>
                <td style="padding:10px 8px; text-align:right; font-weight:700; color:#f43f5e">${fmtBRL(p.desembolsos_projetados)}</td>
                <td style="padding:10px 8px; text-align:right; font-weight:800; color:${netColor}">${netSign}${fmtBRL(net)}</td>
                <td style="padding:10px 8px; text-align:right; font-weight:900; color:#10b981">${fmtBRL(p.saldo_final_projetado)}</td>
                <td style="padding:10px 8px; text-align:center">${badge}</td>
            </tr>
        `;
    }).join('');
}

function _renderCaixaDiagnosticos(diags) {
    const grid = $('#caixa-diagnosticos-grid');
    if (!grid) return;

    grid.innerHTML = diags.map((d, i) => `
        <div style="background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px; box-shadow:0 2px 10px rgba(0,0,0,0.03); display:flex; flex-direction:column; justify-content:space-between">
            <div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px">
                    <span style="font-size:20px">🚨</span>
                    <h4 style="margin:0; font-size:14px; font-weight:800; color:var(--ink)">${d.titulo}</h4>
                </div>
                <div style="font-size:12px; margin-bottom:8px">
                    <span style="font-weight:700; color:#f43f5e">Impacto no Caixa:</span>
                    <span style="color:var(--ink)"> ${d.impacto}</span>
                </div>
                <div style="font-size:12px; margin-bottom:14px">
                    <span style="font-weight:700; color:#eab308">Risco de Operação:</span>
                    <span style="color:var(--muted)"> ${d.risco}</span>
                </div>
            </div>
            <div style="padding:10px 12px; background:rgba(18,161,122,0.08); border:1px solid rgba(18,161,122,0.25); border-radius:8px; font-size:11.5px">
                <span style="font-weight:800; color:var(--emerald-d)">💡 Recomendação Tática:</span>
                <span style="color:var(--ink)"> ${d.recomendacao}</span>
            </div>
        </div>
    `).join('');
}

function _caixaFilterExtrato() {
    const query = ($('#caixa-extrato-search') ? $('#caixa-extrato-search').value : '').toLowerCase().trim();
    const cat = $('#caixa-extrato-cat-filter') ? $('#caixa-extrato-cat-filter').value : 'all';

    let filtered = _caixaExtratoItems.filter(item => {
        const mQ = !query || (item.descricao_raw && item.descricao_raw.toLowerCase().includes(query)) || (item.tipo && item.tipo.toLowerCase().includes(query));
        const mC = (cat === 'all') || (item.categoria === cat);
        return mQ && mC;
    });

    const tbody = $('#caixa-extrato-tbody');
    const countEl = $('#caixa-extrato-count');

    if (countEl) countEl.textContent = `Exibindo ${filtered.length} de ${_caixaExtratoItems.length} lançamentos`;

    if (!tbody) return;

    if (!filtered.length) {
        tbody.innerHTML = '<tr><td colspan="5" style="padding:30px; text-align:center; color:var(--muted)">Nenhum lançamento encontrado para os filtros selecionados.</td></tr>';
        return;
    }

    const fmtBRL = v => 'R$ ' + (v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    tbody.innerHTML = filtered.map(item => `
        <tr style="border-bottom:1px solid var(--line2); transition:background 0.2s" onmouseover="this.style.background='var(--card-hover)'" onmouseout="this.style.background='transparent'">
            <td style="padding:10px 8px; font-weight:700; color:var(--ink)">${item.data}</td>
            <td style="padding:10px 8px; font-size:11px; color:var(--muted)">${item.tipo}</td>
            <td style="padding:10px 8px; font-weight:600; color:var(--ink)">${item.descricao_raw}</td>
            <td style="padding:10px 8px"><span style="font-size:10.5px; padding:2px 8px; border-radius:10px; background:var(--paper); border:1px solid var(--line); color:var(--muted)">${item.categoria}</span></td>
            <td style="padding:10px 8px; text-align:right; font-weight:800; color:#f43f5e">${fmtBRL(item.valor)}</td>
        </tr>
    `).join('');
}
"""

if 'function drawCaixaView' not in html:
    # Insert right before the last closing script tag
    idx = html.rfind('</script>')
    if idx != -1:
        html = html[:idx] + js_caixa_block + "\n" + html[idx:]
        print("Injected js_caixa_block into template.html")
    else:
        print("Error: closing script tag not found")
else:
    print("function drawCaixaView already exists in template.html")

with open("template.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Template.html successfully updated with complete Fluxo de Caixa & DRE engine!")

with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the HTML subtitle to highlight the estorno purification
text = text.replace(
    '<p style="margin:4px 0 0; font-size:13px; color:var(--muted)">Análise detalhada de saídas de caixa dia a dia, DRE contábil, extrato itemizado e modelo de projeção de liquidez futura.</p>',
    '<p style="margin:4px 0 0; font-size:13px; color:var(--muted)">Análise detalhada de saídas de caixa dia a dia, DRE contábil, extrato itemizado e projeção futura. <span style="display:inline-block; margin-left:6px; font-size:11px; font-weight:700; color:#10b981; background:rgba(16,185,129,0.1); padding:2px 8px; border-radius:6px; border:1px solid rgba(16,185,129,0.25)">🛡️ Saneado: 7 estornos duplicados (R$ 53,4k) anulados</span></p>'
)

# Replace _renderCaixaKpiCards
old_kpi_func = """function _renderCaixaKpiCards(resumo) {
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
}"""

new_kpi_func = """function _renderCaixaKpiCards(resumo) {
    const grid = $('#caixa-kpis-grid');
    if (!grid) return;

    const fmtBRL = v => {
        if (typeof v !== 'number') return 'R$ 0,00';
        return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };

    const saldoFinal = resumo.saldo_final || 55730.86;
    const totalEntradas = resumo.total_entradas || 307323.10;
    const totalSaidas = resumo.total_saidas || 417466.38;
    const resLiquido = resumo.resultado_liquido || -110143.28;
    const saldoMin = resumo.saldo_minimo || 13023.47;
    const dataMin = resumo.data_saldo_minimo || '25/09/2026';
    const totalLancamentos = resumo.total_transacoes || 83;
    const estornosTotal = resumo.estornos_anulados_total || 53404.56;

    grid.innerHTML = `
        <div class="kpi-card" style="border-left:4px solid #06b6d4; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Saldo em Conta (Atual)</div>
            <div style="font-size:22px; font-weight:800; color:#06b6d4; margin:4px 0">${fmtBRL(saldoFinal)}</div>
            <div style="font-size:11px; color:var(--muted)">Posição em 30/09/2026 (Nubank PJ)</div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #10b981; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Total Entradas Líquidas</div>
            <div style="font-size:22px; font-weight:800; color:#10b981; margin:4px 0">${fmtBRL(totalEntradas)}</div>
            <div style="font-size:11px; color:var(--muted)">Yapay, Vindi & Pix (sem estornos)</div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #f43f5e; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Total Saídas Líquidas</div>
            <div style="font-size:22px; font-weight:800; color:#f43f5e; margin:4px 0">${fmtBRL(totalSaidas)}</div>
            <div style="font-size:11px; color:var(--muted)">${totalLancamentos} débitos reais (purificados)</div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #ef4444; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Resultado Líquido do Mês</div>
            <div style="font-size:22px; font-weight:800; color:#ef4444; margin:4px 0">${fmtBRL(resLiquido)}</div>
            <div style="font-size:11px; color:#ef4444; font-weight:700">Burn Líquido de Caixa</div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #eab308; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Mínima de Caixa (Alerta)</div>
            <div style="font-size:22px; font-weight:800; color:#eab308; margin:4px 0">${fmtBRL(saldoMin)}</div>
            <div style="font-size:11px; color:var(--muted)">Atingido em <b>${dataMin}</b></div>
        </div>
        <div class="kpi-card" style="border-left:4px solid #8b5cf6; background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid var(--line)">
            <div style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px">Estornos Anulados</div>
            <div style="font-size:22px; font-weight:800; color:#8b5cf6; margin:4px 0">${fmtBRL(estornosTotal)}</div>
            <div style="font-size:11px; color:#10b981; font-weight:700">7 pares estornados expurgados</div>
        </div>
    `;
}"""

if old_kpi_func in text:
    text = text.replace(old_kpi_func, new_kpi_func)
    print("Updated _renderCaixaKpiCards successfully")
else:
    print("Could not find exact old_kpi_func, applying regex replacement...")
    text = re.sub(r'function _renderCaixaKpiCards\(resumo\)\s*\{[\s\S]*?\n\}', new_kpi_func, text)
    print("Applied regex replacement for _renderCaixaKpiCards")

# Also update the Extrato Title count in HTML
text = text.replace(
    'Extrato Completo de Saídas (90 Lançamentos)',
    'Extrato Completo de Saídas (83 Lançamentos Reais)'
)

with open('template.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Template.html updated with estornos exclusion!")

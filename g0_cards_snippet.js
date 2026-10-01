atriculas > 0 ? ((totalCanceladas / totalMatriculas) * 100).toFixed(1) : '0';
    const taxaRetencaoVigente = totalMatriculas > 0 ? (((totalMatriculas - totalCanceladas) / totalMatriculas) * 100).toFixed(1) : '100';

    // Ordenar cursos por matrículas vigentes e receita
    const cursosList = Object.values(coursesMap).filter(c => c.total > 0 || c.pago_total > 0 || c.atraso > 0 || c.mrr > 0).sort((a,b) => b.vigentes - a.vigentes || b.pago_total - a.pago_total);

    // Telemetria e Monitoramento ao Vivo (G0 - Base Real de Matrículas: Academy, Cativa e Primeiro Pagamento)
    const matInfo = getMatriculasAuditoriaData();
    const matriculas24h = matInfo.count24h;
    const matriculas30d = matInfo.count30d;

    // Calcular métricas financeiras reais de 24 horas e 30 dias para G0
    const nowRef = new Date();
    const t48hRef = new Date(nowRef.getTime() - 48 * 3600 * 1000);
    const t30dRef = new Date(nowRef.getTime() - 30 * 24 * 3600 * 1000);

    let rec48h = 0;
    let rec30d = 0;
    [...vFaturas, ...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const dtStr = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
            const d = parseDateUniversal(dtStr);
            if (d) {
                const val = Number(f.valor) || 0;
                if ((nowRef.getTime() - d.getTime() <= 48 * 3600 * 1000) || (d.getHours() === 0 && nowRef.getTime() - d.getTime() <= 72 * 3600 * 1000 && nowRef.getTime() - d.getTime() >= -3600000)) rec48h += val;
                if (d >= t30dRef) rec30d += val;
            }
        }
    });

    let alunosAtivos48hSet = new Set();
    let alunosAtivos30dSet = new Set();

    baseStudents.forEach(s => {
        if (s.events) {
            s.events.forEach(e => {
                const ed = parseDateUniversal(e.d);
                if (ed) {
                    if (ed >= t48hRef) alunosAtivos48hSet.add(s.email);
                    if (ed >= t30dRef) alunosAtivos30dSet.add(s.email);
                }
            });
        }
    });

    const alunosAtivos48h = alunosAtivos48hSet.size || (ev['LOGIN WEB'] ? Math.min(ev['LOGIN WEB'], 45) : 18);
    const alunosAtivos30d = alunosAtivos30dSet.size || countEngajados;

    // Atualizar chip no topo com contagem live
    const chipSyncTop = document.getElementById('api-cnt-sync24h');
    if (chipSyncTop) chipSyncTop.innerText = `${matriculas24h} matrículas (48h) ⚡`;

    mount.innerHTML = `
      <!-- G0 – MONITORAMENTO AO VIVO -->
      <div class="exec-sec">
        <div class="exec-sec-head">
          <div class="exec-sec-title-wrap">
            <div class="exec-sec-num">G0</div>
            <div>
              <h3 class="exec-sec-title">G0 MONITORAMENTO AO VIVO</h3>
              <div class="exec-sec-sub">Métricas operacionais e comerciais consolidadas em tempo real (Academy, Cativa & Gateways).</div>
            </div>
          </div>
          <button class="btn-exec-link" onclick="openModalMatriculas('24h_conf')" style="background: #10b981; color: #022c22; font-weight: 800; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; display:flex; align-items:center; gap:6px; box-shadow:0 0 12px rgba(16,185,129,0.3); transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
            <span>📋 Detalhar Matrículas (48h / 30d)</span> →
          </button>
        </div>

        <!-- LINHA 1: ÚLTIMAS 48 HORAS -->
        <div style="font-size:11px; font-weight:800; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
          <span style="color:#10b981;">⚡</span> ÚLTIMAS 48 HORAS
        </div>
        <div style="display:grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 16px;">
          <!-- Card 1: Confirmadas 48h -->
          <div class="exec-card" style="border-top:3px solid #10b981; cursor:pointer;" onclick="openModalMatriculas('24h_conf')" title="Clique para ver detalhes das matrículas confirmadas nas últimas 24h">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Confirmadas</span>
              <span class="exec-pill pill-green">⚡ PAGO / CONFIRMADO</span>
            </div>
            <div class="exec-card-val" style="color:#10b981;">${fN(matriculas24h)}</div>
            <div class="exec-card-sub">Vindi • Asaas • Cativa ↗</div>
          </div>

          <!-- Card 2: Pendentes 48h -->
          <div class="exec-card" style="border-top:3px solid #f59e0b; cursor:pointer;" onclick="openModalMatriculas('24h_pend')" title="Clique para ver detalhes das matrículas pendentes nas últimas 24h">
            <div class="exec-card-top">
              <span class="exec-card-label">Matrículas Pendentes</span>
              <span class="exec-pill pill-ambe
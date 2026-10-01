import os

dash_dir = r'C:\Users\DELL\Desktop\Dash_InfectoCast'
template_path = os.path.join(dash_dir, 'template.html')

with open(template_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Replace the modal HTML at the top
m_start = code.find('<div class="modal-ov" id="modal-sync-24h">')
m_end = code.find('</div>\n</div>', m_start) + 13
if m_end < m_start:
    m_end = code.find('</div>\r\n</div>', m_start) + 15

new_modal_html = '''<div class="modal-ov" id="modal-sync-24h">
  <div class="modal" role="dialog" aria-modal="true" style="max-width:900px; padding:0; overflow:hidden; border-radius:14px; background:var(--card); box-shadow:0 10px 40px rgba(0,0,0,0.35);">
    <div class="md-head" style="background:var(--card-hover); padding:16px 20px; border-bottom:1px solid var(--line); position:relative;">
      <button class="md-close" onclick="closeSyncModal24h()" aria-label="Fechar" style="position:absolute; right:16px; top:16px; border:none; background:transparent; font-size:18px; cursor:pointer; color:var(--muted);">✕</button>
      <h3 style="margin:0 0 4px; font-size:16px; font-weight:800; color:var(--ink); display:flex; align-items:center; gap:8px;">
        <span style="display:inline-block; width:9px; height:9px; border-radius:50%; background:#10b981; box-shadow:0 0 10px #10b981;"></span>
        Auditoria de Matrículas // Confirmadas vs Pendentes
      </h3>
      <div style="font-size:11.5px; color:var(--muted)">Matrículas Confirmadas (1º Pagamento Aprovado) e Inscrições Pendentes (sem financeiro e sem consumo)</div>
    </div>
    
    <!-- Mini Telemetria & Estatísticas -->
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; padding:14px 20px; background:var(--bg); border-bottom:1px solid var(--line);">
      <div style="padding:10px 14px; background:var(--card); border:1px solid var(--line); border-radius:8px;">
        <div style="font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:700;">Registros no Filtro</div>
        <div style="font-size:18px; font-weight:800; color:#10b981" id="msync-total-val">0</div>
      </div>
      <div style="padding:10px 14px; background:var(--card); border:1px solid var(--line); border-radius:8px;">
        <div style="font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:700;">Tipo Selecionado</div>
        <div style="font-size:12.5px; font-weight:800; color:var(--ink); margin-top:2px;" id="msync-type-label">Matrículas Confirmadas</div>
      </div>
      <div style="padding:10px 14px; background:var(--card); border:1px solid var(--line); border-radius:8px;">
        <div style="font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:700;">Último Registro</div>
        <div style="font-size:12px; font-weight:700; color:var(--ink); margin-top:3px" id="msync-last-time">Hoje recente</div>
      </div>
    </div>

    <!-- Abas Rápidas de Período -->
    <div style="display:flex; align-items:center; gap:8px; padding:12px 20px; background:var(--card); border-bottom:1px solid var(--line); overflow-x:auto;" id="msync-tabs-container">
    </div>

    <!-- Barra de Pesquisa Rápida -->
    <div style="padding:10px 20px; background:var(--bg); border-bottom:1px solid var(--line); display:flex; align-items:center; gap:10px;">
      <input type="text" id="msync-search" placeholder="🔍 Buscar por nome, email ou curso..." style="width:100%; padding:8px 12px; border-radius:6px; border:1px solid var(--line); background:var(--card); color:var(--ink); font-size:12px; outline:none;" />
    </div>

    <!-- Lista de Alunos -->
    <div id="msync-table-body" style="max-height:380px; overflow-y:auto;">
    </div>

    <!-- Rodapé -->
    <div style="padding:12px 20px; background:var(--card-hover); border-top:1px solid var(--line); display:flex; align-items:center; justify-content:space-between; font-size:11px; color:var(--muted);">
      <div><span>💡</span> Matrículas confirmadas possuem primeiro pagamento aprovado via Vindi/Asaas/Cativa.</div>
      <button onclick="closeSyncModal24h()" style="padding:6px 14px; border-radius:6px; border:1px solid var(--line); background:var(--card); color:var(--ink); font-weight:700; cursor:pointer;">Fechar</button>
    </div>
  </div>
</div>'''

code = code[:m_start] + new_modal_html + code[m_end:]

# 2. Replace JavaScript for Modal
js_start = code.find('function openModalMatriculas(')
js_end = code.find('// MODAL: PROJEÇÃO DIÁRIA', js_start)
if js_end == -1:
    js_end = code.find('// MODAL: PROJE', js_start)

new_modal_full_js = '''function openModalMatriculas(period) {
    const matData = getMatriculasAuditoriaData();
    _matriculasModalData = {
        period: period || '24h_conf',
        data: matData
    };

    const modal = document.getElementById('modal-sync-24h');
    if (!modal) return;

    // Atualizar abas dinâmicas
    updateMatriculasModalTabs();

    // Renderizar tabela com o período ativo
    filterMatriculasModalPeriod(_matriculasModalData.period);

    modal.classList.add('on');
    document.body.style.overflow = 'hidden';

    // Search handler
    const searchInp = document.getElementById('msync-search');
    if (searchInp) {
        searchInp.value = '';
        searchInp.oninput = function(e) {
            const term = e.target.value.toLowerCase().trim();
            const currentList = getActiveMatriculasList(_matriculasModalData.period);
            
            const filtered = currentList.filter(s => 
                (s.nome || '').toLowerCase().includes(term) ||
                (s.email || '').toLowerCase().includes(term) ||
                (s.curso || '').toLowerCase().includes(term) ||
                (s.origem || '').toLowerCase().includes(term) ||
                (s.gateway || '').toLowerCase().includes(term)
            );
            renderMatriculasTable(filtered);
        };
    }
}

function openModalSync24h() {
    openModalMatriculas('24h_conf');
}

function closeSyncModal24h() {
    const modal = document.getElementById('modal-sync-24h');
    if (modal) modal.classList.remove('on');
    if (!document.getElementById('modal') || !document.getElementById('modal').classList.contains('on')) {
        document.body.style.overflow = '';
    }
}

function getActiveMatriculasList(periodKey) {
    const d = (_matriculasModalData && _matriculasModalData.data) ? _matriculasModalData.data : getMatriculasAuditoriaData();
    if (periodKey === '24h_conf') return d.list24h || [];
    if (periodKey === '24h_pend') return d.pendentes24h || [];
    if (periodKey === '30d_conf') return d.list30d || [];
    if (periodKey === '30d_pend') return d.pendentes30d || [];
    if (periodKey === 'all_conf') return d.allRecords || [];
    if (periodKey === 'all_pend') return d.allPendentes || [];
    return d.list24h || [];
}

function updateMatriculasModalTabs() {
    const container = document.getElementById('msync-tabs-container');
    if (!container) return;
    
    const d = (_matriculasModalData && _matriculasModalData.data) ? _matriculasModalData.data : getMatriculasAuditoriaData();
    const p = _matriculasModalData.period;

    const tabs = [
        { id: '24h_conf', label: `⚡ Confirmadas 24h (${d.count24h})`, color: '#10b981', textColor: '#022c22' },
        { id: '24h_pend', label: `⏳ Pendentes 24h (${d.countPendentes24h})`, color: '#f59e0b', textColor: '#451a03' },
        { id: '30d_conf', label: `📅 Confirmadas 30d (${d.count30d})`, color: '#3b82f6', textColor: '#ffffff' },
        { id: '30d_pend', label: `⏳ Pendentes 30d (${d.countPendentes30d})`, color: '#f59e0b', textColor: '#451a03' },
        { id: 'all_conf', label: `📂 Todas Confirmadas (${d.totalConfirmadas})`, color: '#8b5cf6', textColor: '#ffffff' },
        { id: 'all_pend', label: `📂 Todas Pendentes (${d.totalPendentes})`, color: '#64748b', textColor: '#ffffff' }
    ];

    container.innerHTML = tabs.map(t => {
        const isActive = p === t.id;
        const bg = isActive ? t.color : 'var(--card)';
        const col = isActive ? t.textColor : 'var(--ink)';
        const border = isActive ? `1px solid ${t.color}` : '1px solid var(--line)';
        return `<button onclick="filterMatriculasModalPeriod('${t.id}')" style="background:${bg}; color:${col}; border:${border}; padding:6px 12px; border-radius:8px; font-size:11.5px; font-weight:700; cursor:pointer; transition:all 0.2s; white-space:nowrap;">${t.label}</button>`;
    }).join('');
}

function filterMatriculasModalPeriod(p) {
    _matriculasModalData.period = p;
    updateMatriculasModalTabs();

    const targetList = getActiveMatriculasList(p);

    const totalValEl = document.getElementById('msync-total-val');
    if (totalValEl) totalValEl.textContent = fmt(targetList.length);

    const typeLabelEl = document.getElementById('msync-type-label');
    if (typeLabelEl) {
        if (p.includes('pend')) {
            typeLabelEl.textContent = 'Matrículas Pendentes (Sem Financeiro / Sem Uso)';
            typeLabelEl.style.color = '#f59e0b';
        } else {
            typeLabelEl.textContent = 'Matrículas Confirmadas (1º Pagamento Aprovado)';
            typeLabelEl.style.color = '#10b981';
        }
    }

    const lastTimeEl = document.getElementById('msync-last-time');
    if (lastTimeEl) {
        if (targetList.length > 0 && targetList[0].data_fmt) {
            lastTimeEl.textContent = targetList[0].data_fmt;
        } else {
            lastTimeEl.textContent = '--';
        }
    }

    renderMatriculasTable(targetList);
}

function renderMatriculasTable(students) {
    const tbody = document.getElementById('msync-table-body');
    if (!tbody) return;

    if (!students || students.length === 0) {
        tbody.innerHTML = '<div style="padding:32px; text-align:center; color:var(--muted); font-size:12.5px;">Nenhum registro encontrado no período selecionado.</div>';
        return;
    }

    let rowsHtml = students.map((s, idx) => {
        const initials = (s.nome || 'A').split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
        const cursoTag = s.curso || 'PLATAFORMA GERAL';
        const dataTag = s.data_fmt || 'Recente';
        const isConfirmada = s.tipo === 'confirmada';
        
        const badgeBg = isConfirmada ? 'rgba(16,185,129,0.12)' : 'rgba(245,158,11,0.12)';
        const badgeColor = isConfirmada ? '#059669' : '#d97706';
        const badgeBorder = isConfirmada ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)';
        const icon = isConfirmada ? '💳' : '⏳';
        const labelText = isConfirmada ? `● Confirmada (${s.gateway || 'Gateway'})` : `⏳ Matrícula Pendente`;

        const valHtml = (isConfirmada && s.valor > 0) 
            ? `<span style="font-weight:800; color:#059669; font-size:11.5px;">${fM(s.valor)}</span>`
            : `<span style="color:var(--muted); font-size:11px;">${isConfirmada ? 'Acesso Confirmado' : '0 aulas assistidas'}</span>`;

        return `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 14px; border-bottom:1px solid var(--line); font-size:12px; transition:background 0.15s;" onmouseover="this.style.background='var(--card-hover)'" onmouseout="this.style.background='transparent'">
            <div style="display:flex; align-items:center; gap:12px; min-width:0;">
              <div style="width:34px; height:34px; border-radius:50%; background:${isConfirmada ? 'var(--sky-w)' : 'rgba(245,158,11,0.15)'}; color:${isConfirmada ? 'var(--sky-d)' : '#d97706'}; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:11px; flex-shrink:0;">
                ${initials}
              </div>
              <div style="min-width:0;">
                <div style="font-weight:700; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                  ${s.nome}
                </div>
                <div style="color:var(--muted); font-size:11px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                  ${s.email}
                </div>
              </div>
            </div>

            <div style="display:flex; align-items:center; gap:12px; flex-shrink:0;">
              <div style="text-align:right; max-width:260px;">
                <span style="display:inline-block; font-size:10.5px; font-weight:700; color:var(--ink); background:var(--bg); border:1px solid var(--line); border-radius:4px; padding:2px 6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:240px;">
                  ${cursoTag}
                </span>
                <div style="color:var(--muted); font-size:10px; margin-top:2px;">
                  ${valHtml} • ${dataTag}
                </div>
              </div>

              <div style="display:flex; align-items:center; gap:4px; padding:3px 8px; border-radius:20px; font-size:10px; font-weight:800; background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder}; white-space:nowrap;">
                <span>${icon}</span>
                <span>${labelText}</span>
              </div>
            </div>
          </div>
        `;
    }).join('');

    tbody.innerHTML = rowsHtml;
}

// Fechar ao clicar fora
document.addEventListener('click', function(e) {
    const modal = document.getElementById('modal-sync-24h');
    if (modal && e.target === modal) {
        closeSyncModal24h();
    }
});

'''

code = code[:js_start] + new_modal_full_js + code[js_end:]

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("SUCCESS: Clean modal and JS updated in template.html!")

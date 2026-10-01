import os

tables_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast\components\tables"
modules_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast\components\modules"
os.makedirs(modules_dir, exist_ok=True)

leads_table_code = """/**
 * InfectoCast Component Library - LeadsTable
 * Especialização de DataTable para análise de Leads, ICP e conversão via WhatsApp.
 */

import { DataTable } from './DataTable.js';

export class LeadsTable extends DataTable {
  /**
   * @param {Object} options
   * @param {Array<Object>} options.leads - Lista de leads
   * @param {Function} [options.onContactWhatsApp] - Callback ao clicar no botão de WhatsApp
   */
  constructor(options = {}) {
    const columns = [
      {
        key: 'nome',
        label: 'Lead / Contato',
        width: '260px',
        render: (val, row) => {
          const initials = (val || 'L').split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
          return `
            <div class="student-cell">
              <div class="student-avatar" style="border-color: rgba(6, 182, 212, 0.4); color: #06b6d4;">${initials}</div>
              <div class="student-info">
                <span class="student-name">${val || 'Lead Sem Nome'}</span>
                <span class="student-email">${row.email || '—'}</span>
              </div>
            </div>
          `;
        }
      },
      {
        key: 'score',
        label: 'Score (ICP)',
        width: '150px',
        render: (val) => {
          const score = Math.min(100, Math.max(0, Math.round(Number(val) || 0)));
          let color = '#ef4444'; // Laser Crimson
          if (score >= 80) color = '#10b981'; // Matrix Emerald
          else if (score >= 50) color = '#f59e0b'; // Hologram Amber
          else if (score >= 30) color = '#06b6d4'; // Electric Cyan

          return `
            <div class="table-progress-wrap">
              <div class="table-progress-bar" style="height: 8px; background: rgba(15, 23, 42, 0.8);">
                <div class="table-progress-fill" style="width: ${score}%; background: linear-gradient(90deg, ${color}88, ${color}); box-shadow: 0 0 10px ${color}66;"></div>
              </div>
              <span class="table-progress-text" style="color: ${color}; font-family: 'JetBrains Mono', monospace; font-weight: 700;">${score} pts</span>
            </div>
          `;
        }
      },
      {
        key: 'maturidade',
        label: 'Maturidade',
        render: (val) => {
          const m = (val || 'frio').toLowerCase();
          let cls = 'status-nunca';
          let label = 'Frio';
          if (m.includes('pronto') || m.includes('compra')) { cls = 'status-ativo'; label = 'Pronto p/ Venda'; }
          else if (m.includes('quente')) { cls = 'status-ativo'; label = 'Quente'; }
          else if (m.includes('morno')) { cls = 'status-risco'; label = 'Morno'; }
          
          return `<span class="status-badge ${cls}"><span class="status-dot"></span> ${label}</span>`;
        }
      },
      {
        key: 'profissao',
        label: 'Especialidade / ICP',
        render: (val) => `<span class="course-tag" style="background: rgba(168, 85, 247, 0.1); border-color: rgba(168, 85, 247, 0.3); color: #c084fc;">${val || 'Médico Geral'}</span>`
      },
      {
        key: 'curso',
        label: 'Interesse',
        render: (val) => `<span class="course-tag" title="${val || ''}">${val || 'Geral'}</span>`
      },
      {
        key: 'conversoes',
        label: 'Conversões',
        align: 'center',
        render: (val) => `<span class="kpi-badge" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4; border: 1px solid rgba(6, 182, 212, 0.3); font-family: 'JetBrains Mono', monospace;">${val || 1} ev</span>`
      },
      {
        key: 'actions',
        label: 'Contato',
        sortable: false,
        align: 'center',
        render: (_, row) => {
          const btn = document.createElement('a');
          const cleanPhone = (row.telefone || '').replace(/\\D/g, '');
          const phone = cleanPhone ? (cleanPhone.startsWith('55') ? cleanPhone : '55' + cleanPhone) : '';
          btn.className = 'action-btn';
          btn.style.borderColor = 'rgba(16, 185, 129, 0.4)';
          btn.style.color = '#10b981';
          btn.style.background = 'rgba(16, 185, 129, 0.08)';
          btn.innerHTML = '⚡ WhatsApp';
          
          if (phone) {
            btn.href = `https://wa.me/${phone}?text=Ol%C3%A1%20${encodeURIComponent(row.nome || '')},%20vimos%20seu%20interesse%20no%20InfectoCast!`;
            btn.target = '_blank';
          } else {
            btn.href = '#';
            btn.style.opacity = '0.5';
            btn.title = 'Sem telefone cadastrado';
          }

          btn.addEventListener('click', (e) => {
            if (!phone) e.preventDefault();
            if (typeof options.onContactWhatsApp === 'function') {
              options.onContactWhatsApp(row);
            }
          });
          return btn;
        }
      }
    ];

    super({
      ...options,
      columns,
      data: options.leads || [],
      searchPlaceholder: 'Buscar lead por nome, email, especialidade ou curso...',
      searchKeys: ['nome', 'email', 'profissao', 'curso', 'telefone']
    });

    this.onContactWhatsApp = options.onContactWhatsApp || null;
  }
}
"""

with open(os.path.join(tables_dir, "LeadsTable.js"), "w", encoding="utf-8") as f:
    f.write(leads_table_code)

financial_table_code = """/**
 * InfectoCast Component Library - FinancialTable
 * Especialização de DataTable para faturas, parcelas e conciliação de receita.
 */

import { DataTable } from './DataTable.js';

export class FinancialTable extends DataTable {
  /**
   * @param {Object} options
   * @param {Array<Object>} options.financial - Lista de lançamentos financeiros
   * @param {Function} [options.onVerFatura] - Callback ao clicar em ver fatura
   */
  constructor(options = {}) {
    const columns = [
      {
        key: 'aluno',
        label: 'Aluno / Sacado',
        width: '260px',
        render: (val, row) => {
          const initials = (val || 'A').split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
          return `
            <div class="student-cell">
              <div class="student-avatar" style="border-color: rgba(245, 158, 11, 0.4); color: #f59e0b;">${initials}</div>
              <div class="student-info">
                <span class="student-name">${val || 'Sem Nome'}</span>
                <span class="student-email">${row.email || '—'}</span>
              </div>
            </div>
          `;
        }
      },
      {
        key: 'plano',
        label: 'Curso / Assinatura',
        render: (val) => `<span class="course-tag" title="${val || ''}">${val || 'Pós-Graduação'}</span>`
      },
      {
        key: 'vencimento',
        label: 'Vencimento',
        render: (val) => `<span style="color: #94a3b8; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">${val || '—'}</span>`
      },
      {
        key: 'valor',
        label: 'Valor',
        align: 'right',
        render: (val) => {
          const num = Number(val) || 0;
          return `<span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #f8fafc;">R$ ${num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;
        }
      },
      {
        key: 'status',
        label: 'Liquidação',
        render: (val) => {
          const s = (val || 'pago').toLowerCase();
          let cls = 'status-ativo';
          let label = 'Pago / Liquidado';
          if (s.includes('vencid') || s.includes('inadimpl')) { cls = 'status-abandono'; label = 'Inadimplente'; }
          else if (s.includes('futur') || s.includes('abert') || s.includes('pendent')) { cls = 'status-risco'; label = 'A Vencer'; }
          
          return `<span class="status-badge ${cls}"><span class="status-dot"></span> ${label}</span>`;
        }
      },
      {
        key: 'gateway',
        label: 'Origem',
        align: 'center',
        render: (val) => {
          const gw = (val || 'Asaas').toLowerCase();
          const isVindi = gw.includes('vindi');
          const border = isVindi ? 'rgba(245, 158, 11, 0.4)' : 'rgba(168, 85, 247, 0.4)';
          const color = isVindi ? '#f59e0b' : '#c084fc';
          return `<span class="kpi-badge" style="border: 1px solid ${border}; color: ${color}; font-size: 0.725rem;">${isVindi ? 'VINDI' : 'ASAAS'}</span>`;
        }
      },
      {
        key: 'actions',
        label: 'Fatura',
        sortable: false,
        align: 'center',
        render: (_, row) => {
          const btn = document.createElement('a');
          btn.className = 'action-btn';
          btn.style.borderColor = 'rgba(6, 182, 212, 0.4)';
          btn.style.color = '#06b6d4';
          btn.innerHTML = '📄 Detalhes';
          
          if (row.url) {
            btn.href = row.url;
            btn.target = '_blank';
          } else {
            btn.href = '#';
          }

          btn.addEventListener('click', (e) => {
            if (!row.url) e.preventDefault();
            if (typeof options.onVerFatura === 'function') {
              options.onVerFatura(row);
            }
          });
          return btn;
        }
      }
    ];

    super({
      ...options,
      columns,
      data: options.financial || [],
      searchPlaceholder: 'Buscar fatura por aluno, e-mail ou descrição...',
      searchKeys: ['aluno', 'email', 'plano', 'status', 'gateway']
    });

    this.onVerFatura = options.onVerFatura || null;
  }
}
"""

with open(os.path.join(tables_dir, "FinancialTable.js"), "w", encoding="utf-8") as f:
    f.write(financial_table_code)

tables_index_code = """export { DataTable } from './DataTable.js';
export { StudentTable } from './StudentTable.js';
export { LeadsTable } from './LeadsTable.js';
export { FinancialTable } from './FinancialTable.js';
"""

with open(os.path.join(tables_dir, "index.js"), "w", encoding="utf-8") as f:
    f.write(tables_index_code)

module_grid_code = """/**
 * InfectoCast Component Library - ModuleEngagementGrid
 * Visualização e mapeamento de engajamento curricular com detecção de gargalos (Sci-Fi HUD).
 */

export class ModuleEngagementGrid {
  /**
   * @param {Object} options
   * @param {HTMLElement|string} options.container - Container DOM
   * @param {Array<Object>} options.modules - Lista de módulos curriculares
   * @param {Function} [options.onModuleClick] - Callback ao clicar em um módulo
   */
  constructor(options = {}) {
    this.container = typeof options.container === 'string'
      ? document.querySelector(options.container)
      : options.container;

    if (!this.container) {
      console.error('[ModuleEngagementGrid] Container inválido.');
      return;
    }

    this.modules = options.modules || [];
    this.onModuleClick = options.onModuleClick || null;
    this.expandedModules = new Set();
    this.render();
  }

  setData(modules) {
    this.modules = modules || [];
    this.render();
  }

  toggleModule(index) {
    if (this.expandedModules.has(index)) {
      this.expandedModules.delete(index);
    } else {
      this.expandedModules.add(index);
    }
    this.render();
  }

  render() {
    this.container.innerHTML = '';
    const grid = document.createElement('div');
    grid.className = 'module-engagement-grid';

    if (!this.modules.length) {
      grid.innerHTML = '<div class="hud-card module-card-empty">Nenhum módulo curricular registrado.</div>';
      this.container.appendChild(grid);
      return;
    }

    this.modules.forEach((mod, idx) => {
      const isExpanded = this.expandedModules.has(idx);
      const card = document.createElement('div');
      card.className = `hud-card module-card ${mod.is_bottleneck ? 'is-bottleneck' : ''}`;
      
      const pct = Math.min(100, Math.max(0, Math.round(Number(mod.taxa_conclusao) || 0)));
      let color = '#06b6d4';
      if (pct >= 80) color = '#10b981';
      else if (pct < 40) color = '#ef4444';
      else if (pct < 65) color = '#f59e0b';

      card.innerHTML = `
        <div class="module-header" data-idx="${idx}">
          <div class="module-title-wrap">
            <span class="module-num">MÓDULO ${String(idx + 1).padStart(2, '0')}</span>
            <h4 class="module-name">${mod.nome || 'Módulo Sem Nome'}</h4>
          </div>
          ${mod.is_bottleneck ? '<span class="module-bottleneck-badge">⚠️ GARGALO</span>' : ''}
          <div class="module-expand-icon">${isExpanded ? '▲' : '▼'}</div>
        </div>

        <div class="module-stats-row">
          <div class="module-stat-item">
            <span class="m-stat-label">Aulas</span>
            <span class="m-stat-value">${mod.total_aulas || 0}</span>
          </div>
          <div class="module-stat-item">
            <span class="m-stat-label">Concluintes</span>
            <span class="m-stat-value">${mod.alunos_concluiram || 0}</span>
          </div>
          <div class="module-stat-item">
            <span class="m-stat-label">Taxa Conclusão</span>
            <span class="m-stat-value" style="color: ${color};">${pct}%</span>
          </div>
        </div>

        <div class="module-progress-track">
          <div class="module-progress-fill" style="width: ${pct}%; background: ${color}; box-shadow: 0 0 10px ${color}88;"></div>
        </div>

        ${isExpanded && mod.aulas && mod.aulas.length ? `
          <div class="module-lessons-list">
            <div class="module-lessons-header">Detalhamento por Aula:</div>
            ${mod.aulas.map((aula, aIdx) => `
              <div class="module-lesson-item">
                <span class="lesson-idx">A${aIdx + 1}</span>
                <span class="lesson-title">${aula.titulo || 'Aula ' + (aIdx + 1)}</span>
                <span class="lesson-views">${aula.visualizacoes || 0} views</span>
              </div>
            `).join('')}
          </div>
        ` : ''}
      `;

      card.querySelector('.module-header').addEventListener('click', () => {
        this.toggleModule(idx);
        if (typeof this.onModuleClick === 'function') {
          this.onModuleClick(mod, idx);
        }
      });

      grid.appendChild(card);
    });

    this.container.appendChild(grid);
  }
}
"""

with open(os.path.join(modules_dir, "ModuleEngagementGrid.js"), "w", encoding="utf-8") as f:
    f.write(module_grid_code)

modules_css_code = """/* InfectoCast - ModuleEngagementGrid Styles (Dark Command-Center HUD) */
.module-engagement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
  width: 100%;
}

.module-card {
  padding: 1.25rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(16px);
  position: relative;
  border-radius: 12px;
}

.module-card:hover {
  border-color: rgba(6, 182, 212, 0.35);
  box-shadow: 0 8px 24px -6px rgba(6, 182, 212, 0.12);
}

.module-card.is-bottleneck {
  border-color: rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.04);
}

.module-card.is-bottleneck:hover {
  border-color: rgba(239, 68, 68, 0.7);
  box-shadow: 0 8px 24px -6px rgba(239, 68, 68, 0.25);
}

.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  gap: 0.75rem;
  user-select: none;
}

.module-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.module-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #06b6d4;
  text-transform: uppercase;
}

.module-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #f8fafc;
  margin: 0;
}

.module-bottleneck-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  animation: pulse-red 2s infinite ease-in-out;
}

@keyframes pulse-red {
  0%, 100% { opacity: 0.9; box-shadow: 0 0 8px rgba(239, 68, 68, 0.2); }
  50% { opacity: 0.6; box-shadow: none; }
}

.module-expand-icon {
  color: #64748b;
  font-size: 0.75rem;
  transition: transform 0.2s;
}

.module-stats-row {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(2, 6, 23, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.08);
}

.module-stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.m-stat-label {
  font-size: 0.7rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.m-stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.95rem;
  font-weight: 700;
  color: #e2e8f0;
}

.module-progress-track {
  width: 100%;
  height: 6px;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 9999px;
  overflow: hidden;
  margin-top: 0.85rem;
}

.module-progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.module-lessons-list {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px dashed rgba(148, 163, 184, 0.15);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.module-lessons-header {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 0.25rem;
}

.module-lesson-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.6rem;
  background: rgba(2, 6, 23, 0.4);
  border-radius: 6px;
  font-size: 0.8rem;
}

.lesson-idx {
  font-family: 'JetBrains Mono', monospace;
  color: #06b6d4;
  font-size: 0.725rem;
  font-weight: 700;
  min-width: 30px;
}

.lesson-title {
  color: #cbd5e1;
  flex: 1;
  margin: 0 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lesson-views {
  font-family: 'JetBrains Mono', monospace;
  color: #64748b;
  font-size: 0.725rem;
}
"""

with open(os.path.join(modules_dir, "modules.css"), "w", encoding="utf-8") as f:
    f.write(modules_css_code)

modules_index_code = """export { ModuleEngagementGrid } from './ModuleEngagementGrid.js';
"""

with open(os.path.join(modules_dir, "index.js"), "w", encoding="utf-8") as f:
    f.write(modules_index_code)

print("SUCCESS: Created LeadsTable, FinancialTable, ModuleEngagementGrid and modules.css")

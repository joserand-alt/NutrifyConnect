import re

def main():
    template_path = 'c:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update root CSS variables and clean theme
    dark_overrides_marker = '/* =============================================================================\n   MANDATORY DARK COMMAND-CENTER OVERRIDES'
    if dark_overrides_marker in html:
        idx_dark = html.find(dark_overrides_marker)
        idx_style_close = html.find('</style>', idx_dark)
        if idx_dark != -1 and idx_style_close != -1:
            light_overrides = """
/* =============================================================================
   MANDATORY LIGHT SLATE EXECUTIVE OVERRIDES
   ============================================================================= */
:root {
  --bg: #f8fafc !important;
  --bg-darker: #f1f5f9 !important;
  --paper: #f8fafc !important;
  --card: #ffffff !important;
  --card-elevated: #ffffff !important;
  --card-translucent: rgba(255, 255, 255, 0.95) !important;
  
  --ink: #0f172a !important;
  --ink2: #334155 !important;
  --muted: #64748b !important;
  --muted2: #94a3b8 !important;
  --line: #e2e8f0 !important;
  --line2: #f1f5f9 !important;
  
  --emerald: #10b981 !important;
  --emerald-d: #059669 !important;
  --emerald-w: rgba(16, 185, 129, 0.12) !important;
  --amber: #f59e0b !important;
  --amber-w: rgba(245, 158, 11, 0.12) !important;
  --coral: #f43f5e !important;
  --coral-w: rgba(244, 63, 94, 0.12) !important;
  --sky: #0284c7 !important;
  --sky-w: rgba(2, 132, 199, 0.12) !important;
  --violet: #8b5cf6 !important;
  --violet-w: rgba(139, 92, 246, 0.12) !important;
  --ink-soft: rgba(2, 132, 199, 0.08) !important;
}

html, body {
  background-color: #f8fafc !important;
  color: #0f172a !important;
}

.card, .kpi, .exec-sec, .exec-kpi-card, .tbl-wrap, .funnel-row, 
.insight, .note, div[style*="background:var(--card)"], div[style*="background: var(--card)"],
div[style*="background:#FFFFFF"], div[style*="background: #FFFFFF"],
div[style*="background:#fff"], div[style*="background: #fff"],
div[style*="background:white"], div[style*="background: white"],
#home-live-section {
  background: #ffffff !important;
  border-color: #e2e8f0 !important;
  color: #0f172a !important;
  box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.05), 0 1px 3px rgba(15, 23, 42, 0.02) !important;
}

/* Secondary boxes */
.exec-kpi-card, div[style*="background:var(--paper)"], div[style*="background: var(--paper)"],
div[style*="background:#F5F7F5"], div[style*="background: #F5F7F5"],
div[style*="background:#F0F3F1"], div[style*="background:#F0F1F3"] {
  background: #f8fafc !important;
  border-color: #e2e8f0 !important;
  color: #0f172a !important;
}

/* TITLES & HEADINGS */
h1, h2, h3, h4, h5, h6, .exec-sec-title, .brand h1 {
  color: #0f172a !important;
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
}

/* MONOSPACE NUMERALS */
.k-val, .exec-kpi-val, .numeral, .val, .metric-value, .stat-value {
  font-family: 'JetBrains Mono', monospace !important;
  font-variant-numeric: tabular-nums !important;
  color: #0f172a !important;
  text-shadow: none !important;
}

/* LABELS & SUBTITLES */
.k-lab, .exec-sec-sub, .exec-kpi-sub, .micro-label, .sub, .k-sub,
label, .eyebrow, .badge-label {
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: #64748b !important;
}

/* TABLES & DATA CELLS */
table, tbody, thead, tr, td, th {
  background-color: transparent !important;
}
th {
  background: #f8fafc !important;
  border-bottom: 2px solid #e2e8f0 !important;
  color: #0369a1 !important;
}
td {
  border-bottom: 1px solid #f1f5f9 !important;
  color: #334155 !important;
}
tr:hover td {
  background: rgba(2, 132, 199, 0.03) !important;
}

/* INPUTS & SELECTS */
select, input, textarea {
  background: #f8fafc !important;
  border: 1px solid #cbd5e1 !important;
  color: #0f172a !important;
  border-radius: 8px !important;
}
select:focus, input:focus {
  border-color: #0284c7 !important;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.12) !important;
  outline: none !important;
}
option {
  background: #ffffff !important;
  color: #0f172a !important;
}

/* PROGRESS BARS */
.prog-fill, .p-fill, .progress-bar-fill {
  background: linear-gradient(90deg, #0284c7 0%, #10b981 100%) !important;
  box-shadow: 0 0 8px rgba(2, 132, 199, 0.25) !important;
}
"""
            html = html[:idx_dark] + light_overrides + html[idx_style_close:]

    # Update the sidebar CSS at the bottom of the file
    sidebar_marker = '/* HUD APP LAYOUT & COLLAPSIBLE SIDEBAR'
    if sidebar_marker in html:
        idx_sb = html.find(sidebar_marker)
        idx_sb_close = html.find('</style>', idx_sb)
        if idx_sb != -1 and idx_sb_close != -1:
            light_sidebar_css = """/* HUD APP LAYOUT & COLLAPSIBLE SIDEBAR (LIGHT EXECUTIVE THEME) */
.hud-app-layout {
  display: flex;
  width: 100%;
  min-height: calc(100vh - 52px);
  position: relative;
  background: #f8fafc;
}

.hud-sidebar {
  width: 240px;
  min-width: 240px;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  box-shadow: 2px 0 16px rgba(15, 23, 42, 0.03);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 100;
  transition: width 0.22s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-x: hidden;
  overflow-y: auto;
  user-select: none;
}

.hud-sidebar.collapsed {
  width: 68px;
  min-width: 68px;
}

.hud-sidebar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 14px;
  border-bottom: 1px solid #e2e8f0;
  min-height: 52px;
}

.hud-sidebar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
}

.hud-sidebar.collapsed .hud-sidebar-brand {
  display: none;
}

.hud-sidebar-title {
  font-family: var(--font-hud);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #0284c7;
}

.sidebar-toggle-btn {
  background: rgba(2, 132, 199, 0.08);
  border: 1px solid rgba(2, 132, 199, 0.2);
  color: #0284c7;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.15s ease;
  flex-shrink: 0;
}
.sidebar-toggle-btn:hover {
  background: #0284c7;
  color: #ffffff;
}
.hud-sidebar.collapsed .sidebar-toggle-btn {
  margin: 0 auto;
}

/* SIDEBAR TABS NAV */
.hud-sidebar .tabs {
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
  padding: 12px 8px !important;
  margin: 0 !important;
  border: none !important;
  flex: 1 !important;
}

.hud-sidebar .tab {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  width: 100% !important;
  padding: 9px 12px !important;
  border-radius: 8px !important;
  border: 1px solid transparent !important;
  border-left: 3px solid transparent !important;
  background: transparent !important;
  color: #64748b !important;
  font-family: var(--font-hud) !important;
  font-size: 11.5px !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
  text-transform: none !important;
  text-align: left !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
  white-space: nowrap !important;
  position: relative !important;
}

.hud-sidebar .tab .num {
  width: 24px !important;
  height: 24px !important;
  min-width: 24px !important;
  border-radius: 6px !important;
  background: #f1f5f9 !important;
  color: #64748b !important;
  font-family: var(--font-mono) !important;
  font-size: 11px !important;
  display: grid !important;
  place-items: center !important;
  flex-shrink: 0 !important;
  transition: all 0.15s ease !important;
}

.hud-sidebar .tab .tab-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hud-sidebar.collapsed .tab {
  padding: 9px 0 !important;
  justify-content: center !important;
}

.hud-sidebar.collapsed .tab .tab-label {
  display: none !important;
}

.hud-sidebar .tab:hover {
  background: #f1f5f9 !important;
  color: #0f172a !important;
}

.hud-sidebar .tab:hover .num {
  background: #e2e8f0 !important;
  color: #0284c7 !important;
}

.hud-sidebar .tab.on {
  background: rgba(2, 132, 199, 0.08) !important;
  color: #0284c7 !important;
  border-left: 3px solid #0284c7 !important;
  font-weight: 700 !important;
}

.hud-sidebar .tab.on .num {
  background: #0284c7 !important;
  color: #ffffff !important;
  font-weight: 800 !important;
}

.hud-sidebar .tab.on::after {
  display: none !important;
}

/* SIDEBAR FOOTER */
.hud-sidebar-footer {
  padding: 12px 10px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-collapse-bar-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 7px 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #64748b;
  font-family: var(--font-hud);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.sidebar-collapse-bar-btn:hover {
  background: #f1f5f9;
  color: #0284c7;
  border-color: #cbd5e1;
}
.hud-sidebar.collapsed .sidebar-collapse-bar-btn {
  justify-content: center;
  padding: 7px 0;
}
.hud-sidebar.collapsed .sidebar-footer-label {
  display: none !important;
}

.sidebar-status-pill {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: #059669;
  white-space: nowrap;
}
.hud-sidebar.collapsed .sidebar-status-pill {
  justify-content: center;
  padding: 4px 0;
}

/* MAIN CONTENT */
.hud-main-content {
  flex: 1;
  min-width: 0;
  padding: 12px 28px 48px;
  max-width: 100%;
}

/* COMPACT HEADER */
header {
  padding: 8px 24px !important;
  min-height: 48px !important;
  max-height: 52px !important;
  display: flex !important;
  align-items: center !important;
}
"""
            html = html[:idx_sb] + light_sidebar_css + html[idx_sb_close:]

    # Remove floating <div class="kpis" id="kpis"></div> from top of main
    html = re.sub(r'<div class="kpis"\s+id="kpis">\s*</div>', '', html)

    # Insert <div class="kpis" id="kpis"></div> inside #p-prog right after .sec-head
    p_prog_idx = html.find('<section class="panel" id="p-prog">')
    if p_prog_idx != -1:
        end_sec_head = html.find('</div>', html.find('<div class="sec-head">', p_prog_idx))
        if end_sec_head != -1:
            html = html[:end_sec_head+6] + '\n    <div class="kpis" id="kpis" style="margin-top:14px; margin-bottom:18px"></div>' + html[end_sec_head+6:]

    # Make sure global-filter-bar has compact margins
    html = re.sub(r'margin:20px 0 24px 0;', 'margin:0 0 14px 0;', html)
    html = re.sub(r'margin: 20px 0 24px 0;', 'margin:0 0 14px 0;', html)

    # Clean up selectTab KPI toggle
    select_tab_snippet = """        // Exibe/oculta barra de KPIs do cabeçalho de acordo com a aba
        if (pId === 'exec' || pId === 'curso' || pId === 'home' || pId === 'fin' || pId === 'funil') {
            if ($('#kpis')) $('#kpis').style.display = 'none';
        } else {
            if ($('#kpis')) $('#kpis').style.display = 'grid';
        }"""
    if select_tab_snippet in html:
        html = html.replace(select_tab_snippet, "// KPIs scoped to relevant tab")

    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Template updated successfully!")

if __name__ == '__main__':
    main()

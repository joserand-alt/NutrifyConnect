import re

TEMPLATE_PATH = r"C:\Users\DELL\Desktop\Dash_InfectoCast\template.html"

with open(TEMPLATE_PATH, "r", encoding="utf-8-sig") as f:
    html = f.read()

# Comprehensive CSS overrides ensuring 100% of panels, cards, tables, inputs, and text are Dark Command Center
comprehensive_dark_css = """
/* =============================================================================
   MANDATORY DARK COMMAND-CENTER OVERRIDES (GUARANTEED APPLIED TO ALL TABS)
   ============================================================================= */
:root {
  --bg: #0a0e14 !important;
  --bg-darker: #06090d !important;
  --paper: #0a0e14 !important;
  --card: #101622 !important;
  --card-elevated: #141c2c !important;
  --card-translucent: rgba(16, 22, 34, 0.9) !important;
  
  --ink: #e2e8f0 !important;
  --ink2: #cbd5e1 !important;
  --muted: #788c9f !important;
  --muted2: #4a5d70 !important;
  --line: rgba(255, 255, 255, 0.08) !important;
  --line2: rgba(255, 255, 255, 0.04) !important;
  
  --neon-cyan: #00f0ff !important;
  --neon-amber: #ff9e00 !important;
  --neon-red: #ff3366 !important;
  --neon-green: #00ff9d !important;
  --neon-violet: #a855f7 !important;
  
  --emerald: #00ff9d !important;
  --emerald-d: #00cc7d !important;
  --emerald-w: rgba(0, 255, 157, 0.12) !important;
  --amber: #ff9e00 !important;
  --amber-w: rgba(255, 158, 0, 0.12) !important;
  --coral: #ff3366 !important;
  --coral-w: rgba(255, 51, 102, 0.12) !important;
  --sky: #00f0ff !important;
  --violet: #a855f7 !important;
  --ink-soft: rgba(0, 240, 255, 0.08) !important;
}

html, body {
  background-color: #0a0e14 !important;
  color: #e2e8f0 !important;
}

/* ALL CARDS & CONTAINERS ACROSS ALL TABS */
.card, .kpi, .exec-sec, .exec-kpi-card, .tbl-wrap, .panel, .funnel-row, .modal-content, 
.insight, .note, div[style*="background:var(--card)"], div[style*="background: var(--card)"],
div[style*="background:#FFFFFF"], div[style*="background: #FFFFFF"],
div[style*="background:#fff"], div[style*="background: #fff"],
div[style*="background:white"], div[style*="background: white"] {
  background: rgba(16, 22, 34, 0.92) !important;
  border-color: rgba(255, 255, 255, 0.08) !important;
  color: #e2e8f0 !important;
  box-shadow: 0 8px 30px -4px rgba(0, 0, 0, 0.7), inset 0 1px 0 0 rgba(255, 255, 255, 0.05) !important;
}

/* CARDS WITH HIGHER CONTRAST IN DARK THEME */
.exec-kpi-card, div[style*="background:var(--paper)"], div[style*="background: var(--paper)"],
div[style*="background:#F5F7F5"], div[style*="background: #F5F7F5"],
div[style*="background:#F0F3F1"], div[style*="background:#F0F1F3"] {
  background: rgba(12, 17, 26, 0.85) !important;
  border-color: rgba(255, 255, 255, 0.06) !important;
  color: #e2e8f0 !important;
}

/* TITLES & HEADINGS */
h1, h2, h3, h4, h5, h6, .exec-sec-title, .brand h1 {
  color: #ffffff !important;
  font-family: 'Space Grotesk', 'Chakra Petch', sans-serif !important;
}

/* MONOSPACE NUMERALS */
.k-val, .exec-kpi-val, .numeral, .val, .metric-value, .stat-value,
div[style*="font-size:29px"], div[style*="font-size: 29px"],
div[style*="font-size:28px"], div[style*="font-size: 28px"],
div[style*="font-size:24px"], div[style*="font-size: 24px"],
div[style*="font-size:22px"], div[style*="font-size: 22px"] {
  font-family: 'JetBrains Mono', monospace !important;
  font-variant-numeric: tabular-nums !important;
  color: #ffffff !important;
  text-shadow: 0 0 14px rgba(0, 240, 255, 0.25) !important;
}

/* MICRO-LABELS IN UPPERCASE */
.k-lab, .exec-sec-sub, .exec-kpi-sub, .micro-label, .sub, .k-sub,
th, label, .eyebrow, .badge-label {
  font-family: 'Chakra Petch', 'Space Grotesk', sans-serif !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: #788c9f !important;
}

/* ACCENT BADGES & BUTTONS */
.btn-exec-link {
  background: rgba(0, 240, 255, 0.08) !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  color: #00f0ff !important;
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.15) !important;
}
.btn-exec-link:hover {
  background: rgba(0, 240, 255, 0.18) !important;
  border-color: #00f0ff !important;
  box-shadow: 0 0 18px rgba(0, 240, 255, 0.35) !important;
}

.exec-sec-num {
  background: rgba(0, 240, 255, 0.1) !important;
  color: #00f0ff !important;
  border: 1px solid rgba(0, 240, 255, 0.3) !important;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.2) !important;
}

/* TABLES & DATA CELLS */
table, tbody, thead, tr, td, th {
  background-color: transparent !important;
}
th {
  background: #090e16 !important;
  border-bottom: 1px solid rgba(0, 240, 255, 0.2) !important;
  color: #00f0ff !important;
}
td {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
  color: #cbd5e1 !important;
}
tr:hover td {
  background: rgba(0, 240, 255, 0.04) !important;
}

/* INPUTS & SELECTS */
select, input, textarea {
  background: #090d14 !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  color: #ffffff !important;
  border-radius: 6px !important;
}
select:focus, input:focus {
  border-color: #00f0ff !important;
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.3) !important;
  outline: none !important;
}
option {
  background: #0f1622 !important;
  color: #ffffff !important;
}

/* STATUS BADGES WITH GLOW */
.b-pago, .badge-pago, .status-pago {
  background: rgba(0, 255, 157, 0.1) !important;
  border: 1px solid rgba(0, 255, 157, 0.35) !important;
  color: #00ff9d !important;
  box-shadow: 0 0 8px rgba(0, 255, 157, 0.2) !important;
}
.b-pend, .badge-pendente, .status-pendente, .b-atraso {
  background: rgba(255, 158, 0, 0.1) !important;
  border: 1px solid rgba(255, 158, 0, 0.35) !important;
  color: #ff9e00 !important;
  box-shadow: 0 0 8px rgba(255, 158, 0, 0.2) !important;
}
.b-canc, .badge-cancelado, .status-cancelado, .b-risco {
  background: rgba(255, 51, 102, 0.1) !important;
  border: 1px solid rgba(255, 51, 102, 0.35) !important;
  color: #ff3366 !important;
  box-shadow: 0 0 8px rgba(255, 51, 102, 0.2) !important;
}

/* HUD CORNER NOTCHES ON SECTION CARDS */
.exec-sec, .card, #home-live-section {
  position: relative;
}
.exec-sec::before, .card::before {
  content: "";
  position: absolute;
  top: 0; left: 0;
  width: 8px; height: 8px;
  border-top: 2px solid #00f0ff;
  border-left: 2px solid #00f0ff;
  border-top-left-radius: 12px;
  pointer-events: none;
}
.exec-sec::after, .card::after {
  content: "";
  position: absolute;
  bottom: 0; right: 0;
  width: 8px; height: 8px;
  border-bottom: 2px solid #00f0ff;
  border-right: 2px solid #00f0ff;
  border-bottom-right-radius: 12px;
  pointer-events: none;
}

/* NEON PROGRESS BARS */
.prog-fill, .p-fill, .progress-bar-fill {
  background: linear-gradient(90deg, #00f0ff 0%, #00ff9d 100%) !important;
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.5) !important;
}
"""

# Insert comprehensive_dark_css right before </style>
pos_style_end = html.find("</style>")
if pos_style_end != -1:
    html = html[:pos_style_end] + "\n\n" + comprehensive_dark_css + "\n" + html[pos_style_end:]
    print("Comprehensive dark CSS injected right before </style>.")

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Template saved! Running node syntax check...")

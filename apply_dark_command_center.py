import re
import os

TEMPLATE_PATH = r"C:\Users\DELL\Desktop\Dash_InfectoCast\template.html"

with open(TEMPLATE_PATH, "r", encoding="utf-8-sig") as f:
    html = f.read()

print("Original template size:", len(html))

# ==============================================================================
# 1. ATUALIZAR <head>: FONTES E THREE.JS
# ==============================================================================
head_fonts_and_libs = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
"""

# Replace existing font links in <head>
font_pos = html.find('<link rel="preconnect" href="https://fonts.googleapis.com">')
font_end = html.find('rel="stylesheet">', font_pos) + len('rel="stylesheet">')
if font_pos != -1:
    html = html[:font_pos] + head_fonts_and_libs.strip() + html[font_end:]
    print("Fonts and Three.js injected into <head>.")

# ==============================================================================
# 2. SISTEMA DE DESIGN CSS DARK COMMAND-CENTER
# ==============================================================================
dark_hud_css = """
/* ==========================================================================
   DARK COMMAND-CENTER / SCI-FI HUD ANALYTICS DESIGN SYSTEM
   ========================================================================== */
:root {
  --bg: #0a0e14;
  --bg-darker: #06090d;
  --paper: #0a0e14;
  --card: #101622;
  --card-elevated: #141c2c;
  --card-translucent: rgba(16, 22, 34, 0.88);
  
  --ink: #e2e8f0;
  --ink2: #cbd5e1;
  --muted: #788c9f;
  --muted2: #4a5d70;
  --line: rgba(255, 255, 255, 0.08);
  --line2: rgba(255, 255, 255, 0.04);
  --line-cyan: rgba(0, 240, 255, 0.3);
  --line-amber: rgba(255, 158, 0, 0.3);
  
  --neon-cyan: #00f0ff;
  --neon-cyan-glow: rgba(0, 240, 255, 0.5);
  --neon-cyan-bg: rgba(0, 240, 255, 0.1);
  
  --neon-amber: #ff9e00;
  --neon-amber-glow: rgba(255, 158, 0, 0.5);
  --neon-amber-bg: rgba(255, 158, 0, 0.1);
  
  --neon-red: #ff3366;
  --neon-red-glow: rgba(255, 51, 102, 0.5);
  --neon-red-bg: rgba(255, 51, 102, 0.1);
  
  --neon-green: #00ff9d;
  --neon-green-glow: rgba(0, 255, 157, 0.5);
  --neon-green-bg: rgba(0, 255, 157, 0.1);
  
  --neon-violet: #a855f7;
  --neon-violet-bg: rgba(168, 85, 247, 0.1);
  
  --emerald: #00ff9d;
  --emerald-d: #00cc7d;
  --emerald-w: rgba(0, 255, 157, 0.12);
  --amber: #ff9e00;
  --amber-w: rgba(255, 158, 0, 0.12);
  --coral: #ff3366;
  --coral-w: rgba(255, 51, 102, 0.12);
  --sky: #00f0ff;
  --violet: #a855f7;
  
  --gradient-heat: linear-gradient(135deg, #ff9e00 0%, #ff3366 100%);
  --gradient-cyan: linear-gradient(135deg, #00f0ff 0%, #3b82f6 100%);
  --gradient-green: linear-gradient(135deg, #00ff9d 0%, #059669 100%);
  --gradient-card: linear-gradient(180deg, rgba(20, 28, 44, 0.95) 0%, rgba(12, 17, 26, 0.98) 100%);
  
  --font-mono: 'JetBrains Mono', monospace;
  --font-hud: 'Chakra Petch', 'Space Grotesk', sans-serif;
  --font-body: 'Inter', system-ui, -apple-system, sans-serif;
  --disp: 'Space Grotesk', system-ui, sans-serif;
  --body: 'Inter', system-ui, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; background: var(--bg); color-scheme: dark; }

body {
  font-family: var(--font-body);
  background-color: var(--bg);
  background-image: 
    radial-gradient(ellipse 80% 50% at 50% -15%, rgba(0, 240, 255, 0.08), transparent),
    radial-gradient(ellipse 60% 45% at 90% 85%, rgba(255, 158, 0, 0.05), transparent),
    linear-gradient(to right, rgba(0, 240, 255, 0.02) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 240, 255, 0.02) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
  background-attachment: fixed;
  color: var(--ink);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  font-size: 13.5px;
  min-height: 100vh;
}

.wrap { max-width: 1340px; margin: 0 auto; padding: 0 24px; }

/* SCROLLBAR CUSTOM HUD */
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: #080c12; }
::-webkit-scrollbar-thumb { background: #1f2c3f; border-radius: 4px; border: 1px solid rgba(0,240,255,0.15); }
::-webkit-scrollbar-thumb:hover { background: #00f0ff; }

/* HEADER COMMAND CENTER */
header {
  background: linear-gradient(180deg, rgba(14, 20, 32, 0.98) 0%, rgba(10, 14, 20, 0.95) 100%);
  border-bottom: 1px solid rgba(0, 240, 255, 0.2);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.8), 0 1px 0 rgba(0, 240, 255, 0.15);
  padding: 18px 0 22px;
  position: relative;
  z-index: 10;
}
header::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, var(--neon-cyan) 30%, var(--neon-amber) 70%, transparent 100%);
  opacity: 0.8;
}

.hd { display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap; }

.brand .eyebrow {
  font-family: var(--font-hud);
  font-size: 10.5px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--neon-cyan);
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}
.brand h1 {
  font-family: var(--font-hud);
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: #ffffff;
  text-shadow: 0 0 16px rgba(0, 240, 255, 0.3);
}
.brand .sub {
  color: var(--muted);
  font-size: 12px;
  font-family: var(--font-hud);
  letter-spacing: 0.05em;
}

.hud-top-telemetry {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.hud-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 255, 157, 0.08);
  border: 1px solid rgba(0, 255, 157, 0.35);
  color: #a7f3d0;
  padding: 6px 14px;
  border-radius: 6px;
  font-family: var(--font-hud);
  font-size: 11px;
  letter-spacing: 0.08em;
  font-weight: 700;
  box-shadow: 0 0 12px rgba(0, 255, 157, 0.15);
}
.hud-live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--neon-green);
  box-shadow: 0 0 8px var(--neon-green), 0 0 12px var(--neon-green);
  animation: hudPulse 2s infinite ease-in-out;
}
@keyframes hudPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.hud-clock-box {
  background: rgba(16, 22, 34, 0.9);
  border: 1px solid var(--line);
  padding: 6px 12px;
  border-radius: 6px;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--neon-cyan);
  display: flex;
  align-items: center;
  gap: 6px;
}

/* CARDS & HUD BOXES */
.card, .kpi, .hud-card {
  background: var(--card-translucent) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 30px -4px rgba(0, 0, 0, 0.7), inset 0 1px 0 0 rgba(255, 255, 255, 0.05) !important;
  position: relative;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.card:hover, .kpi:hover {
  border-color: rgba(0, 240, 255, 0.25) !important;
  box-shadow: 0 12px 36px -4px rgba(0, 0, 0, 0.8), 0 0 15px rgba(0, 240, 255, 0.1) !important;
}

/* CORNER NOTCHES (HUD ACCENTS) */
.hud-card {
  position: relative;
}
.hud-card::before {
  content: "";
  position: absolute;
  top: -1px; left: -1px;
  width: 10px; height: 10px;
  border-top: 2px solid var(--neon-cyan);
  border-left: 2px solid var(--neon-cyan);
  border-top-left-radius: 12px;
  pointer-events: none;
}
.hud-card::after {
  content: "";
  position: absolute;
  bottom: -1px; right: -1px;
  width: 10px; height: 10px;
  border-bottom: 2px solid var(--neon-cyan);
  border-right: 2px solid var(--neon-cyan);
  border-bottom-right-radius: 12px;
  pointer-events: none;
}

/* KPIS GRID */
.kpis {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
  position: relative;
  z-index: 5;
}
.kpi {
  padding: 16px 18px 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.kpi .k-lab {
  font-family: var(--font-hud) !important;
  font-size: 10.5px !important;
  font-weight: 700 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
  display: flex;
  align-items: center;
  gap: 6px;
}
.kpi .k-val {
  font-family: var(--font-mono) !important;
  font-variant-numeric: tabular-nums !important;
  font-size: 28px !important;
  font-weight: 700 !important;
  line-height: 1.15 !important;
  margin-top: 8px !important;
  color: #ffffff !important;
  letter-spacing: -0.02em !important;
  text-shadow: 0 0 16px rgba(0, 240, 255, 0.25);
}
.kpi .k-sub {
  font-size: 11px !important;
  color: var(--muted2) !important;
  margin-top: 4px !important;
  font-family: var(--font-hud);
}
@media(max-width:1100px){ .kpis { grid-template-columns: repeat(3, 1fr); } }
@media(max-width:640px){ .kpis { grid-template-columns: repeat(2, 1fr); } }

/* GLOBAL FILTER BAR */
.global-filter-bar {
  background: rgba(16, 22, 34, 0.92) !important;
  border: 1px solid rgba(0, 240, 255, 0.2) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6), 0 0 15px rgba(0, 240, 255, 0.05) !important;
  border-radius: 12px !important;
}
.global-filter-bar label {
  font-family: var(--font-hud) !important;
  font-size: 10px !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  color: var(--neon-cyan) !important;
}
.global-filter-bar select, .global-filter-bar input {
  background: #0d131d !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  color: #ffffff !important;
  font-family: var(--font-hud) !important;
  font-size: 12px !important;
  border-radius: 6px !important;
}
.global-filter-bar select:focus, .global-filter-bar input:focus {
  border-color: var(--neon-cyan) !important;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
}

/* TABS COCKPIT SWITCHES */
.tabs {
  display: flex;
  gap: 6px;
  margin: 20px 0 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-wrap: wrap;
}
.tab {
  font-family: var(--font-hud);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  background: rgba(16, 22, 34, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: none;
  padding: 10px 18px;
  cursor: pointer;
  position: relative;
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}
.tab .num {
  font-family: var(--font-mono);
  font-size: 10px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--muted);
  width: 18px; height: 18px;
  border-radius: 4px;
  display: grid;
  place-items: center;
  font-weight: 700;
}
.tab:hover {
  color: var(--neon-cyan);
  background: rgba(0, 240, 255, 0.06);
  border-color: rgba(0, 240, 255, 0.2);
}
.tab.on {
  color: var(--neon-cyan);
  background: rgba(0, 240, 255, 0.1);
  border-color: rgba(0, 240, 255, 0.35);
  box-shadow: 0 -4px 14px rgba(0, 240, 255, 0.15);
}
.tab.on .num {
  background: var(--neon-cyan);
  color: #0a0e14;
}
.tab.on::after {
  content: "";
  position: absolute;
  left: 8px; right: 8px; bottom: -1px;
  height: 2.5px;
  background: var(--neon-cyan);
  border-radius: 2px;
  box-shadow: 0 0 10px var(--neon-cyan);
}
.panel { display: none; padding: 20px 0 60px; animation: fade 0.35s ease; }

/* TABLES & DATA GRIDS */
.tbl-wrap {
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow-x: auto;
  background: var(--card-translucent);
}
table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
th {
  background: #0c121c !important;
  color: var(--muted) !important;
  font-family: var(--font-hud) !important;
  font-size: 10px !important;
  font-weight: 700 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  padding: 12px 14px !important;
  border-bottom: 1px solid var(--line) !important;
  white-space: nowrap;
}
td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: var(--ink);
  vertical-align: middle;
}
tr:hover td {
  background: rgba(0, 240, 255, 0.03) !important;
}

/* MONOSPACE NUMERALS & MICRO-LABELS */
.numeral, .mono {
  font-family: var(--font-mono) !important;
  font-variant-numeric: tabular-nums !important;
}
.micro-label {
  font-family: var(--font-hud);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
}

/* RADIAL GAUGES & THREE GLOBE STYLING */
.hud-telemetry-grid {
  display: grid;
  grid-template-columns: 320px 1fr 300px;
  gap: 16px;
  margin-bottom: 24px;
}
@media(max-width:1150px){ .hud-telemetry-grid { grid-template-columns: 1fr; } }

.hud-radial-gauge-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

#telemetry-globe-canvas {
  width: 100%;
  height: 290px;
  display: block;
  border-radius: 10px;
  background: radial-gradient(circle at 50% 50%, #0d1522 0%, #070a0f 100%);
  cursor: grab;
}
#telemetry-globe-canvas:active { cursor: grabbing; }

/* LIVE MONITOR HUD */
#home-live-section {
  background: linear-gradient(180deg, rgba(16, 22, 34, 0.95) 0%, rgba(10, 14, 20, 0.98) 100%) !important;
  border: 1px solid rgba(0, 240, 255, 0.25) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7), 0 0 16px rgba(0, 240, 255, 0.08) !important;
}
.live-stream-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  background: rgba(14, 20, 30, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-left: 3px solid var(--neon-cyan);
  border-radius: 6px;
  font-size: 12px;
  transition: all 0.15s ease;
}
.live-stream-row:hover {
  background: rgba(0, 240, 255, 0.06);
  border-color: rgba(0, 240, 255, 0.3);
  transform: translateX(3px);
}
"""

# Replace CSS in template
pos_style = html.find('<style>')
pos_style_end = html.find('</style>')
if pos_style != -1 and pos_style_end != -1:
    old_css = html[pos_style+7:pos_style_end]
    # We replace the root, body, card, kpi rules with our dark HUD rules while preserving specialized widget classes
    new_css = dark_hud_css + "\n\n/* PRESERVED WIDGET RULES (DARK-MODE OVERRIDES) */\n" + old_css
    html = html[:pos_style+7] + new_css + html[pos_style_end:]
    print("Dark HUD CSS applied successfully.")

# ==============================================================================
# 3. ATUALIZAR <header> COM STATUS DE COMANDO E RELÓGIO HUD
# ==============================================================================
hud_header_replacement = """
<header>
  <div class="wrap hd">
    <div class="brand" style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
      <div class="logo-box" style="width:44px; height:44px; background:radial-gradient(circle, rgba(0,240,255,0.2) 0%, rgba(10,14,20,0.8) 100%); border:1px solid var(--neon-cyan); border-radius:10px; display:grid; place-items:center; box-shadow:0 0 14px rgba(0,240,255,0.35);">
        <span style="font-size:20px;">🛡️</span>
      </div>
      <div class="brand-text">
        <div class="eyebrow"><span class="hud-live-dot"></span> INFECTOCAST COMMAND CENTER // TELEMETRY HUD</div>
        <h1>Painel de Acompanhamento</h1>
        <div class="sub" id="hd-sub">Base Integrada de Alunos, Acessos e Telemetria em Tempo Real</div>
      </div>
    </div>
    
    <div class="hud-top-telemetry">
      <div class="hud-status-badge">
        <span class="hud-live-dot"></span>
        <span>SISTEMA ATIVO // UTC-3</span>
      </div>
      <div class="hud-clock-box">
        <span style="color:var(--muted); font-size:10px; font-family:var(--font-hud);">HORA:</span>
        <span id="hud-clock" style="font-weight:700;">--:--:--</span>
      </div>
      <button id="btn-sync-live" onclick="syncLiveApiManual()" style="background:linear-gradient(135deg, #ff9e00 0%, #ff3366 100%); color:#0a0e14; border:none; padding:8px 16px; border-radius:6px; font-family:var(--font-hud); font-size:11px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; cursor:pointer; display:flex; align-items:center; gap:6px; box-shadow:0 0 16px rgba(255,158,0,0.4); transition:all 0.2s ease;">
        <span>🔄</span> <span>Sincronizar APIs</span>
      </button>
    </div>
  </div>
</header>
"""

header_pos = html.find('<header>')
header_end = html.find('</header>') + len('</header>')
if header_pos != -1 and header_end != -1:
    html = html[:header_pos] + hud_header_replacement.strip() + html[header_end:]
    print("Header replaced with Dark Command Center terminal header.")

# ==============================================================================
# 4. INJETAR SEÇÃO DO GLOBO 3D THREE.JS E GAUGES RADIAIS NA VISÃO GERAL
# ==============================================================================
telemetry_hero_section = """
    <!-- TELEMETRIA SCI-FI COMMAND CENTER: 3D GLOBE + RADIAL GAUGES -->
    <div class="hud-card hud-telemetry-grid" style="padding:18px; margin-bottom:24px;">
      
      <!-- COLUNA 1: GAUGES RADIAIS CONCÊNTRICOS (GLOW/BLOOM) -->
      <div style="display:flex; flex-direction:column; justify-content:space-between; background:rgba(12, 17, 26, 0.7); border:1px solid var(--line); border-radius:10px; padding:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <span class="micro-label" style="color:var(--neon-cyan);">// INDICADORES RADIAIS</span>
          <span style="font-family:var(--font-mono); font-size:10px; color:var(--muted);">HUD_GAUGE_V2</span>
        </div>
        
        <div class="hud-radial-gauge-container">
          <svg width="220" height="220" viewBox="0 0 220 220" style="overflow:visible;">
            <defs>
              <filter id="hud-bloom" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <linearGradient id="grad-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00f0ff" />
                <stop offset="100%" stop-color="#3b82f6" />
              </linearGradient>
              <linearGradient id="grad-amber" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ff9e00" />
                <stop offset="100%" stop-color="#ff3366" />
              </linearGradient>
              <linearGradient id="grad-green" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00ff9d" />
                <stop offset="100%" stop-color="#059669" />
              </linearGradient>
            </defs>
            
            <!-- Trilhas de Fundo -->
            <circle cx="110" cy="110" r="90" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8" />
            <circle cx="110" cy="110" r="72" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8" />
            <circle cx="110" cy="110" r="54" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8" />
            
            <!-- Arcos Radiais com Glow -->
            <circle id="gauge-arc-1" cx="110" cy="110" r="90" fill="none" stroke="url(#grad-cyan)" stroke-width="8" stroke-dasharray="565.48" stroke-dashoffset="140" stroke-linecap="round" filter="url(#hud-bloom)" transform="rotate(-90 110 110)" />
            <circle id="gauge-arc-2" cx="110" cy="110" r="72" fill="none" stroke="url(#grad-amber)" stroke-width="8" stroke-dasharray="452.39" stroke-dashoffset="180" stroke-linecap="round" filter="url(#hud-bloom)" transform="rotate(-90 110 110)" />
            <circle id="gauge-arc-3" cx="110" cy="110" r="54" fill="none" stroke="url(#grad-green)" stroke-width="8" stroke-dasharray="339.29" stroke-dashoffset="90" stroke-linecap="round" filter="url(#hud-bloom)" transform="rotate(-90 110 110)" />
            
            <!-- Núcleo Central -->
            <circle cx="110" cy="110" r="38" fill="#0d1420" stroke="rgba(0,240,255,0.3)" stroke-width="1.5" />
            <text x="110" y="106" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="16" font-weight="700" fill="#00f0ff" id="gauge-val-pct">82%</text>
            <text x="110" y="122" text-anchor="middle" font-family="'Chakra Petch', sans-serif" font-size="8.5" font-weight="600" fill="#788c9f" letter-spacing="1">EFICIÊNCIA</text>
          </svg>
        </div>
        
        <div style="display:flex; justify-content:space-around; margin-top:8px; border-top:1px solid var(--line); padding-top:10px;">
          <div style="text-align:center;">
            <div style="font-size:9px; color:var(--neon-cyan); font-family:var(--font-hud);">● ATIVIDADE</div>
            <div style="font-family:var(--font-mono); font-size:13px; font-weight:700; color:#fff;" id="radial-stat-ativ">76%</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:9px; color:var(--neon-amber); font-family:var(--font-hud);">● ADIMPLÊNCIA</div>
            <div style="font-family:var(--font-mono); font-size:13px; font-weight:700; color:#fff;" id="radial-stat-adim">88%</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:9px; color:var(--neon-green); font-family:var(--font-hud);">● RETENÇÃO</div>
            <div style="font-family:var(--font-mono); font-size:13px; font-weight:700; color:#fff;" id="radial-stat-ret">81%</div>
          </div>
        </div>
      </div>
      
      <!-- COLUNA 2: GLOBO 3D INTERATIVO (THREE.JS) -->
      <div style="display:flex; flex-direction:column; background:rgba(12, 17, 26, 0.7); border:1px solid var(--line); border-radius:10px; padding:16px; position:relative; overflow:hidden;">
        <div style="display:flex; justify-content:space-between; align-items:center; position:relative; z-index:2; margin-bottom:6px;">
          <div>
            <span class="micro-label" style="color:var(--neon-cyan);"><span class="hud-live-dot" style="display:inline-block; margin-right:4px;"></span>DISPERSÃO GEOGRÁFICA & ACESSOS</span>
            <div style="font-size:11px; color:var(--muted); font-family:var(--font-hud);">Topologia de Alunos no Brasil e Redes de Conexão</div>
          </div>
          <div style="font-family:var(--font-mono); font-size:11px; color:var(--neon-green); background:rgba(0,255,157,0.1); padding:3px 8px; border-radius:4px; border:1px solid rgba(0,255,157,0.3);">
            LIVE 3D HUD
          </div>
        </div>
        
        <div style="position:relative; flex:1; min-height:260px;">
          <div id="telemetry-globe-mount" style="width:100%; height:100%; min-height:260px; border-radius:8px; overflow:hidden; position:relative;"></div>
          
          <!-- HUD Overlays on Globe -->
          <div style="position:absolute; bottom:8px; left:12px; pointer-events:none; font-family:var(--font-mono); font-size:9.5px; color:rgba(0,240,255,0.7); line-height:1.4;">
            <div>COORD: -15.7801° S, -47.9292° W [BR]</div>
            <div>STATUS: TELEMETRY STREAMING ACTIVE</div>
          </div>
          <div style="position:absolute; bottom:8px; right:12px; pointer-events:none; font-family:var(--font-hud); font-size:9.5px; color:var(--muted);">
            ARRASTE PARA ROTACIONAR
          </div>
        </div>
      </div>
      
      <!-- COLUNA 3: TELEMETRIA DE PLATAFORMAS & REDE -->
      <div style="display:flex; flex-direction:column; justify-content:space-between; background:rgba(12, 17, 26, 0.7); border:1px solid var(--line); border-radius:10px; padding:16px;">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span class="micro-label" style="color:var(--neon-cyan);">// NÓS DE CONEXÃO</span>
            <span style="font-family:var(--font-mono); font-size:10px; color:var(--neon-green);">CONNECTED</span>
          </div>
          
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div style="background:#090d14; border:1px solid var(--line); border-radius:6px; padding:10px 12px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-size:10px; color:var(--muted); font-family:var(--font-hud);">ACADEMY LMS</div>
                <div style="font-family:var(--font-mono); font-size:14px; font-weight:700; color:#fff;" id="hud-node-acad">98 Alunos</div>
              </div>
              <span style="color:var(--neon-cyan); font-size:11px; font-family:var(--font-hud); font-weight:700;">API LIVE</span>
            </div>
            
            <div style="background:#090d14; border:1px solid var(--line); border-radius:6px; padding:10px 12px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-size:10px; color:var(--muted); font-family:var(--font-hud);">CATIVA DIGITAL</div>
                <div style="font-family:var(--font-mono); font-size:14px; font-weight:700; color:#fff;" id="hud-node-cat">310 Alunos</div>
              </div>
              <span style="color:var(--neon-green); font-size:11px; font-family:var(--font-hud); font-weight:700;">API LIVE</span>
            </div>
            
            <div style="background:#090d14; border:1px solid var(--line); border-radius:6px; padding:10px 12px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-size:10px; color:var(--muted); font-family:var(--font-hud);">FINANCEIRO GATEWAYS</div>
                <div style="font-family:var(--font-mono); font-size:14px; font-weight:700; color:#fff;" id="hud-node-fin">Vindi + Asaas</div>
              </div>
              <span style="color:var(--neon-amber); font-size:11px; font-family:var(--font-hud); font-weight:700;">SYNCED</span>
            </div>
          </div>
        </div>
        
        <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--line);">
          <div style="display:flex; justify-content:space-between; font-family:var(--font-hud); font-size:10px; color:var(--muted); margin-bottom:4px;">
            <span>USO DE BANDA & EVENTOS</span>
            <span class="numeral" style="color:#fff;" id="hud-events-total-badge">--</span>
          </div>
          <div style="height:6px; background:#0a0e14; border-radius:3px; overflow:hidden; border:1px solid rgba(255,255,255,0.06);">
            <div id="hud-events-bar" style="height:100%; width:85%; background:linear-gradient(90deg, #00f0ff, #ff9e00); border-radius:3px; box-shadow:0 0 8px rgba(0,240,255,0.5);"></div>
          </div>
        </div>
      </div>
      
    </div>
"""

# Inject telemetry hero section right above home-kpis-grid in Tab 0
target_kpis = '<div class="kpis" id="home-kpis-grid"'
pos_kpis = html.find(target_kpis)
if pos_kpis != -1:
    html = html[:pos_kpis] + telemetry_hero_section + "\n    " + html[pos_kpis:]
    print("Telemetry Hero Section (3D Globe + Radial Gauges) injected into Tab 0.")

# ==============================================================================
# 5. INJETAR SCRIPTS DO GLOBO THREE.JS E RELÓGIO HUD NO FINAL DO SCRIPT
# ==============================================================================
hud_runtime_scripts = """
// =============================================================================
// RELÓGIO HUD EM TEMPO REAL (BRASÍLIA BRT)
// =============================================================================
function initHudClock() {
  function tick() {
    const el = document.getElementById('hud-clock');
    if (!el) return;
    const now = new Date();
    const pad = n => n < 10 ? '0' + n : n;
    el.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  }
  tick();
  setInterval(tick, 1000);
}

// =============================================================================
// THREE.JS 3D TELEMETRY GLOBE (SCI-FI HUD POINT-CLOUD)
// =============================================================================
let globeScene, globeCamera, globeRenderer, globePoints, globeArcs;
let isDraggingGlobe = false, prevMouseX = 0, prevMouseY = 0;

function initThreeGlobe() {
  const container = document.getElementById('telemetry-globe-mount');
  if (!container || typeof THREE === 'undefined') return;

  const width = container.clientWidth || 400;
  const height = container.clientHeight || 260;

  globeScene = new THREE.Scene();
  globeCamera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  globeCamera.position.z = 210;

  globeRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  globeRenderer.setSize(width, height);
  globeRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.innerHTML = '';
  container.appendChild(globeRenderer.domElement);

  // 1. Esfera de Partículas / Malha Wireframe Densa
  const sphereGeo = new THREE.SphereGeometry(75, 42, 28);
  const sphereMat = new THREE.PointsMaterial({
    color: 0x00f0ff,
    size: 1.4,
    transparent: true,
    opacity: 0.55
  });
  globePoints = new THREE.Points(sphereGeo, sphereMat);
  globeScene.add(globePoints);

  // 2. Anéis equatoriais e meridianos de latitude HUD
  const ringGeo = new THREE.RingGeometry(75, 75.8, 64);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, side: THREE.DoubleSide, transparent: true, opacity: 0.25 });
  const equator = new THREE.Mesh(ringGeo, ringMat);
  equator.rotation.x = Math.PI / 2;
  globeScene.add(equator);

  // 3. Nós de Acesso (Pontos luminosos simulando capitais brasileiras e alunos)
  const nodesGeo = new THREE.BufferGeometry();
  const nodeCoords = [
    [-23.55, -46.63], // São Paulo
    [-22.90, -43.17], // Rio de Janeiro
    [-15.78, -47.92], // Brasília
    [-19.91, -43.93], // Belo Horizonte
    [-12.97, -38.50], // Salvador
    [-8.04, -34.87],  // Recife
    [-30.03, -51.23], // Porto Alegre
    [-25.42, -49.27], // Curitiba
    [-3.73, -38.52],  // Fortaleza
    [-1.45, -48.50]   // Belém
  ];

  const positions = [];
  const colors = [];
  const colorCyan = new THREE.Color(0x00f0ff);
  const colorAmber = new THREE.Color(0xff9e00);

  nodeCoords.forEach((coord, idx) => {
    const lat = coord[0] * (Math.PI / 180);
    const lon = -coord[1] * (Math.PI / 180);
    const r = 76.5;
    const x = r * Math.cos(lat) * Math.cos(lon);
    const y = r * Math.sin(lat);
    const z = r * Math.cos(lat) * Math.sin(lon);
    positions.push(x, y, z);
    const c = idx % 2 === 0 ? colorCyan : colorAmber;
    colors.push(c.r, c.g, c.b);
  });

  nodesGeo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  nodesGeo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

  const nodesMat = new THREE.PointsMaterial({
    size: 4.5,
    vertexColors: true,
    transparent: true,
    opacity: 0.95
  });
  const nodesMesh = new THREE.Points(nodesGeo, nodesMat);
  globeScene.add(nodesMesh);

  // Interatividade Mouse Drag
  container.addEventListener('mousedown', e => {
    isDraggingGlobe = true;
    prevMouseX = e.clientX;
    prevMouseY = e.clientY;
  });
  window.addEventListener('mouseup', () => isDraggingGlobe = false);
  window.addEventListener('mousemove', e => {
    if (!isDraggingGlobe || !globePoints) return;
    const dx = e.clientX - prevMouseX;
    const dy = e.clientY - prevMouseY;
    globePoints.rotation.y += dx * 0.006;
    globePoints.rotation.x += dy * 0.006;
    equator.rotation.z += dx * 0.006;
    nodesMesh.rotation.y += dx * 0.006;
    nodesMesh.rotation.x += dy * 0.006;
    prevMouseX = e.clientX;
    prevMouseY = e.clientY;
  });

  // Loop de Animação 60fps
  function animate() {
    requestAnimationFrame(animate);
    if (!isDraggingGlobe && globePoints) {
      globePoints.rotation.y += 0.0025;
      nodesMesh.rotation.y += 0.0025;
      equator.rotation.z += 0.0025;
    }
    globeRenderer.render(globeScene, globeCamera);
  }
  animate();

  // Resize Handler
  window.addEventListener('resize', () => {
    if (!container || !globeRenderer || !globeCamera) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    globeCamera.aspect = w / h;
    globeCamera.updateProjectionMatrix();
    globeRenderer.setSize(w, h);
  });
}

// Inicializar na carga da página
window.addEventListener('DOMContentLoaded', () => {
  initHudClock();
  setTimeout(initThreeGlobe, 300);
});
"""

# Append script to the end of <script>
pos_script_close = html.rfind('</script>')
if pos_script_close != -1:
    html = html[:pos_script_close] + "\n" + hud_runtime_scripts + "\n" + html[pos_script_close:]
    print("Three.js Globe & HUD Clock runtime scripts appended.")

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Template updated successfully! Ready to run gerador.py.")

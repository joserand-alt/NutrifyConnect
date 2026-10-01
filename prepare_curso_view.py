import os

dash_dir = r'C:/Users/DELL/Desktop/Dash_InfectoCast'
template_path = os.path.join(dash_dir, 'template.html')

with open(template_path, 'r', encoding='utf-8') as f:
    t = f.read()

# 1. Update <nav class="tabs"> to include the new tab
old_nav = '''<nav class="tabs" id="tabs">
    <button class="tab on" data-p="exec"><span class="num">★</span>Visão Executiva</button>
    <button class="tab" data-p="home"><span class="num">0</span>Visão Geral</button>'''

if old_nav not in t:
    # let's search for <nav class="tabs" id="tabs">
    idx_nav = t.find('<nav class="tabs"')
    idx_nav_end = t.find('</nav>', idx_nav)
    print('Found nav tabs at:', idx_nav)

new_nav = '''<nav class="tabs" id="tabs">
    <button class="tab on" data-p="exec"><span class="num">★</span>Visão Executiva</button>
    <button class="tab" data-p="curso" id="btn-tab-curso"><span class="num">🎯</span>Visão por Curso</button>
    <button class="tab" data-p="home"><span class="num">0</span>Visão Geral</button>'''

# 2. Add panel #p-curso after #p-exec
old_exec_panel = '''  <!-- PANEL: VISÃO EXECUTIVA (COCKPIT ESTRATÉGICO) -->
  <section class="panel on" id="p-exec">
    <div id="exec-content-mount"></div>
  </section>'''

if old_exec_panel not in t:
    idx_p = t.find('id="p-exec"')
    print('Found p-exec at:', idx_p)

new_curso_panel = '''  <!-- PANEL: VISÃO EXECUTIVA (COCKPIT ESTRATÉGICO) -->
  <section class="panel on" id="p-exec">
    <div id="exec-content-mount"></div>
  </section>

  <!-- PANEL: VISÃO POR CURSO (COCKPIT 360°) -->
  <section class="panel" id="p-curso">
    <div id="curso-content-mount"></div>
  </section>'''

print('Ready to patch HTML structure!')

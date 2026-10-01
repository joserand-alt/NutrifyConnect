import os

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Clean up <nav class="tabs" id="tabs">
idx_nav_start = text.find('<nav class="tabs"')
idx_nav_end = text.find('</nav>', idx_nav_start) + len('</nav>')

clean_nav = '''<nav class="tabs" id="tabs">
    <button class="tab on" data-p="exec"><span class="num">★</span>Visão Executiva</button>
    <button class="tab" data-p="curso" id="btn-tab-curso"><span class="num">🎯</span>Visão por Curso</button>
    <button class="tab" data-p="home"><span class="num">0</span>Visão Geral</button>
    <button class="tab" data-p="prog"><span class="num">1</span>Progresso por aluno</button>
    <button class="tab" data-p="mod"><span class="num">2</span>Engajamento por módulo</button>
    <button class="tab" data-p="ret"><span class="num">3</span>Retenção &amp; abandono</button>
    <button class="tab" data-p="tl"><span class="num">4</span>Linha temporal</button>
    <button class="tab" data-p="funil"><span class="num">5</span>Funil de Leads</button>
    <button class="tab" data-p="origem"><span class="num">6</span>Origem de Matrículas</button>
    <button class="tab" data-p="fin" id="btn-tab-fin"><span class="num">$</span>Financeiro &amp; Projeção</button>
  </nav>'''

text = text[:idx_nav_start] + clean_nav + text[idx_nav_end:]

# 2. Fix unifiedFin in drawCursoView
old_cfin = "const cFin = unifiedFin.coursesMap[activeCourse] || {"
new_cfin = "const coursesData = (unifiedFin && (unifiedFin.courses || unifiedFin.coursesMap)) || {};\n    const cFin = coursesData[activeCourse] || {"

text = text.replace(old_cfin, new_cfin)

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully cleaned up nav tabs and fixed cFin reference!')

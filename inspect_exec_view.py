with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('function drawExecView(')
print('drawExecView pos:', idx)
if idx != -1:
    print(html[idx:idx+1500])

idx_curso = html.find('function drawCursoView(')
print('drawCursoView pos:', idx_curso)
if idx_curso != -1:
    print(html[idx_curso:idx_curso+1000])

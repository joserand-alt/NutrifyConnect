import sys
code = open('index.html', encoding='utf-8').read()
code = code.replace('const allEnrichedStudents = rawStudents.map(s => {', 'const allEnrichedStudents = [...matriculasConfirmadas, ...matriculasPendentes].map(s => {')
open('index.html', 'w', encoding='utf-8').write(code)
code_dash = open('dashboard_gerado.html', encoding='utf-8').read()
code_dash = code_dash.replace('const allEnrichedStudents = rawStudents.map(s => {', 'const allEnrichedStudents = [...matriculasConfirmadas, ...matriculasPendentes].map(s => {')
open('dashboard_gerado.html', 'w', encoding='utf-8').write(code_dash)

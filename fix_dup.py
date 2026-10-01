import sys
code = open('template.html', encoding='utf-8').read()
code = code.replace('const allEnrichedStudents = rawStudents.map(s => {', 'const allEnrichedStudents = [...matriculasConfirmadas, ...matriculasPendentes].map(s => {')
open('template.html', 'w', encoding='utf-8').write(code)

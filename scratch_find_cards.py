with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'ULTIMAS 48 HORAS|ÚLTIMAS 48 HORAS|getMatriculasAuditoriaData|mat-conf-48h|mat-pend-48h|mat-conf-30d|mat-pend-30d', text, re.I)]
for m in matches:
    print('--- MATCH AT', m, '---')
    print(text[m-50:m+200])

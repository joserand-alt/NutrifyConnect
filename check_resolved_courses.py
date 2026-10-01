import json

with open('dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])

students = data.get('students', [])
print(f"Total students: {len(students)}")

courses_cnt = {}
for s in students:
    c = s.get('curso') or 'SEM CURSO'
    courses_cnt[c] = courses_cnt.get(c, 0) + 1

print("\nDistribuição dos Cursos:")
for c, cnt in sorted(courses_cnt.items(), key=lambda x: x[1], reverse=True):
    print(f" - {c}: {cnt} alunos")

for target in ['danielesarto@yahoo.com.br', 'beatriz.grinsztejn@gmail.com', 'adrianammas@gmail.com', 'daniela.torchi@gmail.com']:
    matches = [s for s in students if s.get('email') == target]
    if matches:
        s = matches[0]
        print(f"\n{target} -> Curso: {s.get('curso')} | Origem: {s.get('curso_origem')} | Aulas: {s.get('aulas_feitas')} | Logins: {s.get('logins')}")

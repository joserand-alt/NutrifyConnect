import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])

students = data.get('students', [])
print(f"Total students in dataset: {len(students)}")

pg_students = [s for s in students if s.get('curso') == 'PLATAFORMA GERAL' or not s.get('curso')]
print(f"Students with PLATAFORMA GERAL: {len(pg_students)}")

# Let's inspect what data these PG students have
print("\n--- Inspecting first 20 PLATAFORMA GERAL students ---")
for s in pg_students[:20]:
    em = s.get('email')
    nm = s.get('nome')
    vindi_info = s.get('vindi')
    asaas_info = s.get('asaas')
    v_plano = vindi_info.get('plano') if vindi_info and isinstance(vindi_info, dict) else None
    a_plano = asaas_info.get('plano') or asaas_info.get('description') if asaas_info and isinstance(asaas_info, dict) else None
    events_cnt = len(s.get('events', []))
    aulas = s.get('aulas_feitas') or s.get('aulas_iniciadas')
    print(f"- {nm} ({em}) | Plat: {s.get('plataforma')} | Logins: {s.get('logins')} | Aulas: {aulas} | Events: {events_cnt} | Vindi Plan: {v_plano} | Asaas Plan: {a_plano}")

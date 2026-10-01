import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])

students = data.get('students', [])
gis = [s for s in students if 'gislayne' in (s.get('email') or '').lower() or 'gislayne' in (s.get('nome') or '').lower()]

print("Found students matching gislayne:", len(gis))
for s in gis:
    print("Student object:")
    for k, v in s.items():
        if k != 'events' and k != 'modulos_detalhe':
            print(f"  {k}: {v}")

# Check in Vindi & Asaas faturas
vindi = data.get('financeiro', {}).get('faturas_tabela', [])
asaas = data.get('financeiro_asaas', {}).get('faturas_tabela', [])

print("\nVindi faturas for gislayne:")
for f in vindi:
    if 'gislayne' in (f.get('email') or '').lower() or 'gislayne' in (f.get('aluno') or '').lower():
        print(" ", f)

print("\nAsaas faturas for gislayne:")
for f in asaas:
    if 'gislayne' in (f.get('email') or '').lower() or 'gislayne' in (f.get('aluno') or '').lower():
        print(" ", f)

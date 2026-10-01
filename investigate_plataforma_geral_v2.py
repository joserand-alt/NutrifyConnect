import json, re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const DATA = (\{.*?\});\s*\n', content, re.DOTALL)
data = json.loads(match.group(1))
students = data.get('students', [])

email_target = 'welisoncatarino13@hotmail.com'

# 1. Find ALL student entries for this email (may have multiple courses)
print("=== TODAS AS ENTRADAS DO ALUNO ===")
entries = [s for s in students if (s.get('email') or '').lower().strip() == email_target]
for s in entries:
    print(f"  Curso: {s.get('curso')} | Plataforma: {s.get('plataforma')} | inscricao_id: {s.get('inscricao_id', 'N/A')}")

# 2. Check how many students are "PLATAFORMA GERAL"
plat_geral = [s for s in students if s.get('curso') == 'PLATAFORMA GERAL']
print(f"\n=== TOTAL 'PLATAFORMA GERAL': {len(plat_geral)} ===")
for s in plat_geral:
    email = (s.get('email') or '').lower().strip()
    nome = s.get('nome', '?')
    has_vindi = bool(s.get('vindi'))
    has_asaas = bool(s.get('asaas'))
    # Check if they have other entries with real courses
    other_entries = [x for x in students if (x.get('email') or '').lower().strip() == email and x.get('curso') != 'PLATAFORMA GERAL']
    other_courses = [x.get('curso') for x in other_entries]
    gateway = 'Vindi' if has_vindi else ('Asaas' if has_asaas else 'Nenhum')
    print(f"  {nome} ({email}) | Gateway: {gateway} | Outros cursos: {other_courses if other_courses else 'NENHUM'}")

# 3. Check Asaas faturas descriptions for plataforma geral students
print(f"\n=== DETALHES ASAAS (Plataforma Geral com Asaas) ===")
for s in plat_geral:
    asaas = s.get('asaas')
    if asaas and asaas.get('faturas'):
        email = (s.get('email') or '').lower().strip()
        faturas = asaas['faturas']
        descs = set()
        for ft in faturas:
            d = ft.get('descricao', 'N/A')
            descs.add(d)
        print(f"  {s.get('nome')} ({email}): descriptions = {descs}")

import json, os

email = 'danielesarto@yahoo.com.br'

# 1. Check in dashboard_gerado.html
with open('dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()
s_idx = html.find('const DATA = {')
e_idx = html.find('};\n', s_idx)
if e_idx == -1: e_idx = html.find('};', s_idx)
data = json.loads(html[s_idx + len('const DATA = '):e_idx + 1])

print("=== 1. NO DASHBOARD (DATA.students) ===")
for s in data['students']:
    if s.get('email','').lower().strip() == email:
        print(f"  Nome: {s.get('nome')}")
        print(f"  Curso: {s.get('curso')}")
        print(f"  Curso Origem: {s.get('curso_origem')}")
        print(f"  Curso Inferido: {s.get('curso_inferido')}")
        print(f"  Plataforma: {s.get('plataforma')}")
        print(f"  Data Insc: {s.get('data_insc')}")
        v = s.get('vindi')
        if v:
            print(f"  Vindi Plano: {v.get('plano')}")
            print(f"  Vindi Status: {v.get('status_assinatura')} / {v.get('status_financeiro')}")
        a = s.get('asaas')
        if a:
            print(f"  Asaas: {a}")
        print("---")

# 2. Check in vindi_cache.json
print("\n=== 2. VINDI CACHE ===")
with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi = json.load(f)
v_data = vindi.get('data', {}).get(email)
if v_data:
    print(f"  Plano: {v_data.get('plano')}")
    print(f"  Status: {v_data.get('status_assinatura')}")
    print(f"  Curso (campo): {v_data.get('curso')}")
else:
    print("  NÃO ENCONTRADO no vindi_cache")

# 3. Check in rd_tagged_matriculas.json
print("\n=== 3. RD TAGGED MATRICULAS ===")
with open('rd_tagged_matriculas.json', 'r', encoding='utf-8') as f:
    tagged = json.load(f)
for k, v in tagged.items():
    if isinstance(v, dict) and v.get('email','').lower().strip() == email:
        print(f"  Key: {k}")
        print(f"  Curso: {v.get('curso')}")
        print(f"  Tags: {v.get('tags_aplicadas')}")

# 4. Check in asaas_cache.json
print("\n=== 4. ASAAS CACHE ===")
if os.path.exists('asaas_cache.json'):
    with open('asaas_cache.json', 'r', encoding='utf-8') as f:
        asaas = json.load(f)
    a_data = asaas.get('data', {}).get(email)
    if a_data:
        print(f"  Asaas data: {json.dumps(a_data, indent=2, ensure_ascii=False)[:500]}")
    else:
        print("  NÃO ENCONTRADO no asaas_cache")

# 5. Check all remaining PLATAFORMA GERAL students
print("\n=== 5. TODOS OS ALUNOS AINDA EM PLATAFORMA GERAL ===")
pg_students = [s for s in data['students'] if s.get('curso','').upper().strip() == 'PLATAFORMA GERAL']
print(f"  Total: {len(pg_students)}")
for s in pg_students:
    em = s.get('email','')
    nm = s.get('nome','')
    v = s.get('vindi')
    v_plano = v.get('plano','') if v else ''
    a = s.get('asaas')
    a_desc = ''
    if a and isinstance(a, dict):
        fts = a.get('faturas', [])
        if fts:
            a_desc = str(fts[0].get('description', fts[0].get('descricao', '')))[:60]
    print(f"  - {nm} ({em}) | Vindi: '{v_plano}' | Asaas desc: '{a_desc}'")

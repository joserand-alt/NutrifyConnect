import json, os

# All 17 PG emails
pg_emails = [
    'vivianvidal01@gmail.com', 'beatriz.grinsztejn@gmail.com', 'jucazita@yahoo.com.br',
    'limafilipe13@hotmail.com', 'souzaxp4i@gmail.com', 'adrianammas@gmail.com',
    'danielesarto@yahoo.com.br', 'welisoncatarino13@hotmail.com', 'secco.mayara@gmail.com',
    'm.mlbmsantos@gmail.com', 'marcosdavi2006@yahoo.com.br', 'raolisw@gmail.com',
    'costalg1@gmail.com', 'laura_orlandi@hotmail.com', 'mclaramdp@gmail.com',
    'markus_braga@hotmail.com', 'daniela.torchi@gmail.com'
]

# 1. Search RAW Asaas bills file for subscription descriptions
print("=== 1. ASAAS CACHE - buscar descrição da cobrança por email ===")
with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

for email in pg_emails:
    data = asaas.get('data', {}).get(email)
    if data:
        print(f"\n  [{email}]")
        print(f"    customer_name: {data.get('customer_name')}")
        print(f"    aluno_id_extref: {data.get('aluno_id_extref')}")
        # Look for description in faturas
        for fat in data.get('faturas', [])[:3]:
            desc = fat.get('description', fat.get('descricao', ''))
            ext_ref = fat.get('externalReference', fat.get('external_reference', ''))
            print(f"    fatura: {fat.get('id')} | desc: '{desc}' | extref: '{ext_ref}' | valor: {fat.get('valor')}")
    else:
        print(f"\n  [{email}] NÃO encontrado no Asaas")

# 2. Search Vindi cache for these emails 
print("\n\n=== 2. VINDI CACHE - buscar plano por email ===")
with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi = json.load(f)
vindi_data = vindi.get('data', {})

for email in pg_emails:
    data = vindi_data.get(email)
    if data:
        print(f"\n  [{email}]")
        print(f"    plano: {data.get('plano')}")
        print(f"    status: {data.get('status_assinatura')}")
        print(f"    produto: {data.get('produto')}")
    else:
        print(f"\n  [{email}] NÃO encontrado na Vindi")

# 3. RD Station data 
print("\n\n=== 3. RD TAGGED MATRICULAS - buscar tags por email ===")
with open('rd_tagged_matriculas.json', 'r', encoding='utf-8') as f:
    rd = json.load(f)
rd_by_email = {}
for k, v in rd.items():
    if isinstance(v, dict):
        em = v.get('email', '').lower().strip()
        if em:
            rd_by_email[em] = v

for email in pg_emails:
    data = rd_by_email.get(email)
    if data:
        print(f"\n  [{email}]")
        print(f"    curso: {data.get('curso')}")
        print(f"    tags: {data.get('tags_aplicadas')}")
        print(f"    cf_curso: {data.get('cf_curso')}")
    else:
        print(f"\n  [{email}] NÃO encontrado no RD")

# 4. Deep dive into the dashboard DATA for each one's source info
print("\n\n=== 4. DASHBOARD DATA - info completa de cada PG ===")
with open('dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()
s_idx = html.find('const DATA = {')
e_idx = html.find('};\n', s_idx)
if e_idx == -1: e_idx = html.find('};', s_idx)
data = json.loads(html[s_idx + len('const DATA = '):e_idx + 1])

for s in data['students']:
    em = s.get('email','').lower().strip()
    if em in pg_emails:
        print(f"\n  [{em}]")
        print(f"    nome: {s.get('nome')}")
        print(f"    curso: {s.get('curso')}")
        print(f"    curso_origem: {s.get('curso_origem')}")
        print(f"    plataforma: {s.get('plataforma')}")
        print(f"    data_insc: {s.get('data_insc')}")
        print(f"    turma: {s.get('turma')}")
        print(f"    vindi: {bool(s.get('vindi'))}")
        if s.get('vindi'):
            print(f"    vindi_plano: {s.get('vindi',{}).get('plano')}")
        print(f"    asaas: {bool(s.get('asaas'))}")
        if s.get('asaas'):
            print(f"    asaas_total: {s.get('asaas',{}).get('total_pago')}")
            fats = s.get('asaas',{}).get('faturas',[])
            if fats:
                print(f"    asaas_valor: {fats[0].get('valor')}")

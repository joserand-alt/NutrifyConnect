"""
Query Academy API to find enrollments/courses for PG students.
Uses the aluno_id_extref from asaas_cache to query /api/alunos/{id}
"""
import json, os, urllib.request

ACADEMY_TOKEN = "idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ"

def academy_get(endpoint):
    url = f"https://academy.infectocast.com.br/api/{endpoint}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {ACADEMY_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

# Load PG student IDs
with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

pg_emails_ids = {
    'danielesarto@yahoo.com.br': '100214',
    'beatriz.grinsztejn@gmail.com': '100251',
    'vivianvidal01@gmail.com': '100260',
    'jucazita@yahoo.com.br': '100253',
    'limafilipe13@hotmail.com': '100240',
    'souzaxp4i@gmail.com': '100229',
    'adrianammas@gmail.com': '100215',
    'welisoncatarino13@hotmail.com': '100203',
    'secco.mayara@gmail.com': '100263',
    'm.mlbmsantos@gmail.com': '100262',
    'marcosdavi2006@yahoo.com.br': '100249',
    'raolisw@gmail.com': '100248',
    'costalg1@gmail.com': '100242',
    'laura_orlandi@hotmail.com': '100233',
    'mclaramdp@gmail.com': '100226',
    'markus_braga@hotmail.com': '100224',
    'daniela.torchi@gmail.com': '100222',
}

# Get IDs from asaas cache
for email in pg_emails_ids:
    data = asaas.get('data', {}).get(email)
    if data:
        pg_emails_ids[email] = data.get('aluno_id_extref', pg_emails_ids[email])

print("=== Querying Academy API for enrollments/courses ===\n")

# Query first 5 as sample
for email, aluno_id in list(pg_emails_ids.items())[:5]:
    print(f"[{email}] aluno_id={aluno_id}")
    
    # Get student info
    result = academy_get(f"alunos/{aluno_id}")
    if result and result.get('success') and result.get('data'):
        st = result['data']
        print(f"  nome: {st.get('nome')}")
        print(f"  email: {st.get('email')}")
        
        # Check turmas/enrollments/courses
        turmas = st.get('turmas', [])
        cursos = st.get('cursos', [])
        inscricoes = st.get('inscricoes', [])
        
        if turmas:
            print(f"  turmas: {json.dumps(turmas, ensure_ascii=False)[:200]}")
        if cursos:
            print(f"  cursos: {json.dumps(cursos, ensure_ascii=False)[:200]}")
        if inscricoes:
            print(f"  inscricoes: {json.dumps(inscricoes, ensure_ascii=False)[:200]}")
        
        # Print all keys we get
        print(f"  available_keys: {list(st.keys())}")
    else:
        print(f"  No data from Academy API")
    
    print()

# Also try the /api/inscricoes endpoint
print("\n=== Trying /api/inscricoes endpoint ===")
result = academy_get("inscricoes?limit=5")
if result:
    print(f"  Keys: {list(result.keys()) if isinstance(result, dict) else 'list'}")
    if isinstance(result, dict) and result.get('data'):
        for i in result['data'][:3]:
            print(f"  Inscricao: {json.dumps(i, ensure_ascii=False)[:200]}")

# Try /api/cursos
print("\n=== Trying /api/cursos endpoint ===")
result = academy_get("cursos")
if result:
    if isinstance(result, dict):
        print(f"  Keys: {list(result.keys())}")
        if result.get('data'):
            for c in (result['data'] if isinstance(result['data'], list) else [result['data']])[:10]:
                print(f"  Curso: {json.dumps(c, ensure_ascii=False)[:200]}")
    elif isinstance(result, list):
        for c in result[:10]:
            print(f"  Curso: {json.dumps(c, ensure_ascii=False)[:200]}")

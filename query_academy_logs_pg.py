"""
Query Academy API /api/alunos/{id}/log for PG students to find course from access logs.
The gerador.py already does this in fetch_logs_from_api() - let's check what logs exist.
"""
import json, os, urllib.request

ACADEMY_TOKEN = "idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ"

def academy_get(endpoint):
    url = f"https://academy.infectocast.com.br/api/{endpoint}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {ACADEMY_TOKEN}",
        "Accept": "application/json", "User-Agent": "Mozilla/5.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

# Load asaas cache to get aluno_id_extref
with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

pg_emails = {
    'danielesarto@yahoo.com.br': None,
    'beatriz.grinsztejn@gmail.com': None,
    'vivianvidal01@gmail.com': None,
    'jucazita@yahoo.com.br': None,
    'limafilipe13@hotmail.com': None,
    'souzaxp4i@gmail.com': None,
    'adrianammas@gmail.com': None,
    'welisoncatarino13@hotmail.com': None,
    'secco.mayara@gmail.com': None,
    'm.mlbmsantos@gmail.com': None,
    'marcosdavi2006@yahoo.com.br': None,
    'raolisw@gmail.com': None,
    'costalg1@gmail.com': None,
    'laura_orlandi@hotmail.com': None,
    'mclaramdp@gmail.com': None,
    'markus_braga@hotmail.com': None,
    'daniela.torchi@gmail.com': None,
}

for email in pg_emails:
    data = asaas.get('data', {}).get(email)
    if data:
        pg_emails[email] = data.get('aluno_id_extref')

print("=== Querying Academy API /api/alunos/{id}/log for PG students ===\n")

for email, aluno_id in pg_emails.items():
    if not aluno_id:
        print(f"  [{email}] No aluno_id - skipping")
        continue
    
    result = academy_get(f"alunos/{aluno_id}/log")
    if 'error' not in result and result.get('success') and isinstance(result.get('data'), list):
        logs = result['data']
        
        # Extract unique courses from logs
        courses = set()
        turmas = set()
        for log in logs:
            curso = log.get('Curso', '')
            turma = log.get('Turma', '')
            modulo = log.get('Modulo', '')
            if curso and curso not in ['', 'None', 'nan']:
                courses.add(curso)
            if turma and turma not in ['', 'None', 'nan']:
                turmas.add(turma)
        
        print(f"  [{email}] aluno_id={aluno_id}")
        print(f"    Logs: {len(logs)}")
        print(f"    Cursos: {courses if courses else 'NONE'}")
        print(f"    Turmas: {turmas if turmas else 'NONE'}")
        
        if not courses and not turmas and logs:
            # Show sample log to understand structure
            print(f"    Sample log keys: {list(logs[0].keys())}")
            print(f"    Sample log: {json.dumps(logs[0], ensure_ascii=False)[:300]}")
    elif 'error' in result:
        print(f"  [{email}] aluno_id={aluno_id} - Error: {result['error'][:80]}")
    else:
        print(f"  [{email}] aluno_id={aluno_id} - No logs found")
    print()

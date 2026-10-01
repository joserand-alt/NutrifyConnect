"""
Try different Academy API endpoints to find student enrollments.
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

# 1. List all courses
print("=== ALL COURSES ===")
result = academy_get("cursos")
all_courses = []
if result.get('data'):
    all_courses = result['data']
    for c in all_courses:
        print(f"  ID={c['id']}: {c['nome']} ({c.get('tipo','')})")

# 2. For each course, try /api/cursos/{id}/matriculas or /api/cursos/{id}/alunos
print("\n=== Try enrollments per course ===")
aluno_id_test = '100214'  # danielesarto
email_test = 'danielesarto@yahoo.com.br'

for curso in all_courses[:15]:
    cid = curso['id']
    
    # Try /api/cursos/{id}/alunos
    r = academy_get(f"cursos/{cid}/alunos")
    if 'error' not in r and r.get('data'):
        alunos = r['data'] if isinstance(r['data'], list) else []
        # Check if our test student is in this course
        for a in alunos:
            a_email = (a.get('email', '') or '').lower().strip()
            a_id = str(a.get('id', ''))
            if a_email == email_test or a_id == aluno_id_test:
                print(f"  ** FOUND {email_test} in course: {curso['nome']} (ID={cid}) **")
        if len(alunos) > 0:
            print(f"  Course {cid} ({curso['nome']}): {len(alunos)} alunos")

# 3. Try /api/turmas endpoint  
print("\n=== Try /api/turmas ===")
r = academy_get("turmas")
if 'error' not in r:
    print(f"  Result keys: {list(r.keys()) if isinstance(r, dict) else 'list'}")
    if r.get('data'):
        for t in (r['data'] if isinstance(r['data'], list) else [])[:10]:
            print(f"  Turma: {json.dumps(t, ensure_ascii=False)[:200]}")

# 4. Try /api/alunos/{id}/cursos
print("\n=== Try /api/alunos/{id}/cursos ===")
r = academy_get(f"alunos/{aluno_id_test}/cursos")
if 'error' not in r:
    print(f"  Result: {json.dumps(r, ensure_ascii=False)[:500]}")
else:
    print(f"  Error: {r['error']}")

# 5. Try /api/alunos/{id}/matriculas
print("\n=== Try /api/alunos/{id}/matriculas ===")
r = academy_get(f"alunos/{aluno_id_test}/matriculas")
if 'error' not in r:
    print(f"  Result: {json.dumps(r, ensure_ascii=False)[:500]}")
else:
    print(f"  Error: {r['error']}")

# 6. Try /api/alunos/{id}/inscricoes
print("\n=== Try /api/alunos/{id}/inscricoes ===")
r = academy_get(f"alunos/{aluno_id_test}/inscricoes")
if 'error' not in r:
    print(f"  Result: {json.dumps(r, ensure_ascii=False)[:500]}")
else:
    print(f"  Error: {r['error']}")

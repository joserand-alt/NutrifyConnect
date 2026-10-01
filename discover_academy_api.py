import urllib.request, json

ACADEMY_TOKEN = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'

# 1. List all courses
url = 'https://academy.infectocast.com.br/api/cursos'
req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + ACADEMY_TOKEN, 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    d = json.loads(resp.read().decode('utf-8'))

cursos = d.get('data', [])
print(f"Total cursos: {len(cursos)}\n")
for c in cursos:
    print(f"  ID: {c['id']} | {c['nome']} | Tipo: {c.get('tipo', 'N/A')}")

# 2. Try to get students enrolled in each course
print("\n\n=== Tentando endpoints de alunos por curso ===")
test_curso_id = cursos[0]['id'] if cursos else 117

endpoints_to_try = [
    f'https://academy.infectocast.com.br/api/cursos/{test_curso_id}/alunos',
    f'https://academy.infectocast.com.br/api/cursos/{test_curso_id}/inscricoes',
    f'https://academy.infectocast.com.br/api/cursos/{test_curso_id}/turmas',
]

for url in endpoints_to_try:
    try:
        req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + ACADEMY_TOKEN, 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read().decode('utf-8'))
            print(f"\nOK {url}")
            print(json.dumps(d, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"FAIL {url}: {e}")

# 3. Try /api/alunos endpoint to list all students with courses
try:
    url = 'https://academy.infectocast.com.br/api/alunos'
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + ACADEMY_TOKEN, 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        d = json.loads(resp.read().decode('utf-8'))
        print(f"\nOK /api/alunos")
        if isinstance(d, dict) and 'data' in d:
            items = d['data']
            if isinstance(items, list):
                print(f"  Total: {len(items)}")
                if items:
                    print(f"  First: {json.dumps(items[0], ensure_ascii=False)[:500]}")
                    # Check if any has curso field
                    sample = items[0]
                    print(f"  Keys: {list(sample.keys())}")
            elif isinstance(items, dict):
                print(f"  Keys: {list(items.keys())[:10]}")
except Exception as e:
    print(f"FAIL /api/alunos: {e}")

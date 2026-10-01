import urllib.request
import json

token = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'

# First get course IDs
req = urllib.request.Request('https://academy.infectocast.com.br/api/cursos', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as resp:
    cursos = json.loads(resp.read().decode('utf-8')).get('data', [])

print(f"Loaded {len(cursos)} courses. First 5:")
for c in cursos[:5]:
    print(f"  ID: {c.get('id')} - {c.get('nome')}")

# Try potential endpoints on the first course ID
c_id = cursos[0]['id']
sub_endpoints = [
    f'https://academy.infectocast.com.br/api/cursos/{c_id}',
    f'https://academy.infectocast.com.br/api/cursos/{c_id}/alunos',
    f'https://academy.infectocast.com.br/api/cursos/{c_id}/matriculas',
    f'https://academy.infectocast.com.br/api/cursos/{c_id}/turmas',
    f'https://academy.infectocast.com.br/api/cursos/{c_id}/inscricoes',
    f'https://academy.infectocast.com.br/api/cursos/{c_id}/students',
    f'https://academy.infectocast.com.br/api/cursos/{c_id}/usuarios',
    f'https://academy.infectocast.com.br/api/matriculas',
    f'https://academy.infectocast.com.br/api/aluno',
    f'https://academy.infectocast.com.br/api/alunos-cursos',
    f'https://academy.infectocast.com.br/api/relatorio/alunos',
    f'https://academy.infectocast.com.br/api/exportar/alunos',
    f'https://academy.infectocast.com.br/api/aluno/100035', # sample student ID
    f'https://academy.infectocast.com.br/api/alunos/100035'
]

for ep in sub_endpoints:
    r = urllib.request.Request(ep, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(r, timeout=8) as res:
            d = json.loads(res.read().decode('utf-8'))
            print(f"[200 OK] {ep}")
            if isinstance(d, dict):
                print(f"   keys: {list(d.keys())}")
                if 'data' in d:
                    dt = d['data']
                    print(f"   data type: {type(dt)}, len: {len(dt) if hasattr(dt, '__len__') else 'N/A'}")
                    if isinstance(dt, list) and dt:
                        print(f"   sample item: {dt[0]}")
                    elif isinstance(dt, dict):
                        print(f"   sample dict keys: {list(dt.keys())}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] {ep}")
    except Exception as e:
        print(f"[ERR] {ep}: {e}")

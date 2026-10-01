import urllib.request
import json
import ssl

TOKEN = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'
BASE = 'https://academy.infectocast.com.br/api'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

def test_endpoint(endpoint):
    url = f"{BASE}{endpoint}" if not endpoint.startswith('http') else endpoint
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            data = resp.read().decode('utf-8')
            try:
                js = json.loads(data)
                return True, resp.status, js
            except Exception:
                return True, resp.status, data[:300]
    except urllib.error.HTTPError as e:
        return False, e.code, f"HTTP {e.code}"
    except Exception as e:
        return False, 0, str(e)

print("=== 1. LISTANDO CURSOS DISPONÍVEIS ===")
ok, status, res = test_endpoint('/cursos')
cursos = []
if ok and isinstance(res, dict):
    cursos = res.get('data', [])
    print(f"Total de cursos: {len(cursos)}")
    for c in cursos:
        print(f"  ID: {c.get('id')} | Nome: {c.get('nome')} | Tipo: {c.get('tipo')}")

test_id = cursos[0]['id'] if cursos else 117
print(f"\nUsando Curso ID: {test_id} ({cursos[0].get('nome') if cursos else 'N/A'}) para testes.\n")

endpoints_to_test = [
    # Swagger / Documentação
    'https://academy.infectocast.com.br/swagger/v1/swagger.json',
    'https://academy.infectocast.com.br/api/swagger.json',
    'https://academy.infectocast.com.br/api/help',
    
    # Detalhes do curso
    f'/cursos/{test_id}',
    f'/cursos/{test_id}/detalhes',
    f'/cursos/{test_id}/grade',
    f'/cursos/{test_id}/estrutura',
    f'/cursos/{test_id}/conteudo',
    
    # Módulos por curso
    f'/cursos/{test_id}/modulos',
    f'/cursos/{test_id}/modulo',
    f'/cursos/{test_id}/secoes',
    f'/cursos/{test_id}/disciplinas',
    
    # Aulas por curso
    f'/cursos/{test_id}/aulas',
    f'/cursos/{test_id}/licoes',
    f'/cursos/{test_id}/itens',
    
    # Endpoints diretos de módulos
    '/modulos',
    f'/modulos?curso_id={test_id}',
    f'/modulos?id_curso={test_id}',
    f'/modulos?cursoId={test_id}',
    
    # Endpoints diretos de aulas
    '/aulas',
    f'/aulas?curso_id={test_id}',
    f'/aulas?id_curso={test_id}',
    f'/aulas?cursoId={test_id}',
    '/licoes',
    '/conteudos',
]

print("=== 2. TESTANDO ROTAS DE MÓDULOS E AULAS ===")
for ep in endpoints_to_test:
    ok, st, out = test_endpoint(ep)
    status_icon = "[OK]" if ok else "[FAIL]"
    print(f"{status_icon} [{st}] {ep}")
    if ok:
        if isinstance(out, dict):
            keys = list(out.keys())
            sample = ""
            if 'data' in out:
                data_val = out['data']
                if isinstance(data_val, list):
                    sample = f" (items: {len(data_val)}, sample keys: {list(data_val[0].keys()) if data_val else 'empty'})"
                elif isinstance(data_val, dict):
                    sample = f" (dict keys: {list(data_val.keys())[:5]})"
            print(f"     Resposta: keys={keys}{sample}")
        else:
            print(f"     Resposta (texto): {str(out)[:150]}")

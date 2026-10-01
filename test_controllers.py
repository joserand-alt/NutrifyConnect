import urllib.request
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

controllers = [
    'curso', 'turma', 'modulo', 'aula', 'aluno', 'inscricao', 'matricula',
    'ead', 'lms', 'conteudo', 'item', 'material', 'video', 'grade',
    'disciplina', 'trilha', 'secao', 'unidade', 'moduloaula', 'cursoaula',
    'cursomodulo', 'turmamodulo', 'turmaaula', 'catalog', 'catalogo'
]

print("=== TESTANDO NOMES DE CONTROLLERS ===")
for c in controllers:
    url = f"{BASE}/{c}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = resp.read().decode('utf-8')
            print(f"[FOUND {resp.status}] /{c} -> {data[:80]}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"[{e.code}] /{c}")
    except Exception:
        pass
print("Fim.")

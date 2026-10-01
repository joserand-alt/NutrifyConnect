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

controllers = ['cursos', 'turmas', 'modulos', 'aulas', 'alunos', 'matriculas', 'conteudos', 'grades']
actions = [
    'modulos', 'modulo',
    'aulas', 'aula',
    'grade', 'grades',
    'conteudo', 'conteudos',
    'disciplinas', 'disciplina',
    'turmas', 'turma',
    'alunos', 'aluno',
    'inscricoes', 'inscricao',
    'itens', 'item',
    'detalhes', 'detalhe',
    'info',
    'listar',
    'all'
]

# Course 106 (CCIH), Turma 1016, Modulo 1032, Aula 100210, Aluno 100028
id_map = {
    'cursos': [106, 117, 107],
    'turmas': [1016, 1008, 1014],
    'modulos': [1032, 1052],
    'aulas': [100210, 100203],
    'alunos': [100028, 100027]
}

print("=== INICIANDO TESTE SISTEMÁTICO DE ROTAS ACADEMY ===")
found = []

for c in controllers:
    # 1. Test controller root
    url = f"{BASE}/{c}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            data = resp.read().decode('utf-8')
            print(f"[FOUND 200] GET /{c} -> {data[:100]}")
            found.append(f"GET /{c}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"[{e.code}] GET /{c}")
            found.append(f"GET /{c} ({e.code})")
    except Exception:
        pass

    # 2. Test actions with IDs
    sample_ids = id_map.get(c, [106])
    for test_id in sample_ids[:1]:
        for act in actions:
            url = f"{BASE}/{c}/{test_id}/{act}"
            req = urllib.request.Request(url, headers=HEADERS)
            try:
                with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
                    data = resp.read().decode('utf-8')
                    print(f"[FOUND 200] GET /{c}/{test_id}/{act} -> {data[:120]}")
                    found.append(f"GET /{c}/{test_id}/{act}")
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    print(f"[{e.code}] GET /{c}/{test_id}/{act}")
                    found.append(f"GET /{c}/{test_id}/{act} ({e.code})")
            except Exception:
                pass

print(f"\n=== RESUMO: {len(found)} ROTAS IDENTIFICADAS ===")
for f in found:
    print(" ", f)

import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    'dashboard.aspx',
    'curso.aspx',
    'cursos.aspx',
    'turma.aspx',
    'turmas.aspx',
    'aula.aspx',
    'aulas.aspx',
    'modulo.aspx',
    'modulos.aspx',
    'conteudo.aspx',
    'grade.aspx',
    'disciplinas.aspx',
    'aluno.aspx',
    'login.aspx',
    'default.aspx',
    'index.aspx'
]

print("=== TESTANDO PÁGINAS ASPX NO ACADEMY ===")
for p in candidates:
    url = f"https://academy.infectocast.com.br/{p}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            print(f"[OK {resp.status}] /{p}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"[STATUS {e.code}] /{p}")
    except Exception as e:
        pass

import json
import urllib.request
import os

token = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'

test_emails = [
    'danielesarto@yahoo.com.br',
    'beatriz.grinsztejn@gmail.com',
    'adrianammas@gmail.com',
    'daniela.torchi@gmail.com',
    'de_alexandre@hotmail.com',
    'fabrizio.motta76@gmail.com'
]

# 1. Check vindi cache
with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi = json.load(f)

# 2. Check asaas cache
with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

# 3. Check cativa cache
if os.path.exists('cativa_cache.json'):
    with open('cativa_cache.json', 'r', encoding='utf-8') as f:
        cativa = json.load(f)
else:
    cativa = {}

# 4. Check rd cache
if os.path.exists('rd_students_cache.json'):
    with open('rd_students_cache.json', 'r', encoding='utf-8') as f:
        rd = json.load(f)
else:
    rd = {}

print("--- INVESTIGAÇÃO DETALHADA POR ALUNO ---")

for em in test_emails:
    print(f"\n==========================================")
    print(f"ALUNO: {em}")
    print(f"==========================================")
    
    # Check Vindi
    v_match = vindi.get('data', {}).get(em)
    if not v_match:
        # search in subscriptions
        for s in vindi.get('subscriptions', []):
            if s.get('customer_email') == em:
                v_match = s
                break
    if v_match:
        print(f"[VINDI] Encontrado! Plano: {v_match.get('plano')} | Status: {v_match.get('status_assinatura') or v_match.get('status_financeiro')}")
    else:
        print(f"[VINDI] Não encontrado diretamente por email.")

    # Check Asaas
    a_match = asaas.get('data', {}).get(em)
    if a_match:
        print(f"[ASAAS] Encontrado! Plano/Desc: {a_match.get('plano') or a_match.get('description')} | Curso: {a_match.get('curso')}")
    else:
        print(f"[ASAAS] Não encontrado.")

    # Check RD
    rd_match = rd.get(em)
    if rd_match:
        print(f"[RD STATION] Encontrado! Tags: {rd_match.get('tags')} | Curso: {rd_match.get('curso')}")
    else:
        print(f"[RD STATION] Não encontrado.")

    # Check Academy API directly by searching aluno ID or querying endpoint
    try:
        url_search = f"https://academy.infectocast.com.br/api/alunos?busca={em}"
        req = urllib.request.Request(url_search, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print(f"[ACADEMY API /api/alunos?busca=...] Resposta:", res)
    except Exception as e:
        print(f"[ACADEMY API] Erro ao buscar: {e}")

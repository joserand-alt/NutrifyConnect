import urllib.request
import json

token_academy = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'
token_cativa = '5348006|E3g11Y75r447H66z5zN5k21Q0N1R923r3y8c3u0W'

print("--- BUSCANDO DANIELE SARTO NA ACADEMY ---")
# Let's list all students in academy to find Daniele Sarto's ID
try:
    url = "https://academy.infectocast.com.br/api/alunos"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token_academy}', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Total alunos returned by /api/alunos:", len(res.get('data', [])))
        for a in res.get('data', []):
            if 'daniele' in str(a).lower() or 'sarto' in str(a).lower() or 'danielesarto' in str(a).lower():
                print("FOUND IN ACADEMY:", a)
                # Now fetch logs for this aluno
                id_aluno = a.get('id') or a.get('id_aluno')
                if id_aluno:
                    log_url = f"https://academy.infectocast.com.br/api/alunos/{id_aluno}/log"
                    req_log = urllib.request.Request(log_url, headers={'Authorization': f'Bearer {token_academy}', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_log, timeout=15) as resp_log:
                        res_log = json.loads(resp_log.read().decode('utf-8'))
                        print(f"Logs count for ID {id_aluno}:", len(res_log.get('data', [])))
                        print("Sample logs:", res_log.get('data', [])[:5])
except Exception as e:
    print("Error querying Academy:", e)

print("\n--- BUSCANDO DANIELE SARTO NA CATIVA ---")
try:
    url = "https://api.cativadigital.com.br/v1/users?search=danielesarto"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token_cativa}', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Cativa search result:", res)
except Exception as e:
    print("Error querying Cativa search:", e)

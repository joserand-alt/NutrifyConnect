import urllib.request
import json

token = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'
endpoints = [
    'https://academy.infectocast.com.br/api/alunos',
    'https://academy.infectocast.com.br/api/students',
    'https://academy.infectocast.com.br/api/matriculas',
    'https://academy.infectocast.com.br/api/inscricoes',
    'https://academy.infectocast.com.br/api/users',
    'https://academy.infectocast.com.br/api/cursos',
    'https://academy.infectocast.com.br/api/turmas',
    'https://academy.infectocast.com.br/api/logs'
]

for ep in endpoints:
    req = urllib.request.Request(ep, headers={
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[SUCCESS] {ep} -> Status: {resp.status}")
            if isinstance(data, dict):
                print(f"   Keys: {list(data.keys())}")
                if 'data' in data:
                    val = data['data']
                    if isinstance(val, list):
                        print(f"   data is list with {len(val)} items")
                        if val and isinstance(val[0], dict):
                            print(f"   First item keys: {list(val[0].keys())}")
                            print(f"   First item sample: {val[0]}")
                    elif isinstance(val, dict):
                        print(f"   data is dict with keys: {list(val.keys())}")
            elif isinstance(data, list):
                print(f"   Direct list with {len(data)} items")
                if data and isinstance(data[0], dict):
                    print(f"   First item keys: {list(data[0].keys())}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {ep}")
    except Exception as e:
        print(f"[ERROR] {ep}: {e}")

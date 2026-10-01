import json, urllib.request

# 1. Get Welison's Academy ID from asaas cache
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)
data = cache.get('data', {})
for k, v in data.items():
    email = (v.get('customer_email') or '').lower()
    if 'welisoncatarino' in email:
        print("Welison found in cache:")
        print(f"  Key: {k}")
        print(f"  aluno_id_extref: {v.get('aluno_id_extref')}")
        welison_id = v.get('aluno_id_extref')
        break

# 2. Check if there's an inscricoes/enrollments endpoint
ACADEMY_TOKEN = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'

# Try /api/inscricoes endpoint
endpoints = [
    f'https://academy.infectocast.com.br/api/alunos/{welison_id}/inscricoes',
    f'https://academy.infectocast.com.br/api/alunos/{welison_id}/turmas',
    f'https://academy.infectocast.com.br/api/alunos/{welison_id}/cursos',
    f'https://academy.infectocast.com.br/api/inscricoes?aluno_id={welison_id}',
]

for url in endpoints:
    try:
        req = urllib.request.Request(url, headers={
            'Authorization': f'Bearer {ACADEMY_TOKEN}',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read().decode('utf-8'))
            print(f"\nOK {url}:")
            print(json.dumps(d, indent=2, ensure_ascii=False)[:1000])
    except Exception as e:
        print(f"\nFAIL {url}: {e}")

# 3. Also check the Inscrições spreadsheets for this email
print("\n\n=== CHECKING STUDENT_COURSE_MAP ===")
# Let's look at all the inscription spreadsheets
import os
for fn in os.listdir(r'C:\Users\DELL\Desktop\Acompanhamento de acessos'):
    if fn.startswith('Inscrições') and fn.endswith('.xlsx'):
        print(f"\nFile: {fn}")
        try:
            import openpyxl
            wb = openpyxl.load_workbook(os.path.join(r'C:\Users\DELL\Desktop\Acompanhamento de acessos', fn), data_only=True)
            for ws in wb.worksheets:
                for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
                    row_str = ' '.join(str(c or '') for c in row).lower()
                    if 'welison' in row_str or 'catarino' in row_str:
                        print(f"  FOUND: {row}")
        except Exception as e:
            print(f"  Error: {e}")

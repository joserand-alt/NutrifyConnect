import json

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

data = cache.get('data', {})

target_emails = [
    'welisoncatarino13@hotmail.com', 'rafael.farmaco@gmail.com',
    'limafilipe13@hotmail.com', 'souzaxp4i@gmail.com',
    'adrianammas@gmail.com', 'kyllianmunhoz@gmail.com',
    'gcotta29@gmail.com', 'costalg1@gmail.com',
    'laura_orlandi@hotmail.com', 'mclaramdp@gmail.com',
    'markus_braga@hotmail.com', 'daniela.torchi@gmail.com',
    'danielesarto@yahoo.com.br'
]

print("=== ASAAS CACHE - Alunos Plataforma Geral ===\n")
for aluno_id, info in data.items():
    email = (info.get('customer_email') or '').lower()
    if email in target_emails:
        nome = info.get('customer_name', '?')
        extref = info.get('aluno_id_extref', 'N/A')
        faturas = info.get('faturas', [])
        
        print(f"[{aluno_id}] {nome} ({email})")
        print(f"  aluno_id_extref: {extref}")
        
        if faturas:
            ft = faturas[0]
            print(f"  Fatura exemplo:")
            for k, v in ft.items():
                if isinstance(v, str) and len(v) < 100:
                    print(f"    {k}: {v}")
                elif isinstance(v, (int, float, bool)):
                    print(f"    {k}: {v}")
        print()

# Now check gerador.py for PLATAFORMA GERAL logic
print("\n=== GERADOR.PY - Lógica PLATAFORMA GERAL ===\n")
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'PLATAFORMA GERAL' in line or 'plataforma geral' in line.lower() or 'Plataforma Geral' in line:
        ctx_start = max(0, i-4)
        ctx_end = min(len(lines), i+4)
        for j in range(ctx_start, ctx_end):
            marker = ">>>" if j == i-1 else "   "
            print(f"{marker} {j+1}: {lines[j]}", end='')
        print("\n---")

import json, re

# Load the asaas cache to see if there's course data there
try:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
        asaas_cache = json.load(f)
    print(f"=== ASAAS CACHE: {len(asaas_cache)} entries ===\n")
    
    target_emails = [
        'welisoncatarino13@hotmail.com', 'rafael.farmaco@gmail.com',
        'limafilipe13@hotmail.com', 'souzaxp4i@gmail.com',
        'adrianammas@gmail.com', 'kyllianmunhoz@gmail.com',
        'gcotta29@gmail.com', 'costalg1@gmail.com',
        'laura_orlandi@hotmail.com', 'mclaramdp@gmail.com',
        'markus_braga@hotmail.com', 'daniela.torchi@gmail.com',
        'danielesarto@yahoo.com.br'
    ]
    
    for entry in asaas_cache:
        email = (entry.get('email') or '').lower().strip()
        if email in target_emails:
            print(f"Email: {email}")
            print(f"  Nome: {entry.get('nome', entry.get('name', '?'))}")
            print(f"  Curso: {entry.get('curso', 'N/A')}")
            print(f"  Plano: {entry.get('plano', 'N/A')}")
            print(f"  customer_id: {entry.get('customer_id', entry.get('id', 'N/A'))}")
            # Check for inscricao or subscription info
            for k, v in entry.items():
                if k not in ('email', 'nome', 'name', 'curso', 'plano', 'customer_id', 'id', 'faturas', 'payments'):
                    if isinstance(v, str) and len(v) < 200:
                        print(f"  {k}: {v}")
                    elif isinstance(v, (int, float, bool)):
                        print(f"  {k}: {v}")
            print()
except FileNotFoundError:
    print("asaas_cache.json not found")

# Also check what the gerador does with these students
print("\n=== CHECKING GERADOR LOGIC ===")
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py', 'r', encoding='utf-8') as f:
    gerador = f.read()

# Find where PLATAFORMA GERAL is set
lines = gerador.split('\n')
for i, line in enumerate(lines, 1):
    if 'PLATAFORMA GERAL' in line or 'plataforma geral' in line.lower():
        # Show context
        start = max(0, i-3)
        end = min(len(lines), i+3)
        for j in range(start, end):
            marker = ">>>" if j+1 == i else "   "
            print(f"{marker} {j+1}: {lines[j]}")
        print()

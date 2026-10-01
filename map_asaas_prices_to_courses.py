"""
Map Asaas contract values to courses.
Known course prices from the existing data:
"""
import json

# From our investigation, the KNOWN students and their contract values:
known_contracts = {
    'danielesarto@yahoo.com.br': 1968.30,    # 10x R$196.83
    'beatriz.grinsztejn@gmail.com': 2187.00,  # 1x R$2187
    'vivianvidal01@gmail.com': 8407.80,        # 18x R$467.10
    'jucazita@yahoo.com.br': 24984.00,         # 18x R$1388
    'limafilipe13@hotmail.com': 519.00,         # 1x R$519
    'souzaxp4i@gmail.com': 2187.00,            # 1x R$2187
    'adrianammas@gmail.com': 24984.00,         # 18x R$1388
    'welisoncatarino13@hotmail.com': 8407.80,  # 18x R$467.10
    'secco.mayara@gmail.com': 2187.00,         # 5x R$437.40
    'm.mlbmsantos@gmail.com': 9342.00,         # 12x R$778.50
    'marcosdavi2006@yahoo.com.br': 17488.80,   # 18x R$971.60
    'raolisw@gmail.com': 24984.00,             # 12x R$2082
    'costalg1@gmail.com': 2187.00,             # 10x R$218.70
    'laura_orlandi@hotmail.com': 2187.00,      # 12x R$182.25
    'mclaramdp@gmail.com': 819.00,             # 12x R$68.25
    'markus_braga@hotmail.com': 2187.00,       # 12x R$182.25
    'daniela.torchi@gmail.com': 2187.00,       # 5x R$437.40
}

# Now load the Vindi cache to understand KNOWN price->course mapping
with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi = json.load(f)

print("=== VINDI: Valores e planos conhecidos ===\n")
plan_prices = {}
for email, data in vindi.get('data', {}).items():
    plano = data.get('plano', '')
    if not plano: continue
    # Get faturas to compute total value
    fats = data.get('faturas', [])
    for f in fats:
        valor = f.get('valor', 0)
        if valor > 0:
            plan_prices.setdefault(plano, set()).add(valor)

for plan, prices in sorted(plan_prices.items()):
    print(f"  {plan}: parcelas = {sorted(prices)}")

# Check what Asaas total values map to
print("\n\n=== CONTRACT TOTAL VALUES -> POSSIBLE COURSES ===\n")
unique_values = sorted(set(known_contracts.values()))
for v in unique_values:
    emails = [e for e, val in known_contracts.items() if val == v]
    print(f"  R${v:,.2f}: {len(emails)} alunos")
    for e in emails:
        print(f"    - {e}")

# Key insight: We need to check what products Asaas has
# Let's check the Asaas products API

print("\n\n=== PRICE MAPPING ANALYSIS ===")
print("  R$2,187.00 = SOS Antibiotico (most common single course price)")
print("  R$819.00 = ? (module or smaller course)")
print("  R$1,968.30 = ? (close to R$2187 but discounted)")
print("  R$8,407.80 = ? (multi-course bundle)")
print("  R$24,984.00 = ? (full pos-graduation)")
print("  R$519.00 = ? (module)")
print("  R$9,342.00 = ? (multi-course)")
print("  R$17,488.80 = ? (multi-course)")

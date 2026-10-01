"""
Build a definitive price->course mapping from KNOWN Vindi data.
Then apply it to resolve the 17 PLATAFORMA GERAL students.
"""
import json, re

# Load Vindi cache - has known price->course mappings
with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi = json.load(f)

# Build plan name -> canonical course mapping
plan_to_course = {}
plan_total_values = {}

for email, data in vindi.get('data', {}).items():
    plano = data.get('plano', '')
    if not plano: continue
    
    # Calculate total contract value from faturas
    fats = data.get('faturas', [])
    if fats:
        parcela = fats[0].get('valor', 0)
        n_parcelas = len(fats)
        total = round(parcela * n_parcelas, 2)
        plan_total_values.setdefault(plano, set()).add(total)
    
    # Map plan name to canonical course
    p_upper = plano.upper()
    if 'INFECTOPEDI' in p_upper or 'PEDIAT' in p_upper:
        plan_to_course[plano] = 'POS-GRADUACAO EM INFECTOPEDIATRIA'
    elif 'ORTO' in p_upper or 'PARTES MOLES' in p_upper:
        plan_to_course[plano] = 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES'
    elif 'CCIH' in p_upper or 'HOSPITALAR' in p_upper or 'PREVENCAO' in p_upper:
        plan_to_course[plano] = 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'
    elif 'IMUNO' in p_upper or 'INUNO' in p_upper:
        plan_to_course[plano] = 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'
    elif 'SOS' in p_upper or 'ANTIBIO' in p_upper:
        plan_to_course[plano] = 'S.O.S ANTIBIOTICO'
    elif 'MULTI-R' in p_upper or 'MULTIR' in p_upper:
        plan_to_course[plano] = 'JORNADA MULTI-R'
    elif 'FUNGO' in p_upper or 'ANTIFUNG' in p_upper:
        plan_to_course[plano] = 'DO FUNGO AO ANTIFUNGICO'
    elif 'NUTRIFY' in p_upper:
        plan_to_course[plano] = 'NUTRIFY CONNECT'

# Now analyze Vindi known total values per COURSE
course_values = {}
for plano, course in plan_to_course.items():
    if plano in plan_total_values:
        for val in plan_total_values[plano]:
            course_values.setdefault(course, set()).add(val)

print("=== KNOWN COURSE VALUES (from Vindi) ===\n")
for course, values in sorted(course_values.items()):
    print(f"  {course}:")
    for v in sorted(values):
        print(f"    R${v:,.2f}")

# Now analyze the Asaas PG students values
print("\n\n=== ASAAS PG STUDENTS VALUES ===\n")
with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

pg_emails = [
    'vivianvidal01@gmail.com', 'beatriz.grinsztejn@gmail.com', 'jucazita@yahoo.com.br',
    'limafilipe13@hotmail.com', 'souzaxp4i@gmail.com', 'adrianammas@gmail.com',
    'danielesarto@yahoo.com.br', 'welisoncatarino13@hotmail.com', 'secco.mayara@gmail.com',
    'm.mlbmsantos@gmail.com', 'marcosdavi2006@yahoo.com.br', 'raolisw@gmail.com',
    'costalg1@gmail.com', 'laura_orlandi@hotmail.com', 'mclaramdp@gmail.com',
    'markus_braga@hotmail.com', 'daniela.torchi@gmail.com'
]

# Calculate total contract value from Asaas faturas
for email in pg_emails:
    data = asaas.get('data', {}).get(email)
    if not data: continue
    
    fats = data.get('faturas', [])
    if not fats: continue
    
    # Extract total from description
    desc = fats[0].get('description', '')
    total = 0
    m = re.search(r'R\$([0-9.,]+)\s*\((\d+)x\)', desc)
    if m:
        total_str = m.group(1).replace('.','').replace(',','.')
        total = float(total_str)
    
    parcela = fats[0].get('valor', 0)
    n_parcelas = len(fats)
    
    print(f"  [{email}]")
    print(f"    Total contrato (desc): R${total:,.2f}")
    print(f"    Parcela: R${parcela:,.2f} x {n_parcelas}")
    
    # Try to match with known course values
    matched = False
    for course, values in course_values.items():
        if total in values:
            print(f"    >>> MATCH: {course}")
            matched = True
            break
        # Try with some tolerance (within 5%)
        for v in values:
            if abs(total - v) / max(v, 1) < 0.05:
                print(f"    >>> APPROXIMATE MATCH (~{abs(total-v):.2f} diff): {course}")
                matched = True
                break
        if matched: break
    
    if not matched:
        # Try by parcela value
        for course, values in course_values.items():
            for v in values:
                expected_parcela = v / n_parcelas
                if abs(parcela - expected_parcela) < 1:
                    print(f"    >>> PARCELA MATCH: {course} (total R${v:,.2f} / {n_parcelas} = R${expected_parcela:,.2f})")
                    matched = True
                    break
            if matched: break
    
    if not matched:
        print(f"    >>> NO MATCH - need manual mapping")
    print()

# Definitive mapping by Asaas contract total values
print("\n\n=== PROPOSED PRICE->COURSE MAP FOR ASAAS ===\n")
# Analysis of known Nutrify pricing:
# R$2,187.00 = SOS Antibiotico (standard price)
# R$1,968.30 = SOS Antibiotico (10% discount)  
# R$819.00 = Module-only (e.g. SOS ATB MDR or single module)
# R$519.00 = Module mini (SOS ATB module or event)
# R$24,984.00 = Pos-Graduacao (18x R$1,388 = standard PG price)
# R$17,488.80 = Pos-Graduacao (18x R$971.60 = PG with discount)
# R$9,342.00 = Pos-Graduacao (12x R$778.50)
# R$8,407.80 = Pos-Graduacao (18x R$467.10)

# The SOS ATB price is R$2,187
# PG prices vary by discount/parcelas but R$24,984 is standard 18x
# R$971.60 is a known Vindi PG parcela value (Ortopedicas and InfectoPediatria)
# R$1,388 is standard PG parcela
# R$467.10 appears in Vindi as well

print("Key insight: Without product name in Asaas, we CANNOT reliably")
print("distinguish which specific Pos-Graduacao course a student is in")
print("when the price is a generic PG price (R$24,984, R$17,488, etc.)")
print("because multiple PG courses share the same pricing tiers.")
print()
print("HOWEVER, R$2,187 and R$819 are specific to SOS Antibiotico.")
print("For PG students, we need the Asaas 'externalReference' to")
print("cross-reference with Academy API /api/alunos/{id} to find courses.")

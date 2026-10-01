import json

pg_emails = [
    'vivianvidal01@gmail.com', 'beatriz.grinsztejn@gmail.com', 'jucazita@yahoo.com.br',
    'limafilipe13@hotmail.com', 'souzaxp4i@gmail.com', 'adrianammas@gmail.com',
    'danielesarto@yahoo.com.br', 'welisoncatarino13@hotmail.com', 'secco.mayara@gmail.com',
    'm.mlbmsantos@gmail.com', 'marcosdavi2006@yahoo.com.br', 'raolisw@gmail.com',
    'costalg1@gmail.com', 'laura_orlandi@hotmail.com', 'mclaramdp@gmail.com',
    'markus_braga@hotmail.com', 'daniela.torchi@gmail.com'
]

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

# Known prices -> courses mapping (from the business)
# R$2187 = SOS ATB (total 12x)
# R$1388 = ?
# R$519 = ?
# R$467.10 = ?
# R$196.83 = ?

print("=== ASAAS: valor total e descrições para resolver curso ===\n")
for email in pg_emails:
    data = asaas.get('data', {}).get(email)
    if not data:
        print(f"  [{email}] NÃO encontrado no Asaas\n")
        continue
    
    # Get all faturas descriptions
    fats = data.get('faturas', [])
    descs = set()
    valores = set()
    for f in fats:
        d = f.get('description', f.get('descricao', ''))
        if d: descs.add(d)
        v = f.get('valor', 0)
        if v: valores.add(v)
    
    total = data.get('total_pago', 0)
    
    print(f"  [{email}]")
    print(f"    Nome: {data.get('customer_name')}")
    print(f"    Total pago: R${total}")
    print(f"    Valores parcela: {valores}")
    print(f"    Desc: {list(descs)[:3]}")
    
    # Try to extract payment number
    for d in descs:
        if 'Pagamento #' in d:
            # e.g. "Parcela 1 de 12. Pagamento #100084 - R$2.187,00 (12x)"
            idx = d.find('R$')
            if idx >= 0:
                valor_str = d[idx+2:].split(' ')[0].replace('.','').replace(',','.')
                try:
                    v_total = float(valor_str)
                    print(f"    Valor TOTAL contrato: R${v_total}")
                except: pass
            break
    print()

# Now let's check asaas_service to understand what descriptions Asaas returns
print("\n=== Valores conhecidos dos cursos Nutrify ===")
print("  SOS ATB (SOS Antibiótico) = R$2.187,00")
print("  PED (Pediatria) = R$2.187,00")  
print("  ATB Módulo = R$819,00")
print("  Preciso identificar pela API do Asaas qual campo tem o NOME DO PRODUTO")

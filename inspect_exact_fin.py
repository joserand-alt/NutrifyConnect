with open('vindi_service.py', 'r', encoding='utf-8') as f:
    v_code = f.read()

pos_fin = v_code.find('financeiro_global = {')
print("=== vindi_service.py financeiro_global ===")
print(v_code[pos_fin:pos_fin+1200])

with open('asaas_service.py', 'r', encoding='utf-8') as f:
    a_code = f.read()

pos_afin = a_code.find('financeiro_global = {')
print("\n=== asaas_service.py financeiro_global ===")
print(a_code[pos_afin:pos_afin+1200])

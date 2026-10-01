with open('vindi_service.py', 'r', encoding='utf-8') as f:
    vindi_code = f.read()

print("=== vindi_service.py length:", len(vindi_code))
pos_proj = vindi_code.find('projecao')
print(vindi_code[pos_proj-100:pos_proj+2500])

with open('asaas_service.py', 'r', encoding='utf-8') as f:
    asaas_code = f.read()

print("\n=== asaas_service.py length:", len(asaas_code))
pos_aproj = asaas_code.find('projecao')
print(asaas_code[pos_aproj-100:pos_aproj+2500])

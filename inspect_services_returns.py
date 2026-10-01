with open('vindi_service.py', 'r', encoding='utf-8') as f:
    vindi_code = f.read()

pos_ret = vindi_code.rfind('return')
print("=== vindi_service.py return block ===")
print(vindi_code[pos_ret-500:pos_ret+1000])

with open('asaas_service.py', 'r', encoding='utf-8') as f:
    asaas_code = f.read()

pos_aret = asaas_code.rfind('return')
print("\n=== asaas_service.py return block ===")
print(asaas_code[pos_aret-500:pos_aret+1000])

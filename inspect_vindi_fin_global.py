with open('vindi_service.py', 'r', encoding='utf-8') as f:
    vindi_code = f.read()

pos = vindi_code.find('financeiro_global = {')
print("=== vindi_service.py financeiro_global definition ===")
print(vindi_code[pos-1000:pos+1500])

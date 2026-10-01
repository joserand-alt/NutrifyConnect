with open('cativa_api.py', 'r', encoding='utf-8') as f:
    cativa_code = f.read()
print("--- cativa_api.py ---")
print(cativa_code[:1500])

with open('gerador.py', 'r', encoding='utf-8') as f:
    gen_code = f.read()

pos_acad = gen_code.find('def fetch_logs_from_api')
print("\n--- gerador.py Academy logs fetch ---")
print(gen_code[pos_acad:pos_acad+1500])

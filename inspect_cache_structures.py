import json

# Check vindi_cache.json
with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi_cache = json.load(f)

print("vindi_cache keys:", list(vindi_cache.keys()))
fin = vindi_cache.get('financeiro', {})
print("vindi_cache.financeiro keys:", list(fin.keys()))
print("vindi_cache subscriptions:", len(fin.get('subscriptions', [])))
print("vindi_cache projecao_mensal_map:", fin.get('projecao_mensal_map'))

# Check asaas_cache.json
with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas_cache = json.load(f)

print("\nasaas_cache keys:", list(asaas_cache.keys()))
afin = asaas_cache.get('financeiro', {})
print("asaas_cache.financeiro keys:", list(afin.keys()))
print("asaas_cache projecao_mensal_map:", afin.get('projecao_mensal_map'))

# Check gerador.py where vindi and asaas are serialized into DATA
with open('gerador.py', 'r', encoding='utf-8') as f:
    gen_code = f.read()

pos_v_fin = gen_code.find('financeiro_data')
print("\n--- gerador.py financeiro_data snippet ---")
print(gen_code[pos_v_fin-100:pos_v_fin+2000].encode('ascii', 'replace').decode('ascii'))

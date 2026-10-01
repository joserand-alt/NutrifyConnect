import json

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi_cache = json.load(f)

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas_cache = json.load(f)

print("=== VINDI PROJECAO MENSAL ===")
print(json.dumps(vindi_cache.get('financeiro', {}).get('projecao_mensal', []), indent=2))

print("\n=== ASAAS PROJECAO MENSAL ===")
print(json.dumps(asaas_cache.get('financeiro', {}).get('projecao_mensal', []), indent=2))

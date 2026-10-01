import os

for path in [
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py',
    r'C:\Users\DELL\Desktop\Acompanhamento de acessos\asaas_service.py'
]:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Add projecao_map = {} near historico_map = {}
        old_init = "historico_map = {}\n\n    faturas_tabela = []"
        new_init = "historico_map = {}\n    projecao_map = {}\n\n    faturas_tabela = []"
        
        if old_init in code:
            code = code.replace(old_init, new_init)
        else:
            code = code.replace("historico_map = {}", "historico_map = {}\n    projecao_map = {}")
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"Fixed projecao_map in {path}")

cache_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json'
if os.path.exists(cache_file):
    os.remove(cache_file)
    print("Cleared asaas_cache.json")

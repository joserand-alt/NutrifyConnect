import os
import re

vpath = r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_service.py'

with open(vpath, 'r', encoding='utf-8') as f:
    code = f.read()

# Look for sub_status == 'active' block in vindi_service.py
old_active_block = """        elif sub_status == 'active':
            st_fin = 'adimplente'
            st_lbl = 'Adimplente'
            st_color = 'var(--emerald-d)'
            st_bg = 'var(--emerald-bg)'"""

new_active_block = """        elif sub_status == 'active':
            st_fin = 'adimplente'
            st_lbl = 'Adimplente'
            st_color = 'var(--emerald-d)'
            st_bg = 'var(--emerald-bg)'
            mrr_ativo_total += price
            if next_b_dt:
                proj_ym = next_b_dt.strftime('%Y-%m')
                projecao_mensal_map[proj_ym] = projecao_mensal_map.get(proj_ym, 0.0) + price
            else:
                projecao_mensal_map[current_ym] = projecao_mensal_map.get(current_ym, 0.0) + price"""

if old_active_block in code:
    code = code.replace(old_active_block, new_active_block)
    print("Updated active sub MRR calculation in vindi_service.py!")
else:
    print("Could not find old_active_block, using regex...")
    pattern = r'(elif sub_status == [\'"]active[\'"]:.*?st_bg = [\'"]var\(--emerald-bg\)[\'"])'
    match = re.search(pattern, code, re.DOTALL)
    if match:
        code = code[:match.start()] + new_active_block + code[match.end():]
        print("Updated active sub MRR via regex in vindi_service.py!")

with open(vpath, 'w', encoding='utf-8') as f:
    f.write(code)

# Clear vindi cache
cache_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json'
if os.path.exists(cache_path):
    os.remove(cache_path)
    print("Removed vindi_cache.json")

print("vindi_service.py fix complete.")

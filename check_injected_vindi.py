import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('window.CURRENT_DATA')
if idx != -1:
    end_idx = html.find('</script>', idx)
    data_str = html[idx:end_idx]
    
    # Check vindi in window.CURRENT_DATA
    v_idx = data_str.find('"vindi":')
    if v_idx != -1:
        print('Found "vindi": in CURRENT_DATA')
        # Let's inspect what keys are present
        k_data = '"data":' in data_str[v_idx:v_idx+1000]
        k_kpis = '"kpis":' in data_str[v_idx:v_idx+1000]
        k_subs = '"subscriptions":' in data_str[v_idx:v_idx+2000]
        print(f'has data: {k_data}, has kpis: {k_kpis}, has subscriptions: {k_subs}')

# Also check gerador.py to see what gerador.py injects into CURRENT_DATA['vindi']
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py', 'r', encoding='utf-8') as f:
    g_code = f.read()

for l in g_code.splitlines():
    if 'vindi_data' in l or 'get_vindi_data' in l:
        print('gerador line:', l.strip())

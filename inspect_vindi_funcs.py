with open('vindi_service.py', 'r', encoding='utf-8') as f:
    vindi_src = f.read()

import re
funcs = re.findall(r'def\s+([a-zA-Z0-9_]+)\s*\(', vindi_src)
print("Functions in vindi_service.py:", funcs)

pos_get = vindi_src.find('def get_vindi_data')
print("\n=== get_vindi_data ===")
print(vindi_src[pos_get:pos_get+3000])

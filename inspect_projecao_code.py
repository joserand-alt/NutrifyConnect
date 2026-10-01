import json
import re

with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

# Let's inspect G1 in template.html
g1_idx = tmpl.find('<!-- G1')
if g1_idx != -1:
    print("\n--- G1 HTML in template.html ---")
    print(tmpl[g1_idx:g1_idx+3500].encode('ascii', 'replace').decode('ascii'))

# Let's find where G1 variables are computed in drawExecView
exec_idx = tmpl.find('function drawExecView')
if exec_idx != -1:
    print("\n--- drawExecView calculation snippet ---")
    pos_mount = tmpl.find('mount.innerHTML = `', exec_idx)
    print(tmpl[exec_idx:pos_mount].encode('ascii', 'replace').decode('ascii')[-3500:])

import subprocess
import re

with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
with open('temp_test_syntax.js', 'w', encoding='utf-8') as f:
    f.write(scripts[0] if scripts else '')

res = subprocess.run(['node', '-c', 'temp_test_syntax.js'], capture_output=True)
print('Node return code:', res.returncode)
if res.returncode != 0:
    print('Error:', res.stderr.decode('utf-8', errors='ignore'))
else:
    print('JavaScript syntax is 100% PERFECT!')

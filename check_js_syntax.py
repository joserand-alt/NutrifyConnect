import re
import subprocess

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
print(f"Extracted {len(scripts)} script tags.")

with open('test_script.js', 'w', encoding='utf-8') as sf:
    sf.write('const window = {}; const document = { querySelector: () => null, querySelectorAll: () => [] };\n')
    for s in scripts:
        sf.write(s + '\n')

res = subprocess.run(['node', '-c', 'test_script.js'], capture_output=True, text=True)
if res.returncode == 0:
    print("SUCCESS: JavaScript syntax in template.html is 100% VALID!")
else:
    print("SYNTAX ERROR in JavaScript:")
    print(res.stderr)

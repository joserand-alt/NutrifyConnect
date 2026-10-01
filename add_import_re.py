import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

if 'import re' not in code:
    code = 'import re\n' + code
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Added import re to asaas_service.py!")
else:
    print("import re already present.")

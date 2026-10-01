import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

funcs = re.findall(r'def\s+([a-zA-Z0-9_]+)\(', text)
print("Functions in asaas_service.py:", funcs)

for f in funcs:
    pos = text.find(f'def {f}(')
    print(f"\n--- Function: {f} (pos {pos}) ---")
    print(text[pos:pos+1000])

import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'financeiro|vindi|asaas', text, re.IGNORECASE):
    idx = m.start()
    print(f"Match at {idx}: {text[max(0, idx-20):min(len(text), idx+100)]!r}")

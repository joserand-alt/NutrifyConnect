import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'drawFinanceiro', text):
    idx = m.start()
    print(f"Match at {idx}: {repr(text[max(0, idx-30):min(len(text), idx+100)])}")

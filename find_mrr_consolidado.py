import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('mrrConsolidado')
while pos != -1:
    print(f"Match at {pos}:\n{text[max(0, pos-100):min(len(text), pos+300)]}\n---")
    pos = text.find('mrrConsolidado', pos+1)

import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'GRUPO 7|Semáforo de Risco|exec-g7|Alerta', text, re.IGNORECASE)]
for idx in matches:
    print(f"Match at {idx}:\n{text[max(0, idx-50):min(len(text), idx+500)]}\n---")

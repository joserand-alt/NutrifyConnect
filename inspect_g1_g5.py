template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Lines 4400 to 4720 in template.html ---')
for i in range(4400, min(4720, len(lines))):
    line = lines[i].rstrip()
    if any(k in line.lower() for k in ['grupo', 'g1', 'g2', 'g3', 'g4', 'g5', 'exec-sec-title', 'exec-sec-num', 'exec-card-val', 'exec-card-label', 'exec-card-sub', 'aquisi', 'venda']):
        print(f"{i+1}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

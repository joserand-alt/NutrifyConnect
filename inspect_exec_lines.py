template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Lines 3954 to 4300 ---')
for i in range(3953, min(4300, len(lines))):
    line = lines[i].rstrip()
    if any(k in line.lower() for k in ['grupo', 'bloco', 'card', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'aquisi', 'venda', 'receita', 'engajamento', 'retenc', 'lados', 'grid', 'mount.innerhtml', 'sec-head', 'h3', 'h4', 'span']):
        print(f"{i+1}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

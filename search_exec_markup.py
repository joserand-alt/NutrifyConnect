template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Search for titles / sections in drawExecView (lines 4300-4999) ---')
for i in range(4300, min(5000, len(lines))):
    line = lines[i].rstrip()
    if any(k in line.lower() for k in ['aquisi', 'venda', 'receita', 'engajamento', 'retenc', 'saude', 'inadimpl', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'exec-group', 'exec-card', 'exec-header', 'bloco', 'grupo', 'card-header']):
        print(f"{i+1}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

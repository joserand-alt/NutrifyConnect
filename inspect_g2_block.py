template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_g2 = text.find('<!-- GRUPO 2: AQUISI')
if idx_g2 != -1:
    print('G2 HTML block in drawExecView:')
    print(text[idx_g2:idx_g2+2200].encode('ascii', 'replace').decode('ascii'))

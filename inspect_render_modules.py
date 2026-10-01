template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_mod = text.find('function renderModules')
if idx_mod != -1:
    print('--- renderModules in template.html ---')
    print(text[idx_mod:idx_mod+2500])

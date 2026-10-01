template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect selectTab
idx_st = text.find('function selectTab')
if idx_st != -1:
    print('--- selectTab function ---')
    print(text[idx_st:idx_st+800].encode('ascii', 'replace').decode('ascii'))

# Let's inspect where drawCursoView is in template.html
idx_cv = text.find('function drawCursoView')
if idx_cv != -1:
    print('\n--- drawCursoView position ---')
    print(text[idx_cv:idx_cv+1000].encode('ascii', 'replace').decode('ascii'))
else:
    print('\n--- drawCursoView NOT FOUND! ---')

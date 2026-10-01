template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Nav tabs
idx_tabs = text.find('<nav class="tabs"')
print('Tabs location:')
print(text[idx_tabs:idx_tabs+800].encode('ascii', 'replace').decode('ascii'))

# Panels
idx_exec = text.find('<section class="panel on" id="p-exec">')
print('\nPanel exec location:')
print(text[idx_exec:idx_exec+400].encode('ascii', 'replace').decode('ascii'))

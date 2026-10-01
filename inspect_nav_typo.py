template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_tabs = text.find('<nav class="tabs"')
print('--- Nav tabs in template.html ---')
print(text[idx_tabs:idx_tabs+1000].encode('ascii', 'replace').decode('ascii'))

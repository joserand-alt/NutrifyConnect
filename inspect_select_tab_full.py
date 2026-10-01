with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('function selectTab(')
print(html[idx:idx+2500])

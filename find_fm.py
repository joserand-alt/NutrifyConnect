template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('fM =')
while idx != -1:
    print(text[idx-50:idx+150].replace('\n', ' '))
    idx = text.find('fM =', idx + 10)

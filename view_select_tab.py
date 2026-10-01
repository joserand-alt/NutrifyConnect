template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function selectTab')
print(text[idx:idx+1200].encode('ascii', errors='replace').decode('ascii'))

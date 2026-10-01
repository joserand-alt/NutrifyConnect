template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_nav = text.find('<nav')
idx_panel0 = text.find('<!-- PANEL 0:')
print('nav at:', idx_nav, 'panel0 at:', idx_panel0)
print('--- NAV SNIPPET ---')
print(text[idx_nav:idx_panel0].encode('ascii', errors='replace').decode('ascii'))
print('--- PANEL 0 START ---')
print(text[idx_panel0:idx_panel0+300].encode('ascii', errors='replace').decode('ascii'))

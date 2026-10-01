with open('c:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

panels = ['exec', 'curso', 'home', 'prog', 'mod', 'ret', 'tl', 'funil', 'origem', 'fin']
for p in panels:
    print(f'p-{p} in index.html:', f'id="p-{p}"' in html)

# Let's inspect where selectTab is and how it switches
idx = html.find('function selectTab(')
if idx != -1:
    print('--- selectTab ---')
    print(html[idx:idx+1200])

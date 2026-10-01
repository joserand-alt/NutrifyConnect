template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function switchTab')
if idx != -1:
    print('switchTab found at', idx)
    print(text[idx:idx+1200].encode('ascii', errors='replace').decode('ascii'))
else:
    print('switchTab not found, looking for data-p click')
    idx_dp = text.find('data-p')
    print('data-p at', idx_dp)
    print(text[idx_dp:idx_dp+600].encode('ascii', errors='replace').decode('ascii'))

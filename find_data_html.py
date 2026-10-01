import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read(50000)

pos = text.find('const DATA =')
if pos == -1: pos = text.find('let DATA =')
if pos == -1: pos = text.find('var DATA =')
if pos == -1: pos = text.find('DATA =')
print("DATA pos in dashboard_gerado.html:", pos)
if pos != -1:
    print(text[pos:pos+200])

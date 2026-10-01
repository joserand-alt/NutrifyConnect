import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_renderall = text.find('function renderAll')
print("renderAll function:")
print(text[pos_renderall:pos_renderall+3000])

import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function _renderFinCursosTable(')
if idx != -1:
    print("_renderFinCursosTable snippet:")
    print(text[idx:idx+2500])

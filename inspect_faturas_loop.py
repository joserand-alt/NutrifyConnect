import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('// 2. Faturas Emitidas e Histórico')
pos_end = text.find('// 5. Totalizadores Finais', pos)

print(text[pos:pos_end])

import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('// ABA FINANCEIRO')
print("Position:", pos)
print(text[pos:pos+3000])

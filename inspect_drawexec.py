import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function drawExecView')
pos_end = text.find('function drawHome', pos)

print(f"drawExecView span: {pos} to {pos_end}")
print(text[pos:pos+3000])

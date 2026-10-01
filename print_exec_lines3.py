import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_exec = text.find('function drawExecView')
pos_exec_end = text.find('function drawHome', pos_exec)

lines = text[pos_exec:pos_exec_end].split('\n')
for idx, l in enumerate(lines[250:400], start=251):
    print(f"{idx}: {l[:100]}")

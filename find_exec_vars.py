import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('computeUnifiedFinancialDataset')
# Find occurrences in drawExecView
pos_exec = text.find('function drawExecView')
pos_exec_end = text.find('function drawHome', pos_exec)

print("drawExecView region:")
for line in text[pos_exec:pos_exec_end].split('\n')[:120]:
    if any(k in line for k in ['computeUnifiedFinancialDataset', 'finUnified', 'mrr', 'proj', 'atraso', 'adimplencia', 'leads', 'totalVigentes']):
        print(line)

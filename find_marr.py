import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function computeUnifiedFinancialDataset')
pos_end = text.find('function drawExecView', pos)

unified_code = text[pos:pos_end]

pos_marr = unified_code.find('mArr')
print("mArr snippet:")
print(unified_code[pos_marr-200:pos_marr+400])

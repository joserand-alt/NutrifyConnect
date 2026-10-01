import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function computeUnifiedFinancialDataset')
pos_end = text.find('function drawExecView', pos)

unified_code = text[pos:pos_end]

# Find how cm.projecao_mensal is built
pos_proj = unified_code.find('projecao_mensal')
print("Snippet around projecao_mensal in computeUnifiedFinancialDataset:")
print(unified_code[pos_proj-200:pos_proj+800])

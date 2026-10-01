import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function computeUnifiedFinancialDataset')
pos_end = text.find('function drawExecView', pos)

print(text[pos:pos+4000])

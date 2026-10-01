import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect computeUnifiedFinancialDataset in template.html
pos = text.find('function computeUnifiedFinancialDataset')
pos_end = text.find('function drawExecView', pos)
print("Current computeUnifiedFinancialDataset length:", pos_end - pos)

# Let's check how Asaas MRR is added in computeUnifiedFinancialDataset
# We ensure that:
# 1. Asaas MRR per course adds the active adimplente installments or the course's first month projection
# 2. The global MRR precisely matches vKpis.mrr_ativo (221.982,43) + aKpis.mrr_ativo (4.281,10) = 226.263,53

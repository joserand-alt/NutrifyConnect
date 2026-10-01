import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_unified = text.find('function computeUnifiedFinancialDataset')
pos_getfin = text.find('function _getFinData')
pos_renderfin = text.find('function _renderFinCursosTable')

print(f"computeUnifiedFinancialDataset pos: {pos_unified}")
print(f"_getFinData pos: {pos_getfin}")
print(f"_renderFinCursosTable pos: {pos_renderfin}")

print("\n--- _getFinData ---")
print(text[pos_getfin:pos_getfin+1500])

print("\n--- _renderFinCursosTable ---")
print(text[pos_renderfin:pos_renderfin+1500])

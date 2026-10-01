import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect buildHead, statusChips, renderRows
pos = text.find('function buildHead')
pos_end = text.find('function renderModules')
print("--- buildHead to renderModules ---")
print(text[pos:pos+3500])

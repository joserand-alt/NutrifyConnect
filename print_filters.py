import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_init = text.find('function initFilters')
pos_apply = text.find('function applyFilters')
print("initFilters / applyFilters span:")
print(text[pos_init:pos_apply+2000])

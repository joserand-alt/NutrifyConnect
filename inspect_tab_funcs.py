import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_sel = text.find('function selectTab')
pos_mod = text.find('function renderModules')
pos_ret = text.find('function renderRetention')
pos_tl = text.find('function drawTimeline')

print("--- selectTab ---")
print(text[pos_sel:pos_sel+1000])

print("\n--- renderModules ---")
print(text[pos_mod:pos_mod+1500])

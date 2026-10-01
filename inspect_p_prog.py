import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="p-prog"')
pos_end = text.find('</section>', pos)
print("--- p-prog HTML ---")
print(text[pos:pos_end+10])

import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_trigger = text.find('function triggerUpdate')
print(f"triggerUpdate pos: {pos_trigger}")
print(text[pos_trigger:pos_trigger+4000])

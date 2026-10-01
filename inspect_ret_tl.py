import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_ret = text.find('function renderRetention')
pos_tl = text.find('function drawTimeline')

print("--- renderRetention ---")
print(text[pos_ret:pos_ret+2000])

print("\n--- drawTimeline ---")
print(text[pos_tl:pos_tl+2000])

import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Inspect panels in HTML
for p in ['p-prog', 'p-mod', 'p-ret', 'p-tl']:
    pos = text.find(f'id="{p}"')
    print(f"--- HTML Panel: {p} (at {pos}) ---")
    if pos != -1:
        print(text[pos:pos+1000])

# Inspect JS functions
for func in ['renderRows', 'renderModules', 'renderRetention', 'drawTimeline']:
    pos = text.find(f'function {func}')
    print(f"--- JS Function: {func} (at {pos}) ---")
    if pos != -1:
        print(text[pos:pos+1500])

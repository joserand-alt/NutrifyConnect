import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

panels = re.findall(r'<section class="panel.*?" id="(.*?)">', text)
print("Panels found in template.html:", panels)

# Let's inspect each panel's content
for p in panels:
    pos = text.find(f'id="{p}"')
    pos_end = text.find('</section>', pos)
    print(f"Panel '{p}' length: {pos_end - pos} chars")

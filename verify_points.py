# Let's inspect the exact lines in template.html where:
# 1. nav tabs starts and ends
# 2. panel home starts
# 3. selectTab is located
# 4. renderAll is located
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("File length:", len(content))
assert '<nav class="tabs" id="tabs">' in content, "nav tabs not found"
assert '<section class="panel on" id="p-home">' in content, "panel on p-home not found"
assert 'function selectTab(' in content, "selectTab not found"
assert 'function renderAll(' in content, "renderAll not found"
print("All key insertion points verified successfully!")

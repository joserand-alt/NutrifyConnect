import re

with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.findall(r'<div[^>]*id=["\']p-[^"\']+["\'][^>]*>', text)
print("Panels with id=p-*:\n", m)

for item in m:
    pos = text.find(item)
    print(f"\n--- {item} (pos: {pos}) ---")
    print(text[pos:pos+300])

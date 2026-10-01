import re

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for tab navigation / buttons / switchers
print('--- Nav buttons / tabs HTML ---')
for m in re.finditer(r'<nav[^>]*>(.*?)</nav>', text, re.DOTALL):
    print(m.group(0)[:1500].encode('ascii', 'replace').decode('ascii'))

print('\n--- Occurrences of Progresso ---')
for line_no, line in enumerate(text.splitlines(), 1):
    if 'progresso' in line.lower():
        print(f"{line_no}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

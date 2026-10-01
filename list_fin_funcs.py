import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search all functions in the finance section
pos = text.find('// ABA FINANCEIRO')
fin_text = text[pos:]
for m in re.finditer(r'function\s+([a-zA-Z0-9_$]+)', fin_text):
    print(m.group(1))

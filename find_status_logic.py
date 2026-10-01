import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# find STATUS object definition
m = re.search(r'const STATUS\s*=\s*\{.*?\}\s*;', text, re.DOTALL)
if m:
    print("STATUS object:\n", m.group(0)[:500])

# find where status is assigned to students
for line in text.splitlines():
    if 'status' in line and ('student' in line or 's.status' in line or 'calcStatus' in line):
        print("Line:", line.strip()[:120])

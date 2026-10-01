import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's find all places where HTML elements or lists or tables or selects are populated with courses, modules, or turmas
matches = re.finditer(r'(function\s+[a-zA-Z0-9_]+\s*\([^)]*\)\s*\{|render[a-zA-Z0-9_]+|build[a-zA-Z0-9_]+)', html)

# Let's search specifically for what renders on the screen that looks like a vertical list of items or turmas
for m in re.finditer(r'([^\n]+\b(?:turma|modulo|disciplina|curso|ranking|grade|curriculo)\b[^\n]+)', html, re.IGNORECASE):
    line = m.group(0).strip()
    if any(k in line.lower() for k in ['render', 'innerhtml', 'createelement', 'table', 'tab-', 'select', 'options']):
        print(line[:120])

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Matches for .filters:")
for m in re.finditer(r'\.filters\b', text):
    start = max(0, m.start() - 100)
    end = min(len(text), m.end() + 100)
    print("---")
    print(text[start:end])

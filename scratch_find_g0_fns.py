with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'G0 MONITORAMENTO AO VIVO', text, re.I)]
print("Found G0 occurrences:", len(matches))
for i, m in enumerate(matches):
    # Find enclosing function
    fn_pos = text.rfind('function ', 0, m)
    fn_name = text[fn_pos:fn_pos+50].split('(')[0]
    print(f"Match {i+1} at {m} inside: {fn_name}")

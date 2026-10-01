template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'(\.tab|\.tabs|data-p)', text)
for m in matches:
    pos = m.start()
    if pos > 190000: # inside script
        print('Script match at', pos, ':')
        print(text[pos-50:pos+300].encode('ascii', errors='replace').decode('ascii'))
        print('---')
        break

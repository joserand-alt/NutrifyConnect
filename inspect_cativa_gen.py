with open('gerador.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'data_insc', content)]
print("data_insc in gerador.py:", len(matches))

# Let's inspect where Cativa students are processed in gerador.py
cativa_pos = content.find('cativa')
print("cativa in gerador.py:", cativa_pos)

# Let's search for how cativa students are loaded
pos = content.find('df_cativa')
if pos == -1:
    pos = content.find('cativa_api')
if pos == -1:
    pos = content.find('Cativa')
print("Cativa loading at:", pos)
print(content[pos-100:pos+2500].encode('ascii', 'replace').decode('ascii'))

import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect everything after drawFunil
pos_funil = text.find('function drawFunil')
print("After drawFunil:", text[pos_funil:pos_funil+1000])

# Let's find all function names in original_template.html
import re
all_funcs = re.findall(r'function\s+([a-zA-Z0-9_$]+)', text)
print("Total functions in original:", len(all_funcs))
print("Functions in original:", all_funcs)

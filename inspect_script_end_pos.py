import json
import re
import subprocess

with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect where the script ends and where DOMContentLoaded or init should go
idx_script_end = text.rfind('</script>')
print('Script end at line:', text[:idx_script_end].count('\n') + 1)
print('Code around script end:')
print(text[idx_script_end-500:idx_script_end])

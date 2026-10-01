template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Lines 1256 to 1320 in template.html ---')
for i in range(1255, min(1320, len(lines))):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

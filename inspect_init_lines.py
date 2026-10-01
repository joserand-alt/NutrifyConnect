template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Lines 1440 to 1530 ---')
for i in range(1439, min(1530, len(lines))):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

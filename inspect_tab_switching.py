template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Tab switching and initialization (lines 1480-1600) ---')
for i in range(1479, min(1600, len(lines))):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

print('\n--- renderRows function (lines 1760-1860) ---')
for i in range(1759, min(1860, len(lines))):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

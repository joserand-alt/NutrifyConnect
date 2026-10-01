template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Initialization code (lines 1450-1530) ---')
for i in range(1449, min(1530, len(lines))):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

print('\n--- buildHead and statusChips (lines 1640-1760) ---')
for i in range(1639, min(1760, len(lines))):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

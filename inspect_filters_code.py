template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Top bar controls (lines 630-690) ---')
for i in range(629, min(690, len(lines))):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

print('\n--- initFilters and related functions (lines 1250-1380) ---')
for i in range(1249, min(1380, len(lines))):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('--- Last 60 lines of template.html ---')
for i in range(max(0, len(lines)-60), len(lines)):
    print(f"{i+1}: {lines[i].rstrip().encode('ascii', 'replace').decode('ascii')}")

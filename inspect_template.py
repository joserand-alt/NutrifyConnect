import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print('Total lines:', len(lines))
for idx, line in enumerate(lines):
    if '<nav class="tabs"' in line:
        print(f'Nav tabs at line {idx+1}: {line.strip()[:100]}')
        for j in range(idx, min(idx+25, len(lines))):
            print(f'  {j+1}: {lines[j].strip()}')
        break
for idx, line in enumerate(lines):
    if 'id="p-home"' in line:
        print(f'p-home at line {idx+1}: {line.strip()[:100]}')
        break
for idx, line in enumerate(lines):
    if 'function selectTab(' in line:
        print(f'selectTab at line {idx+1}: {line.strip()[:100]}')
        for j in range(idx, min(idx+30, len(lines))):
            print(f'  {j+1}: {lines[j].strip()}')
        break
for idx, line in enumerate(lines):
    if 'function renderAll(' in line:
        print(f'renderAll at line {idx+1}: {line.strip()[:100]}')
        for j in range(idx, min(idx+25, len(lines))):
            print(f'  {j+1}: {lines[j].strip()}')
        break

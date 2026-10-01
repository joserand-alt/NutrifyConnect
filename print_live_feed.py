with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i in range(3375, 3465):
    print(f"{i+1}: {ascii(lines[i].strip()[:100])}")

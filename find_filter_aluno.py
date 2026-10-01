with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'filter-aluno' in l or 'selAluno' in l:
        print(f"Line {i+1}: {l.strip()[:100]}")

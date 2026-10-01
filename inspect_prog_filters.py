template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect the panel for prog
idx_prog = text.find('id="p-prog"')
if idx_prog != -1:
    print('--- Panel p-prog HTML ---')
    print(text[idx_prog:idx_prog+1500].encode('ascii', 'replace').decode('ascii'))
else:
    print('p-prog not found by id="p-prog"!')
    # search for class or data-p
    for line_no, line in enumerate(text.splitlines(), 1):
        if 'p-prog' in line or 'prog' in line:
            print(f"{line_no}: {line[:100].encode('ascii', 'replace').decode('ascii')}")

# Let's search for filter-curso and filter-aluno in JS
print('\n--- filter-curso and filter-aluno JS references ---')
for line_no, line in enumerate(text.splitlines(), 1):
    if 'filter-curso' in line or 'filter-aluno' in line or 'populate' in line or 'filterCurso' in line or 'initFilters' in line:
        print(f"{line_no}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

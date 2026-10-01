import re

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for all <select> tags in the whole file
selects = list(re.finditer(r'<select[^>]*>(.*?)</select>', text, re.DOTALL))
print(f'Total select tags: {len(selects)}')
for s in selects:
    # get the tag itself
    tag_match = re.search(r'<select[^>]*>', s.group(0))
    print('Select tag:', tag_match.group(0) if tag_match else 'unknown')

# Search for renderRows or how tab "Progresso por Aluno" (p-prog) is rendered
print('\n--- Search for renderRows or p-prog rendering ---')
for line_no, line in enumerate(text.splitlines(), 1):
    if 'renderRows' in line or 'p-prog' in line or 'tab-prog' in line or 'renderProgresso' in line or 'tbody' in line or 'renderAll' in line:
        print(f"{line_no}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

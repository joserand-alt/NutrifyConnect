template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for function drawExecView
for line_no, line in enumerate(text.splitlines(), 1):
    if 'function drawExecView' in line or 'p-exec' in line or 'exec-content' in line:
        print(f"{line_no}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

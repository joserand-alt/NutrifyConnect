template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

for line_no, line in enumerate(text.splitlines(), 1):
    if 'drawExecView' in line or 'drawHome' in line or 'drawFinanceiro' in line or 'init()' in line:
        print(f"{line_no}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

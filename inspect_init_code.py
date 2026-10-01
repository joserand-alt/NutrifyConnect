template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Search for buildHead, statusChips, init() and initialization code
for line_no, line in enumerate(text.splitlines(), 1):
    if 'buildHead' in line or 'statusChips' in line or 'init()' in line or 'DOMContentLoaded' in line or 'window.onload' in line:
        print(f"{line_no}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Search for switchTab or tab click
for line_no, line in enumerate(text.splitlines(), 1):
    if 'switchTab' in line or 'data-p' in line or 'tabs' in line and 'click' in line:
        print(f"{line_no}: {line[:120].encode('ascii', 'replace').decode('ascii')}")

idx_tab_event = text.find("tabs.onclick")
if idx_tab_event == -1:
    idx_tab_event = text.find("$('#tabs')")
if idx_tab_event == -1:
    idx_tab_event = text.find('$$(".tab")')

print(f'\nTab event index: {idx_tab_event}')
if idx_tab_event != -1:
    print(text[idx_tab_event-200:idx_tab_event+1200].encode('ascii', 'replace').decode('ascii'))

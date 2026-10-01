template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line_no, line in enumerate(lines, 1):
    if any(k in line for k in ['function computeUnifiedFinancialDataset', 'function getFinDataset', 'function getUnifiedFinancialDataset', 'coursesMap']):
        print(f"{line_no}: {line.strip().encode('ascii', 'replace').decode('ascii')}")

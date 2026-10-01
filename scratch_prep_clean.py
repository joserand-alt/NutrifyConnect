with open('apply_financial_projections_fix.py', 'r', encoding='utf-8') as f:
    py_code = f.read()

# Let's see how files are replaced
script_to_fix = """
with open('apply_financial_projections_fix.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx_new = text.find('new_func = \"\"\"')
idx_new_end = text.find('\"\"\"\\n\\nfiles = [', idx_new)
new_func = text[idx_new + len('new_func = \"\"\"'):idx_new_end]

files = [
    r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html',
    r'C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html',
    r'C:/Users/DELL/Desktop/Dash_InfectoCast/index.html'
]

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    idx1 = content.find('function computeUnifiedFinancialDataset')
    if idx1 == -1:
        print(f"Not found in {file_path}")
        continue
    idx_next_func = content.find('function fM(val)', idx1)
    if idx_next_func == -1:
        print(f"fM not found in {file_path}")
        continue

    # Clean replacement between idx1 and idx_next_func
    updated = content[:idx1] + new_func.strip() + '\\n\\n\\n' + content[idx_next_func:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated)
    print(f"Successfully cleaned & updated {file_path}")
"""

with open('scratch_do_clean_replace.py', 'w', encoding='utf-8') as f:
    f.write(script_to_fix)

print("Saved scratch_do_clean_replace.py")

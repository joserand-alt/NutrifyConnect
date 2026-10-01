import os
import json

dash_dir = r'C:/Users/DELL/Desktop/Dash_InfectoCast'
template_path = os.path.join(dash_dir, 'template.html')
index_path = os.path.join(dash_dir, 'index.html')
dash_gerado_path = os.path.join(dash_dir, 'dashboard_gerado.html')

# 1. Read existing DATA from index.html
with open(index_path, 'r', encoding='utf-8') as f:
    idx_content = f.read()

marker_start = "const DATA = "
idx_start = idx_content.find(marker_start)
if idx_start == -1:
    marker_start = "var DATA = "
    idx_start = idx_content.find(marker_start)

assert idx_start != -1, "Could not find DATA marker in index.html"

# Find end of DATA JSON
idx_data_start = idx_start + len(marker_start)

# In index.html, DATA is followed by script logic, let's find the closing of DATA:
# In template.html, DATA is followed by whatever comes after "};" or next statement.
# Let's inspect what follows DATA in index.html:
# Typically: 'const DATA = { ... };\n\n'
# Let's find ';\n\nfunction ' or ';\nlet CURRENT_DATA' or similar.

marker_next = ";\n\nlet CURRENT_DATA"
idx_next = idx_content.find(marker_next, idx_data_start)
if idx_next == -1:
    marker_next = ";\nlet CURRENT_DATA"
    idx_next = idx_content.find(marker_next, idx_data_start)
if idx_next == -1:
    marker_next = "let CURRENT_DATA"
    idx_next = idx_content.find(marker_next, idx_data_start)

assert idx_next != -1, "Could not find end of DATA in index.html"

json_data_str = idx_content[idx_data_start:idx_next].strip()
if json_data_str.endswith(';'):
    json_data_str = json_data_str[:-1].strip()

print(f"Extracted DATA string of length: {len(json_data_str)}")

# 2. Read template.html and split at const DATA = { ... };
with open(template_path, 'r', encoding='utf-8') as f:
    tpl_content = f.read()

tpl_start = tpl_content.find("const DATA = {")
assert tpl_start != -1, "Could not find const DATA = { in template.html"

tpl_end = tpl_content.find("};", tpl_start) + len("};")

pre = tpl_content[:tpl_start]
post = tpl_content[tpl_end:]

final_html = pre + "const DATA = " + json_data_str + ";" + post

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(final_html)

if os.path.exists(dash_gerado_path):
    with open(dash_gerado_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

print(f"Successfully compiled template.html into {index_path}! (size: {len(final_html)} bytes)")

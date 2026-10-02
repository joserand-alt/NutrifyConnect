import re

with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# find panels
panels = re.findall(r'<div[^>]*class=["\'][^"\']*panel[^"\']*["\'][^>]*id=["\']([^"\']+)["\']', text)
print("Panels found in template.html:", panels)

# find where p-fin starts and ends
m_fin = re.search(r'<div[^>]*id=["\']p-fin["\'][^>]*>', text)
if m_fin:
    start_pos = m_fin.start()
    print("Found p-fin at position:", start_pos)
    print("Snippet of p-fin:\n", text[start_pos:start_pos+1000])

# find drawFinanceiro definition
m_fn = re.search(r'function\s+drawFinanceiro\s*\([^)]*\)\s*\{', text)
if m_fn:
    start_pos = m_fn.start()
    print("\nFound drawFinanceiro at position:", start_pos)
    print("Snippet of drawFinanceiro:\n", text[start_pos:start_pos+1200])

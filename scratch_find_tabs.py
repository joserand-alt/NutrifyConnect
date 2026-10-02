import re

with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find navigation tabs in HTML
nav_match = re.search(r'<nav[^>]*>.*?</nav>', text, re.DOTALL | re.IGNORECASE)
with open("tabs_output.txt", "w", encoding="utf-8") as out:
    if nav_match:
        out.write("NAV BLOCK:\n" + nav_match.group(0)[:4000] + "\n\n")
        
    for fn_name in ['selectTab', 'showTab', 'switchTab', 'openTab', 'changeTab', 'renderTab', 'setTab', 'renderAll', 'renderView']:
        m_fn = re.search(rf'function\s+{fn_name}\s*\([^)]*\)\s*\{{', text)
        if m_fn:
            out.write(f"\nFound function: {fn_name}\n")
            start = m_fn.start()
            out.write(text[start:start+1500] + "\n")

print("Wrote to tabs_output.txt")

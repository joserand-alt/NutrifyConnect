template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

broken_block = """// INIT
$$('.tab').forEach(b => {
    b.onclick = () => {
        // Tabs inicializadas via selectTab
$$('.tab')[0].click();"""

clean_block = """// INIT
$$('.tab')[0].click();"""

if broken_block in text:
    text = text.replace(broken_block, clean_block)
    print("Fixed broken block directly")
else:
    # Use regex
    import re
    p = re.compile(r"// INIT\s*\$\$'\.tab'\.forEach\(b => \{\s*b\.onclick = \(\) => \{\s*// Tabs inicializadas via selectTab\s*\$\$'\.tab'\[0\]\.click\(\);")
    text, n = p.subn(clean_block, text)
    print("Regex fixed broken block:", n)

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved template.html")

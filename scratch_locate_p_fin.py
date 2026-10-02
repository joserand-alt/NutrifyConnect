import re

with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# find p-fin section
m_fin = re.search(r'<section[^>]*id=["\']p-fin["\'][^>]*>.*?</section>', text, re.DOTALL)
if m_fin:
    print("Found p-fin section length:", len(m_fin.group(0)))
    print("p-fin starts at:", m_fin.start(), "ends at:", m_fin.end())
    print("Snippet after p-fin:\n", text[m_fin.end():m_fin.end()+300])

# find nav tabs
m_nav = re.search(r'<nav[^>]*id=["\']tabs["\'][^>]*>.*?</nav>', text, re.DOTALL)
if m_nav:
    print("\nNav tabs snippet:\n", m_nav.group(0))

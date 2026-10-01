with open('template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find the G1 header marker
import re
g1_matches = [m.start() for m in re.finditer(r'G1', content)]
print("G1 matches:", g1_matches)
for p in g1_matches:
    print("At", p, ":", content[p:p+100].encode('ascii', 'replace').decode('ascii'))

# Let's find the handlers after 538000
print("\n--- Content around 538600 ---")
print(content[538000:543000].encode('ascii', 'replace').decode('ascii'))

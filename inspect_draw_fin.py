import json
import re

# Load template.html
with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

# Let's inspect drawFinanceiro in template.html to see how financial tab renders its KPIs
pos_df = tmpl.find('function drawFinanceiro')
print("=== drawFinanceiro snippet ===")
print(tmpl[pos_df:pos_df+2500].encode('ascii', 'replace').decode('ascii'))

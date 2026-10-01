import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for tab click listeners in the script
script_match = re.search(r'<script>(.*?)</script>', text, re.DOTALL)
if script_match:
    script = script_match.group(1)
    for m in re.finditer(r'\.tab\b|\bdata-p\b|p-fin\b|drawFinanceiro|renderFin', script):
        idx = m.start()
        print(f"Match at {idx}: {repr(script[max(0, idx-40):min(len(script), idx+120)])}")

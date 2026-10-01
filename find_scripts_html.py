import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
print(f"Total scripts in dashboard_gerado.html: {len(scripts)}")
for idx, s in enumerate(scripts):
    print(f"Script {idx} length: {len(s)}")
    print(s[:300])
    print("---")

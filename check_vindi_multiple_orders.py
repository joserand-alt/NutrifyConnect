import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    v_fat = data.get('financeiro', {}).get('faturas_tabela', [])
    print(f"Total Vindi faturas: {len(v_fat)}")
    
    # Check if any student in Vindi has multiple subscriptions where one has paid and another has 0 paid
    by_email = {}
    for f in v_fat:
        em = str(f.get('email', '')).lower().strip()
        by_email.setdefault(em, []).append(f)
        
    print(f"Total unique emails in Vindi faturas: {len(by_email)}")
    
    # Check if Laura is in Vindi
    laura_v = by_email.get('laurawarlitzer@gmail.com', [])
    print(f"Laura in Vindi: {len(laura_v)} faturas:")
    for f in laura_v:
        print(" ", f.get('id'), f.get('status'), f.get('valor'), f.get('plano'))

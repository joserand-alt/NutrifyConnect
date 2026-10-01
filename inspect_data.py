import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print("Top keys in DATA:", list(data.keys()))
    if 'financeiro' in data:
        print("financeiro keys:", list(data['financeiro'].keys()))
        print("financeiro.kpis:", data['financeiro'].get('kpis'))
    if 'financeiro_asaas' in data:
        print("financeiro_asaas keys:", list(data['financeiro_asaas'].keys()))
        print("financeiro_asaas.kpis:", data['financeiro_asaas'].get('kpis'))
    if 'funil' in data:
        print("funil keys:", list(data['funil'].keys()))
        print("funil.kpis:", data['funil'].get('kpis'))
    if 'students' in data:
        print("students count:", len(data['students']))
        print("student sample:", data['students'][0])
    if 'meta' in data:
        print("meta:", data['meta'])
    if 'courses' in data:
        print("courses count:", len(data['courses']))

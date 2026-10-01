import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])
    laura_a = [f for f in a_fat if 'laurawarlitzer' in str(f.get('email', '')).lower()]
    print("Laura Asaas Invoices:")
    for f in laura_a:
        print(f"  ID: {f.get('id')} | Forma: {f.get('forma_pagamento')} | Valor: {f.get('valor')} | Venc: {f.get('vencimento')} | Status: {f.get('status')} | Desc: {f.get('description')} | Plano: {f.get('plano')}")

import os

vpath = r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_service.py'
with open(vpath, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix status check for paid fatura avulsa
code = code.replace(
    "has_paid_renegociacao = any(b.get('is_fatura_avulsa') and b.get('status') == 'paid' for b in unique_bills)",
    "has_paid_renegociacao = any(b.get('is_fatura_avulsa') and b.get('status') in ['paid', 'pago'] for b in unique_bills)"
)

code = code.replace(
    "paid_bills_count = sum(1 for b in unique_bills if b['status'] == 'paid')",
    "paid_bills_count = sum(1 for b in unique_bills if b['status'] in ['paid', 'pago'])"
)

with open(vpath, 'w', encoding='utf-8') as f:
    f.write(code)

cache_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json'
if os.path.exists(cache_file):
    os.remove(cache_file)

print('Fixed paid status check in vindi_service.py!')

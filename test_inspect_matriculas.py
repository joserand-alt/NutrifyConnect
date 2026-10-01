import json
import re
import datetime

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract DATA from index.html
start = html.find('const DATA = {')
end = html.find('};', start) + 1
data_str = html[start + len('const DATA = '):end]

data = json.loads(data_str)
print("DATA keys:", list(data.keys()))

students = data.get('students', [])
print(f"Total students in DATA: {len(students)}")

vindi = data.get('financeiro', {})
asaas = data.get('financeiro_asaas', {})

v_faturas = vindi.get('faturas_tabela', [])
a_faturas = asaas.get('faturas_tabela', [])

print(f"Vindi faturas count: {len(v_faturas)}")
print(f"Asaas faturas count: {len(a_faturas)}")

# Let's inspect student structure
if students:
    s0 = students[0]
    print("\nSample student keys:", list(s0.keys()))
    print("Sample student dates:", {
        'data_insc': s0.get('data_insc'),
        'data_matricula': s0.get('data_matricula'),
        'origem': s0.get('origem'),
        'email': s0.get('email'),
        'status': s0.get('status')
    })

# Check first payment dates vs registration dates
print("\n--- Analysing First Payments & Registration Dates ---")
first_payments = {}
for f in (v_faturas + a_faturas):
    st = (f.get('status') or '').lower()
    if st in ['pago', 'paid', 'received', 'confirmed']:
        em = (f.get('email') or '').lower().strip()
        dt_str = f.get('data_pagamento') or f.get('data_pagamento_iso') or f.get('data') or ''
        if em and dt_str:
            if em not in first_payments:
                first_payments[em] = dt_str
            else:
                # Keep earliest
                if dt_str < first_payments[em]:
                    first_payments[em] = dt_str

print(f"Total students with identified paid invoice: {len(first_payments)}")

# Let's inspect registration dates across students
with_data_insc = [s for s in students if s.get('data_insc')]
print(f"Students with data_insc: {len(with_data_insc)}")
if with_data_insc:
    print("Sample data_insc values:", [s.get('data_insc') for s in with_data_insc[:10]])

# Let's check origins
origins = {}
for s in students:
    orig = s.get('origem', 'Desconhecida')
    origins[orig] = origins.get(orig, 0) + 1
print("Origins breakdown:", origins)

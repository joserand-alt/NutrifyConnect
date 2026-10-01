import json
from datetime import datetime, timedelta

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])

students = data.get('students', [])
vindi = data.get('financeiro', {})
asaas = data.get('financeiro_asaas', {})

v_faturas = vindi.get('faturas_tabela', [])
a_faturas = asaas.get('faturas_tabela', [])

def parse_date(d_str):
    if not d_str or str(d_str).lower() in ['none', 'nan', 'null', '']:
        return None
    s = str(d_str).strip()
    for fmt in [
        '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S.%f'
    ]:
        try:
            return datetime.strptime(s.split('+')[0].split('.')[0], fmt.split('.')[0])
        except:
            pass
    return None

# Map first payments
first_pay_map = {}

for f in v_faturas:
    st = (f.get('status') or '').lower()
    if st in ['pago', 'paid', 'received', 'confirmed']:
        em = (f.get('email') or '').lower().strip()
        nm = (f.get('aluno') or '').lower().strip()
        dt = parse_date(f.get('data_pagamento') or f.get('data_pagamento_iso') or f.get('data'))
        if dt:
            if em and (em not in first_pay_map or dt < first_pay_map[em]['date']):
                first_pay_map[em] = {'date': dt, 'gateway': 'Vindi', 'val': f.get('valor')}
            if nm and (nm not in first_pay_map or dt < first_pay_map[nm]['date']):
                first_pay_map[nm] = {'date': dt, 'gateway': 'Vindi', 'val': f.get('valor')}

for f in a_faturas:
    st = (f.get('status') or '').lower()
    if st in ['pago', 'paid', 'received', 'confirmed']:
        em = (f.get('email') or '').lower().strip()
        nm = (f.get('aluno') or '').lower().strip()
        dt = parse_date(f.get('data_pagamento') or f.get('data_pagamento_iso') or f.get('data'))
        if dt:
            if em and (em not in first_pay_map or dt < first_pay_map[em]['date']):
                first_pay_map[em] = {'date': dt, 'gateway': 'Asaas', 'val': f.get('valor')}
            if nm and (nm not in first_pay_map or dt < first_pay_map[nm]['date']):
                first_pay_map[nm] = {'date': dt, 'gateway': 'Asaas', 'val': f.get('valor')}

# Reference Date: 2026-09-18
now = datetime(2026, 9, 18, 17, 30)
t24h = now - timedelta(hours=24)
t30d = now - timedelta(days=30)

matriculas = []
for s in students:
    em = (s.get('email') or '').lower().strip()
    nm = (s.get('nome') or '').strip()
    
    # Check internal/test accounts
    cr = (s.get('curso') or '').upper()
    if 'NUTRIFY' in cr or any(x in em for x in ['@infectocast', '@integralmedica', '@nutrify', '@cativa', 'teste', 'gcotta29', 'j.o.s.e.r.a.n.d@gmail.com']):
        continue
    
    dt_insc = parse_date(s.get('data_insc') or s.get('data_inscricao') or s.get('data_matricula'))
    pay_info = first_pay_map.get(em) or first_pay_map.get(nm.lower())

    eff_date = None
    origem_sinal = None

    if pay_info:
        eff_date = pay_info['date']
        origem_sinal = f"Primeiro Pagamento ({pay_info['gateway']})"
    elif dt_insc:
        eff_date = dt_insc
        origem_sinal = f"Cadastro {s.get('plataforma') or 'Academy'}"

    if eff_date:
        matriculas.append({
            'nome': nm,
            'email': em,
            'curso': s.get('curso') or 'PLATAFORMA GERAL',
            'data': eff_date,
            'data_fmt': eff_date.strftime('%d/%m/%Y %H:%M'),
            'origem_sinal': origem_sinal,
            'status': s.get('status') or 'Ativo',
            'is_24h': eff_date >= t24h,
            'is_30d': eff_date >= t30d
        })

matriculas_24h = [m for m in matriculas if m['is_24h']]
matriculas_30d = [m for m in matriculas if m['is_30d']]

print(f"Total matriculas validas: {len(matriculas)}")
print(f"Matriculas 24h: {len(matriculas_24h)}")
print(f"Matriculas 30d: {len(matriculas_30d)}")

print("\nBreakdown 24h por origem:")
b24 = {}
for m in matriculas_24h:
    b24[m['origem_sinal']] = b24.get(m['origem_sinal'], 0) + 1
print(b24)

print("\nBreakdown 30d por origem:")
b30 = {}
for m in matriculas_30d:
    b30[m['origem_sinal']] = b30.get(m['origem_sinal'], 0) + 1
print(b30)

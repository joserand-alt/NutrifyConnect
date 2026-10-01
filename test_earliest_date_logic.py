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

# Map first paid invoice or first invoice per student
first_pay_map = {}

for f in (v_faturas + a_faturas):
    st = (f.get('status') or '').lower()
    if st in ['pago', 'paid', 'received', 'confirmed']:
        em = (f.get('email') or '').lower().strip()
        nm = (f.get('aluno') or '').lower().strip()
        # If data_pagamento is empty, use vencimento!
        dt_raw = f.get('data_pagamento') or f.get('data_pagamento_iso') or f.get('vencimento') or f.get('vencimento_iso') or f.get('data') or ''
        d = parse_date(dt_raw)
        if d:
            if em:
                if em not in first_pay_map or d < first_pay_map[em]['date']:
                    first_pay_map[em] = {'date': d, 'gateway': f.get('gateway') or ('Vindi' if f in v_faturas else 'Asaas'), 'val': f.get('valor')}
            if nm:
                if nm not in first_pay_map or d < first_pay_map[nm]['date']:
                    first_pay_map[nm] = {'date': d, 'gateway': f.get('gateway') or ('Vindi' if f in v_faturas else 'Asaas'), 'val': f.get('valor')}

# Check Gislayne specifically
gis_pay = first_pay_map.get('gislayneoliveira2018@gmail.com')
print("Gislayne first pay map:", gis_pay)

# Now check all students
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
    
    # In students, let's also fix dt_insc if it took a future invoice
    # If student has vindi faturas, find the earliest fatura date
    earliest_vindi_date = None
    if s.get('vindi') and isinstance(s['vindi'], dict):
        fts = s['vindi'].get('faturas', [])
        dates = []
        for f in fts:
            d = parse_date(f.get('data_pagamento') or f.get('vencimento'))
            if d:
                dates.append(d)
        if dates:
            earliest_vindi_date = min(dates)

    earliest_asaas_date = None
    if s.get('asaas') and isinstance(s['asaas'], dict):
        fts = s['asaas'].get('faturas', [])
        dates = []
        for f in fts:
            d = parse_date(f.get('data_pagamento') or f.get('vencimento'))
            if d:
                dates.append(d)
        if dates:
            earliest_asaas_date = min(dates)

    pay_info = first_pay_map.get(em) or first_pay_map.get(nm.lower())
    dt_insc = parse_date(s.get('data_insc') or s.get('data_inscricao'))

    # If dt_insc is in the future (> now) or from a recent invoice by mistake, fallback to earliest date or first log
    dt_first_log = parse_date(s.get('first'))
    
    # Determine the real registration/enrollment date:
    # Priority:
    # 1. First payment date
    # 2. Earliest financial contract/invoice date (Vindi/Asaas)
    # 3. First login date (if earlier)
    # 4. dt_insc (if valid and not future)
    
    eff_date = None
    origem_sinal = None

    candidates = []
    if pay_info:
        candidates.append((pay_info['date'], f"Primeiro Pagamento ({pay_info['gateway']})", 1))
    if earliest_vindi_date:
        candidates.append((earliest_vindi_date, "Contrato Vindi", 2))
    if earliest_asaas_date:
        candidates.append((earliest_asaas_date, "Contrato Asaas", 2))
    if dt_first_log:
        candidates.append((dt_first_log, "Primeiro Acesso / Log", 3))
    if dt_insc and dt_insc <= now:
        candidates.append((dt_insc, f"Cadastro {s.get('plataforma') or 'Academy'}", 4))

    if candidates:
        # Sort by date ascending (earliest real event!)
        candidates.sort(key=lambda x: x[0])
        eff_date = candidates[0][0]
        origem_sinal = candidates[0][1]

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

print(f"\nTotal matriculas: {len(matriculas)}")
print(f"Matriculas 24h: {len(matriculas_24h)}")
print(f"Matriculas 30d: {len(matriculas_30d)}")

print("\n--- Lista Matrículas 24h ---")
for m in matriculas_24h:
    print(f"  {m['nome']} ({m['email']}): {m['data_fmt']} - {m['origem_sinal']} [{m['curso']}]")

print("\n--- Gislayne status in final matriculas ---")
for m in matriculas:
    if 'gislayne' in m['email']:
        print(m)

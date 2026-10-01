import json
from datetime import datetime, timedelta

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])

students = data.get('students', [])
v_faturas = data.get('financeiro', {}).get('faturas_tabela', [])
a_faturas = data.get('financeiro_asaas', {}).get('faturas_tabela', [])

def parse_date(d_str):
    if not d_str or str(d_str).lower() in ['none', 'nan', 'null', '']:
        return None
    s = str(d_str).strip()
    # Format dd/mm/yyyy or dd/mm/yyyy hh:mm:ss
    for fmt in ['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S.%f']:
        try:
            return datetime.strptime(s.split('+')[0].split('.')[0], fmt.split('.')[0])
        except:
            pass
    return None

# Find first payment date per student
first_payment_map = {}
for f in (v_faturas + a_faturas):
    st = (f.get('status') or '').lower()
    if st in ['pago', 'paid', 'received', 'confirmed']:
        em = (f.get('email') or '').lower().strip()
        dt_raw = f.get('data_pagamento') or f.get('data_pagamento_iso') or f.get('data') or ''
        d = parse_date(dt_raw)
        if em and d:
            if em not in first_payment_map or d < first_payment_map[em]:
                first_payment_map[em] = d

# Reference Date: assuming current system date or max date in logs/payments
# In 2026-09-18
now = datetime(2026, 9, 18, 17, 30)
t24h = now - timedelta(hours=24)
t30d = now - timedelta(days=30)

print(f"Reference NOW: {now}")
print(f"24h threshold: {t24h}")
print(f"30d threshold: {t30d}")

# Let's inspect how enrollment date (data de matrícula) is determined:
# Priority / Best signal:
# 1. First Payment Date (if student paid)
# 2. Platform Registration Date (Academy or Cativa: data_insc / data_matricula)

matriculas_24h = []
matriculas_30d = []
all_matriculas = []

for s in students:
    em = (s.get('email') or '').lower().strip()
    nm = s.get('nome')
    plataforma = s.get('plataforma')
    dt_insc = parse_date(s.get('data_insc') or s.get('data_inscricao'))
    dt_first_pay = first_payment_map.get(em)

    # Best signal of matricula: first payment, or registration date in Academy / Cativa
    # If student paid, first payment date is the commercial matriculation date.
    # Otherwise or if platform registration is available, take the earliest valid date or the platform date.
    effective_matricula_date = None
    signal_type = None

    if dt_first_pay and dt_insc:
        # If both exist, usually first payment or platform enrollment (whichever is primary or earliest)
        effective_matricula_date = dt_first_pay # First payment is the best signal as specified by user!
        signal_type = 'Primeiro Pagamento'
    elif dt_first_pay:
        effective_matricula_date = dt_first_pay
        signal_type = 'Primeiro Pagamento'
    elif dt_insc:
        effective_matricula_date = dt_insc
        signal_type = f'Cadastro {plataforma or "Plataforma"}'

    if effective_matricula_date:
        all_matriculas.append({
            'email': em,
            'nome': nm,
            'data_matricula': effective_matricula_date,
            'signal': signal_type,
            'plataforma': plataforma,
            'curso': s.get('curso')
        })
        if effective_matricula_date >= t24h:
            matriculas_24h.append((em, nm, effective_matricula_date, signal_type, s.get('curso')))
        if effective_matricula_date >= t30d:
            matriculas_30d.append((em, nm, effective_matricula_date, signal_type, s.get('curso')))

print(f"\nTotal Matrículas Calculadas: {len(all_matriculas)}")
print(f"Matrículas 24h: {len(matriculas_24h)}")
print(f"Matrículas 30d: {len(matriculas_30d)}")

print("\n--- Amostra de Matrículas nas Últimas 24h ---")
for m in matriculas_24h:
    print(f" - {m[1]} ({m[0]}): {m[2].strftime('%d/%m/%Y %H:%M')} [{m[3]}] - {m[4]}")

print("\n--- Amostra de Matrículas nos Últimos 30 Dias (Top 10) ---")
for m in matriculas_30d[:10]:
    print(f" - {m[1]} ({m[0]}): {m[2].strftime('%d/%m/%Y %H:%M')} [{m[3]}] - {m[4]}")

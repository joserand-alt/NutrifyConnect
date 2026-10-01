import json

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = 'const DATA = '
i1 = html.find(m)
i2 = html.find(';\n\nlet CURRENT_DATA', i1)
if i2 == -1: i2 = html.find(';\nlet CURRENT_DATA', i1)
data = json.loads(html[i1+len(m):i2].strip().rstrip(';'))

vSubs = data.get('financeiro', {}).get('subscriptions', [])
vFaturas = data.get('financeiro', {}).get('faturas_tabela', [])

# Resolve canonical course function
def resolve_canonical(name):
    n = str(name or '').upper().strip()
    if 'INFECTOPED' in n or 'PEDIATR' in n:
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA'
    if 'CCIH' in n or 'PREVENCAO' in n or 'CONTROLE DE INFECCAO' in n:
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'
    if 'IMUNODEPRIMIDO' in n:
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'
    if 'ORTOPED' in n or 'MOLES' in n:
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES'
    if 'MULTI-R' in n or 'MULTIR' in n or 'JORNADA' in n:
        return 'JORNADA MULTI-R'
    if 'FUNGO' in n or 'ANTIFUNGICO' in n:
        return 'DO FUNGO AO ANTIFUNGICO'
    if 'SOS' in n or 'ANTIBIOTICO' in n or 'S.O.S' in n:
        return 'S.O.S ANTIBIOTICO'
    if 'INFECTOXPERT' in n:
        return 'INFECTOXPERT'
    return 'PLATAFORMA GERAL'

# Students map
email_to_course = {}
for s in data.get('students', []):
    em = str(s.get('email', '')).lower().strip()
    c = resolve_canonical(s.get('curso'))
    if em: email_to_course[em] = c

# Check faturas for PED
ped_faturas = []
for f in vFaturas:
    em = str(f.get('email', '')).lower().strip()
    c = resolve_canonical(f.get('curso') or email_to_course.get(em))
    if c == 'POS-GRADUACAO EM INFECTOPEDIATRIA':
        ped_faturas.append(f)

print(f"Total PED faturas: {len(ped_faturas)}")

# Check monthly payments in PED faturas
monthly_paid = {}
for f in ped_faturas:
    st = str(f.get('status', '')).lower()
    if st in ['paid', 'pago', 'received', 'confirmed']:
        val = float(f.get('valor') or 0)
        dt = str(f.get('data_pagamento_iso') or f.get('data_pagamento') or f.get('data') or '')
        ym = dt[:7]
        if ym:
            monthly_paid[ym] = monthly_paid.get(ym, 0) + val

print("\nPED Historico Mensal Pago:")
for ym in sorted(monthly_paid.keys())[-10:]:
    print(f"  {ym}: R$ {monthly_paid[ym]:.2f}")

# Check PED subscriptions
ped_subs_real = []
for s in vSubs:
    em = str(s.get('customer_email', '')).lower().strip()
    c = resolve_canonical(s.get('curso') or email_to_course.get(em))
    if c == 'POS-GRADUACAO EM INFECTOPEDIATRIA' and s.get('status_financeiro') == 'adimplente':
        ped_subs_real.append(s)

print(f"\nTotal Active PED subscriptions: {len(ped_subs_real)}")
total_mrr = sum(float(s.get('valor_parcela') or 0) for s in ped_subs_real)
print(f"Total PED MRR: R$ {total_mrr:.2f}")

# Now let's trace the 18-month simulation for each subscription!
proj_months = [0] * 18
for s in ped_subs_real:
    price = float(s.get('valor_parcela') or 0)
    planoStr = str(s.get('plano', '')).upper()
    totalCycles = 18
    if '24' in planoStr: totalCycles = 24
    elif '12' in planoStr or 'ANUAL' in planoStr: totalCycles = 12
    elif '6' in planoStr or 'SEMESTRAL' in planoStr: totalCycles = 6

    fats = s.get('faturas', [])
    paidCount = len([f for f in fats if f.get('status') in ['paid', 'pago']])
    remainingCycles = max(0, totalCycles - paidCount)

    for m in range(18):
        if m < remainingCycles:
            proj_months[m] += price

print("\nSimulated Future 18 Months Projection for PED:")
month_names = ['Set/26', 'Out/26', 'Nov/26', 'Dez/26', 'Jan/27', 'Fev/27', 'Mar/27', 'Abr/27', 'Mai/27', 'Jun/27', 'Jul/27', 'Ago/27']
for idx, m_val in enumerate(proj_months[:12]):
    lbl = month_names[idx] if idx < len(month_names) else f"M+{idx}"
    print(f"  {lbl} (m={idx}): R$ {m_val:.2f}")

# Check which subscriptions end early!
print("\nSubscriptions breakdown by remaining cycles:")
for s in ped_subs_real:
    price = float(s.get('valor_parcela') or 0)
    planoStr = str(s.get('plano', '')).upper()
    totalCycles = 18
    if '24' in planoStr: totalCycles = 24
    elif '12' in planoStr or 'ANUAL' in planoStr: totalCycles = 12
    elif '6' in planoStr or 'SEMESTRAL' in planoStr: totalCycles = 6
    fats = s.get('faturas', [])
    paidCount = len([f for f in fats if f.get('status') in ['paid', 'pago']])
    remaining = max(0, totalCycles - paidCount)
    if remaining < 12:
        print(f"  {s.get('customer_name')}: R$ {price}/mês | Total cycles: {totalCycles}, Paid: {paidCount}, Remaining: {remaining} -> ENDS IN {remaining} MONTHS!")

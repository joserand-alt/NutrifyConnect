import json
from datetime import datetime, date, timedelta
import calendar

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json', 'r', encoding='utf-8') as f:
    vc = json.load(f)

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    ac = json.load(f)

today = date.today()
end_of_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
d30_date = today + timedelta(days=30)

def norm_course(c):
    c = (c or '').strip().upper()
    if 'PREV' in c or 'CCIH' in c or 'HOSPITALAR' in c:
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'
    elif 'IMUNO' in c or 'DEPRIMIDO' in c:
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'
    elif 'ORTO' in c:
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES'
    elif 'PED' in c:
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA'
    elif 'MULTI' in c or 'JORNADA' in c:
        return 'JORNADA MULTI-R'
    elif 'FUNGO' in c or 'ANTIFUNGICO' in c:
        return 'DO FUNGO AO ANTIFUNGICO'
    elif 'SOS' in c or 'ANTIBIOTICO' in c or 'ATB' in c:
        return 'S.O.S ANTIBIOTICO'
    elif 'GERAL' in c or 'PLATAFORMA' in c:
        return 'PLATAFORMA GERAL'
    return c or 'PLATAFORMA GERAL'

courses = {}
def get_cm(c_name):
    c = norm_course(c_name)
    if c not in courses:
        courses[c] = {
            'curso': c,
            'pago_total': 0.0,
            'pago_set26': 0.0,
            'pago_ago26': 0.0,
            'a_vencer_set26': 0.0,
            'mrr': 0.0,
            'proj_30d': 0.0,
            'atraso': 0.0
        }
    return courses[c]

# 1. Process Vindi Faturas
v_faturas = vc.get('financeiro', {}).get('faturas_tabela', [])
for f in v_faturas:
    c_name = f.get('curso') or 'PLATAFORMA GERAL'
    cm = get_cm(c_name)
    st = (f.get('status') or '').lower()
    val = float(f.get('valor') or 0.0)
    dt_pag = (f.get('data_pagamento') or f.get('data_pagamento_iso') or '').strip()
    dt_venc = (f.get('vencimento') or f.get('vencimento_iso') or '').strip()
    
    if st in ['pago', 'paid']:
        cm['pago_total'] += val
        if '09/2026' in dt_pag or '2026-09' in dt_pag or '/09/26' in dt_pag:
            cm['pago_set26'] += val
        elif '08/2026' in dt_pag or '2026-08' in dt_pag or '/08/26' in dt_pag:
            cm['pago_ago26'] += val
    elif st in ['em_atraso', 'overdue']:
        cm['atraso'] += val

# 2. Process Asaas Faturas
email_to_course = {}
for email, st_info in vc.get('data', {}).items():
    if st_info.get('curso'):
        email_to_course[email.strip().lower()] = st_info['curso']

a_faturas = ac.get('financeiro', {}).get('faturas_tabela', [])
for f in a_faturas:
    em = (f.get('email') or '').strip().lower()
    c_name = email_to_course.get(em) or f.get('curso') or 'PLATAFORMA GERAL'
    cm = get_cm(c_name)
    st = (f.get('status') or '').lower()
    val = float(f.get('valor') or 0.0)
    dt_pag = (f.get('data_pagamento') or f.get('data_pagamento_iso') or '').strip()
    dt_venc = (f.get('vencimento') or f.get('vencimento_iso') or '').strip()
    
    if st in ['pago', 'paid', 'received', 'confirmed']:
        cm['pago_total'] += val
        if '09/2026' in dt_pag or '2026-09' in dt_pag or '/09/26' in dt_pag:
            cm['pago_set26'] += val
        elif '08/2026' in dt_pag or '2026-08' in dt_pag or '/08/26' in dt_pag:
            cm['pago_ago26'] += val
    elif st in ['pendente', 'pending', 'a_vencer']:
        if dt_venc:
            try:
                d_dt = datetime.strptime(dt_venc[:10], '%Y-%m-%d').date() if '-' in dt_venc else datetime.strptime(dt_venc[:10], '%d/%m/%Y').date()
                if today <= d_dt <= end_of_month:
                    cm['a_vencer_set26'] += val
                if today <= d_dt <= d30_date:
                    cm['proj_30d'] += val
            except:
                pass

# 3. Process Vindi Subscriptions
v_subs = vc.get('subscriptions', [])
for sub in v_subs:
    if sub.get('status_financeiro') == 'adimplente':
        c_name = sub.get('curso') or 'PLATAFORMA GERAL'
        cm = get_cm(c_name)
        price = float(sub.get('valor_parcela') or 0.0)
        cm['mrr'] += price
        
        prox_fmt = sub.get('proximo_vencimento')
        if prox_fmt:
            try:
                p_dt = datetime.strptime(prox_fmt, '%d/%m/%Y').date()
                if today <= p_dt <= end_of_month:
                    cm['a_vencer_set26'] += price
                if today <= p_dt <= d30_date:
                    cm['proj_30d'] += price
            except:
                cm['a_vencer_set26'] += price
                cm['proj_30d'] += price
        else:
            cm['a_vencer_set26'] += price
            cm['proj_30d'] += price

# 4. Process Asaas Active Customers / MRR
for email, st_info in ac.get('data', {}).items():
    if st_info.get('status_financeiro') == 'adimplente':
        c_name = email_to_course.get(email.strip().lower()) or st_info.get('curso') or 'PLATAFORMA GERAL'
        cm = get_cm(c_name)
        price = float(st_info.get('valor_parcela') or st_info.get('mrr') or 0.0)
        cm['mrr'] += price

print(f"{'CURSO':<40} | {'PAGO TOTAL':<14} | {'SET/26 PAGO':<12} | {'A VENCER SET':<12} | {'MES VIGENTE':<12} | {'MRR':<10} | {'D+30':<10}")
print("-" * 125)

tot_pago_tot = 0
tot_pago_set = 0
tot_venc_set = 0
tot_rec_mes = 0
tot_mrr = 0
tot_p30 = 0

for c, cm in sorted(courses.items(), key=lambda x: x[1]['mrr'], reverse=True):
    rec_mes = cm['pago_set26'] + cm['a_vencer_set26']
    tot_pago_tot += cm['pago_total']
    tot_pago_set += cm['pago_set26']
    tot_venc_set += cm['a_vencer_set26']
    tot_rec_mes += rec_mes
    tot_mrr += cm['mrr']
    tot_p30 += cm['proj_30d']
    print(f"{c[:40]:<40} | R$ {cm['pago_total']:>11,.2f} | R$ {cm['pago_set26']:>9,.2f} | R$ {cm['a_vencer_set26']:>9,.2f} | R$ {rec_mes:>9,.2f} | R$ {cm['mrr']:>7,.2f} | R$ {cm['proj_30d']:>7,.2f}")

print("=" * 125)
print(f"{'TOTAL CONSOLIDADO':<40} | R$ {tot_pago_tot:>11,.2f} | R$ {tot_pago_set:>9,.2f} | R$ {tot_venc_set:>9,.2f} | R$ {tot_rec_mes:>9,.2f} | R$ {tot_mrr:>7,.2f} | R$ {tot_p30:>7,.2f}")

import json, os
from datetime import datetime, timedelta

vindi_service_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_service.py'
with open(vindi_service_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace get_vindi_data in vindi_service.py with the clean subscription-isolated logic
old_func_pat = r'def get_vindi_data\(force_reload=False\):[\s\S]*?return \{\s*"cached_at": datetime\.now\(\)\.isoformat\(\),\s*"data": students_vindi,\s*"financeiro": \{[\s\S]*?\}\s*\}'

new_func = """def get_vindi_data(force_reload=False):
    \"\"\"
    Retorna o dicionário completo com dados por aluno e agregações globais da Aba Financeiro.
    \"\"\"
    if not force_reload and os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            cached_at = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if datetime.now() - cached_at < timedelta(hours=CACHE_TTL_HOURS) and 'financeiro' in cached:
                print(f"[VINDI CACHE] Carregados dados da Vindi com financeiro global ({len(cached.get('data', {}))} alunos).")
                return cached
        except Exception as e:
            print(f"[VINDI CACHE] Rebuscando: {e}")

    subs = fetch_all_vindi_subscriptions()
    bills = fetch_all_vindi_bills()
    now = datetime.now()

    # Regra de negócio: uma cobrança/fatura só deve ser considerada se o aluno tiver ao menos um pagamento.
    # Se nunca pagou, seu financeiro deve ser desconsiderado até que ele pague uma.
    paid_customers_cid = set()
    paid_customers_email = set()
    for b in bills:
        if b.get('status') == 'paid':
            cid_p = b.get('customer', {}).get('id')
            cemail_p = (b.get('customer', {}).get('email') or '').strip().lower()
            if cid_p: paid_customers_cid.add(cid_p)
            if cemail_p: paid_customers_email.add(cemail_p)

    bills_by_sub_id = {}
    bills_by_cid = {}
    bills_by_email = {}
    
    total_recebido = 0.0
    total_faturas_pagas = 0
    recebido_mes_atual = 0.0
    total_em_atraso = 0.0
    qtd_em_atraso = 0
    historico_mensal_map = {}
    
    faturas_para_tabela_geral = []
    current_ym = now.strftime('%Y-%m')

    for b in bills:
        cid = b.get('customer', {}).get('id')
        cemail = (b.get('customer', {}).get('email') or '').strip().lower()
        # Regra: se o aluno nunca pagou nenhuma fatura, desconsidera totalmente seu financeiro
        if (cid not in paid_customers_cid) and (cemail not in paid_customers_email):
            continue
        cname = b.get('customer', {}).get('name') or 'Cliente'
        
        status = b.get('status', 'pending')
        amount_val = 0.0
        try: amount_val = float(b.get('amount', 0) or 0)
        except: pass

        due_iso = b.get('due_at')
        due_dt = _parse_iso(due_iso)
        due_fmt = _format_date(due_iso)

        charges = b.get('charges', [])
        c0 = charges[0] if charges else {}
        paid_iso = c0.get('paid_at')
        paid_dt = _parse_iso(paid_iso)
        paid_fmt = _format_date(paid_iso)

        pm_obj = c0.get('payment_method') or b.get('payment_method') or {}
        pm_name = pm_obj.get('public_name') or pm_obj.get('name') or pm_obj.get('type') or 'Outro'
        if 'cart' in pm_name.lower() or 'credit' in pm_name.lower():
            pm_tipo = 'Cartão de Crédito'
        elif 'boleto' in pm_name.lower():
            pm_tipo = 'Boleto'
        elif 'pix' in pm_name.lower():
            pm_tipo = 'Pix'
        else:
            pm_tipo = pm_name

        is_overdue = False
        days_overdue = 0
        if status == 'pending':
            if due_dt and due_dt < now:
                is_overdue = True
                days_overdue = max(1, (now - due_dt).days)
                status_label = f"Em Atraso ({days_overdue}d)"
                status_key = 'em_atraso'
            else:
                status_label = "A Vencer"
                status_key = 'a_vencer'
        elif status == 'paid':
            status_label = "Pago"
            status_key = 'pago'
        elif status == 'canceled':
            status_label = "Cancelado"
            status_key = 'cancelado'
        else:
            status_label = status.capitalize()
            status_key = status

        url = b.get('url') or (c0.get('print_url') if c0 else None) or f"https://app.vindi.com.br/customer/bills/{b.get('id')}"
        sub_obj = b.get('subscription') or {}
        sub_id_bill = sub_obj.get('id')
        plan_name_bill = sub_obj.get('plan', {}).get('name') or ""

        fatura_item = {
            "id": b.get('id'),
            "status": status_key,
            "status_label": status_label,
            "valor": amount_val,
            "valor_fmt": f"R$ {amount_val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "vencimento": due_fmt,
            "vencimento_iso": due_iso or "",
            "data_pagamento": paid_fmt,
            "data_pagamento_iso": paid_iso or "",
            "forma_pagamento": pm_tipo,
            "url": url,
            "dias_atraso": days_overdue,
            "aluno": cname,
            "email": cemail,
            "subscription_id": sub_id_bill,
            "plano": plan_name_bill
        }

        if sub_id_bill:
            bills_by_sub_id.setdefault(sub_id_bill, []).append(fatura_item)
        if cid:
            bills_by_cid.setdefault(cid, []).append(fatura_item)
        if cemail:
            bills_by_email.setdefault(cemail, []).append(fatura_item)

        if status == 'paid':
            total_recebido += amount_val
            total_faturas_pagas += 1
            ref_dt = paid_dt or due_dt or _parse_iso(b.get('created_at'))
            if ref_dt:
                ym = ref_dt.strftime('%Y-%m')
                if ym not in historico_mensal_map:
                    historico_mensal_map[ym] = {'pago': 0.0, 'qtd': 0}
                historico_mensal_map[ym]['pago'] += amount_val
                historico_mensal_map[ym]['qtd'] += 1
                if ym == current_ym:
                    recebido_mes_atual += amount_val
        elif is_overdue:
            total_em_atraso += amount_val
            qtd_em_atraso += 1

        faturas_para_tabela_geral.append(fatura_item)

    faturas_para_tabela_geral.sort(key=lambda x: x.get('data_pagamento_iso') or x.get('vencimento_iso') or '', reverse=True)

    students_vindi = {}
    subscriptions_list = []
    mrr_ativo_total = 0.0
    projecao_mensal_map = {}

    import unicodedata
    def _norm_course(name):
        if not name: return ''
        n = str(name).strip().upper()
        n = ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
        if 'ORTOPED' in n or 'PARTES MOLES' in n: return 'PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES'
        if 'CCIH' in n or 'PREVENCAO' in n or 'HOSPITALAR' in n:
            if 'FARM' in n: return 'PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH) - FARMÁCIA'
            if 'ENF' in n: return 'PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH) - ENFERMAGEM'
            return 'PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)'
        if 'IMUNO' in n: return 'PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS'
        if 'PED' in n or 'INFECTOPED' in n: return 'PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA'
        if 'SOS' in n or 'ANTIBIOTICO' in n or 'ATB' in n: return 'S.O.S ANTIBIÓTICO'
        if 'FERRAMENTA' in n or 'QUALIDADE' in n: return 'FERRAMENTAS DE QUALIDADE'
        return n

    for sub in subs:
        c = sub.get('customer', {})
        email = (c.get('email') or '').strip().lower()
        cid = c.get('id')
        sub_id = sub.get('id')
        if not email:
            continue
        if (cid not in paid_customers_cid) and (email not in paid_customers_email):
            continue

        price = 0.0
        for it in sub.get('product_items', []):
            ps = it.get('pricing_schema', {})
            if ps.get('price'):
                try: price += float(ps['price'])
                except: pass
        if price == 0 and sub.get('plan'):
            for it in sub.get('plan', {}).get('plan_items', []):
                ps = it.get('pricing_schema', {})
                if ps.get('price'):
                    try: price += float(ps['price'])
                    except: pass

        sub_status = sub.get('status', 'active')
        next_b_iso = sub.get('next_billing_at')
        next_b_dt = _parse_iso(next_b_iso)
        next_b_fmt = _format_date(next_b_iso)
        overdue_since = sub.get('overdue_since')
        plan_name = sub.get('plan', {}).get('name') or 'Assinatura Pós-Graduação'
        course_name = _norm_course(plan_name)

        # Matched bills ONLY for this subscription
        aluno_bills = []
        if sub_id and sub_id in bills_by_sub_id:
            aluno_bills = list(bills_by_sub_id[sub_id])
        elif cid and cid in bills_by_cid:
            for b in bills_by_cid[cid]:
                if b.get('plano') == plan_name or not b.get('subscription_id'):
                    aluno_bills.append(b)
        elif email in bills_by_email:
            for b in bills_by_email[email]:
                if b.get('plano') == plan_name or not b.get('subscription_id'):
                    aluno_bills.append(b)

        seen_ids = set()
        unique_bills = []
        for b in aluno_bills:
            if b['id'] not in seen_ids:
                seen_ids.add(b['id'])
                unique_bills.append(b)

        student_overdue_bills = [b for b in unique_bills if b['status'] == 'em_atraso']
        valor_atraso = sum(b['valor'] for b in student_overdue_bills)
        dias_atraso = max([b['dias_atraso'] for b in student_overdue_bills], default=0)

        if sub_status == 'canceled':
            st_fin = 'cancelado'
            st_lbl = 'Cancelado'
            st_color = 'var(--muted)'
            st_bg = 'rgba(0,0,0,0.06)'
        elif student_overdue_bills or overdue_since:
            st_fin = 'em_atraso'
            st_lbl = f'Atraso ({dias_atraso}d)' if dias_atraso > 0 else 'Em Atraso'
            st_color = '#e11d48'
            st_bg = 'rgba(225,29,72,0.1)'
        elif sub_status == 'active':
            st_fin = 'adimplente'
            st_lbl = 'Em Dia'
            st_color = '#059669'
            st_bg = 'rgba(16,185,129,0.1)'
            mrr_ativo_total += price
            
            if next_b_dt:
                base_dt = next_b_dt if next_b_dt > now else (now + timedelta(days=5))
                for m_offset in range(6):
                    proj_dt = base_dt + timedelta(days=30 * m_offset)
                    ym = proj_dt.strftime('%Y-%m')
                    projecao_mensal_map[ym] = projecao_mensal_map.get(ym, 0.0) + price
                    
                    if m_offset > 0 or not any(b['status'] == 'a_vencer' for b in unique_bills):
                        proj_fmt = proj_dt.strftime('%d/%m/%Y')
                        unique_bills.append({
                            "id": f"proj-{sub_id}-{m_offset}",
                            "status": "futuro",
                            "status_label": "Futuro (Agendado)",
                            "valor": price,
                            "valor_fmt": f"R$ {price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                            "vencimento": proj_fmt,
                            "vencimento_iso": proj_dt.isoformat(),
                            "data_pagamento": "",
                            "data_pagamento_iso": "",
                            "forma_pagamento": sub.get('payment_method', {}).get('public_name') or 'Recorrência',
                            "url": f"https://app.vindi.com.br/admin/subscriptions/{sub_id}",
                            "dias_atraso": 0,
                            "aluno": c.get('name'),
                            "email": email,
                            "subscription_id": sub_id,
                            "plano": plan_name
                        })
        elif sub_status in ['expired', 'inactive']:
            st_fin = 'quitado'
            st_lbl = 'Quitado'
            st_color = '#64748b'
            st_bg = 'rgba(100,116,139,0.1)'
        else:
            st_fin = sub_status
            st_lbl = sub_status.capitalize()
            st_color = 'var(--muted)'
            st_bg = 'rgba(0,0,0,0.05)'

        sub_pm = sub.get('payment_method', {}).get('public_name') or sub.get('payment_method', {}).get('name') or 'Outro'
        unique_bills.sort(key=lambda x: x.get('vencimento_iso') or x.get('data_pagamento_iso') or '', reverse=True)

        sub_data = {
            "has_vindi": True,
            "customer_id": cid,
            "customer_name": c.get('name') or '',
            "customer_email": email,
            "subscription_id": sub_id,
            "plano": plan_name,
            "curso": course_name,
            "status_assinatura": sub_status,
            "status_financeiro": st_fin,
            "status_label": st_lbl,
            "status_color": st_color,
            "status_bg": st_bg,
            "forma_pagamento": sub_pm,
            "valor_parcela": price,
            "proximo_vencimento": next_b_fmt,
            "dias_atraso": dias_atraso,
            "valor_atraso": valor_atraso,
            "faturas": unique_bills
        }

        subscriptions_list.append(sub_data)
        
        # Save by email (first or active preferred)
        if email not in students_vindi or sub_status == 'active':
            students_vindi[email] = sub_data
        # Also map by (email, course)
        students_vindi[f"{email}___{course_name}"] = sub_data

    sorted_ym = sorted(historico_mensal_map.keys())
    meses_pt = {'01':'Jan','02':'Fev','03':'Mar','04':'Abr','05':'Mai','06':'Jun','07':'Jul','08':'Ago','09':'Set','10':'Out','11':'Nov','12':'Dez'}
    historico_mensal = []
    for ym in sorted_ym[-14:]:
        y, m = ym.split('-')
        lbl = f"{meses_pt.get(m, m)}/{y[2:]}"
        historico_mensal.append({
            "mes": ym,
            "label": lbl,
            "pago": round(historico_mensal_map[ym]['pago'], 2),
            "qtd": historico_mensal_map[ym]['qtd']
        })

    sorted_proj_ym = sorted([ym for ym in projecao_mensal_map.keys() if ym >= current_ym])
    projecao_mensal = []
    for ym in sorted_proj_ym[:6]:
        y, m = ym.split('-')
        lbl = f"{meses_pt.get(m, m)}/{y[2:]}"
        projecao_mensal.append({
            "mes": ym,
            "label": lbl,
            "previsto": round(projecao_mensal_map[ym], 2)
        })

    financeiro_global = {
        "mrr_ativo": round(mrr_ativo_total, 2),
        "total_recebido": round(total_recebido, 2),
        "total_faturas_pagas": total_faturas_pagas,
        "recebido_mes_atual": round(recebido_mes_atual, 2),
        "total_em_atraso": round(total_em_atraso, 2),
        "qtd_em_atraso": qtd_em_atraso,
        "historico_mensal": historico_mensal,
        "projecao_mensal": projecao_mensal,
        "faturas_recentes": faturas_para_tabela_geral[:150]
    }

    cache_data = {
        "cached_at": datetime.now().isoformat(),
        "data": students_vindi,
        "subscriptions": subscriptions_list,
        "financeiro": financeiro_global
    }

    try:
        with open(CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"[VINDI] Cache atualizado com sucesso ({len(students_vindi)} alunos e financeiro global).")
    except Exception as e:
        print(f"[VINDI] Erro ao salvar cache: {e}")

    return cache_data"""

import re
code = re.sub(r'def get_vindi_data\(force_reload=False\):[\s\S]*?return cache_data', new_func.strip(), code, count=1)

with open(vindi_service_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated vindi_service.py successfully!")

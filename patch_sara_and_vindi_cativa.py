import os
import re

# ==============================================================================
# 1. Update vindi_service.py
# ==============================================================================
vindi_paths = [
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_service.py',
    r'C:\Users\DELL\Desktop\Acompanhamento de acessos\vindi_service.py'
]

vindi_patch_code = """
        # Matched bills for this subscription + customer's faturas avulsas
        aluno_bills = []
        if sub_id and sub_id in bills_by_sub_id:
            aluno_bills.extend(bills_by_sub_id[sub_id])
            
        # Also include customer's faturas avulsas (subscription is None)
        faturas_avulsas = []
        if cid and cid in bills_by_cid:
            for b in bills_by_cid[cid]:
                if not b.get('subscription_id'):
                    faturas_avulsas.append(b)
        elif email in bills_by_email:
            for b in bills_by_email[email]:
                if not b.get('subscription_id'):
                    faturas_avulsas.append(b)
                    
        for fa in faturas_avulsas:
            fa_copy = dict(fa)
            fa_copy['is_fatura_avulsa'] = True
            fa_copy['plano'] = f"Fatura Avulsa ({plan_name})"
            fa_copy['curso'] = course_name
            aluno_bills.append(fa_copy)

        seen_ids = set()
        unique_bills = []
        for b in aluno_bills:
            if b['id'] not in seen_ids:
                seen_ids.add(b['id'])
                unique_bills.append(b)

        # Check for paid fatura avulsa (renegociação / acordo)
        has_paid_renegociacao = any(b.get('is_fatura_avulsa') and b.get('status') == 'paid' for b in unique_bills)
        
        student_overdue_bills = [b for b in unique_bills if b['status'] == 'em_atraso' and not b.get('is_fatura_avulsa')]
        dias_atraso = max([b.get('dias_atraso', 0) for b in student_overdue_bills], default=0)
        valor_atraso = sum(b.get('valor', 0) for b in student_overdue_bills)

        paid_bills_count = sum(1 for b in unique_bills if b['status'] == 'paid')

        if student_overdue_bills and not has_paid_renegociacao:
            st_fin = 'em_atraso'
            st_lbl = 'Em Atraso'
            st_color = 'var(--rose-d)'
            st_bg = 'var(--rose-bg)'
        elif sub_status == 'active':
            st_fin = 'adimplente'
            st_lbl = 'Adimplente'
            st_color = 'var(--emerald-d)'
            st_bg = 'var(--emerald-bg)'
        elif sub_status in ['expired', 'inactive']:
            if has_paid_renegociacao or paid_bills_count > 0:
                st_fin = 'quitado'
                st_lbl = 'Quitado (Acordo/Renegociação)' if has_paid_renegociacao else 'Quitado'
                st_color = '#64748b'
                st_bg = 'rgba(100,116,139,0.1)'
            else:
                st_fin = 'inativo'
                st_lbl = 'Inativo'
                st_color = 'var(--muted)'
                st_bg = 'rgba(0,0,0,0.05)'
        elif sub_status == 'canceled':
            if has_paid_renegociacao or paid_bills_count > 0:
                st_fin = 'quitado' if has_paid_renegociacao else 'cancelado'
                st_lbl = 'Quitado (Renegociação)' if has_paid_renegociacao else 'Cancelado'
                st_color = '#64748b' if has_paid_renegociacao else 'var(--muted)'
                st_bg = 'rgba(100,116,139,0.1)' if has_paid_renegociacao else 'rgba(0,0,0,0.05)'
            else:
                st_fin = 'cancelado'
                st_lbl = 'Cancelado'
                st_color = 'var(--muted)'
                st_bg = 'rgba(0,0,0,0.05)'
        else:
            st_fin = sub_status
            st_lbl = sub_status.capitalize()
            st_color = 'var(--muted)'
            st_bg = 'rgba(0,0,0,0.05)'

        sub_pm = sub.get('payment_method', {}).get('public_name') or sub.get('payment_method', {}).get('name') or 'Outro'
        unique_bills.sort(key=lambda x: x.get('vencimento_iso') or x.get('data_pagamento_iso') or '', reverse=True)

        # Calculate a quality score for this subscription to select the best one
        sub_score = 0
        if sub_status == 'active': sub_score += 1000
        elif sub_status in ['expired', 'inactive']: sub_score += 500
        elif sub_status == 'canceled': sub_score += 100
        sub_score += (paid_bills_count * 50)
        if has_paid_renegociacao: sub_score += 300

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
            "dias_atraso": dias_atraso if not has_paid_renegociacao else 0,
            "valor_atraso": valor_atraso if not has_paid_renegociacao else 0.0,
            "has_renegociacao": has_paid_renegociacao,
            "faturas": unique_bills,
            "_score": sub_score
        }

        subscriptions_list.append(sub_data)
        
        # Save by email prioritizing higher score
        if email not in students_vindi or sub_score > students_vindi[email].get('_score', 0):
            students_vindi[email] = sub_data
            
        key_ec = f"{email}___{course_name}"
        if key_ec not in students_vindi or sub_score > students_vindi[key_ec].get('_score', 0):
            students_vindi[key_ec] = sub_data
"""

for vp in vindi_paths:
    if os.path.exists(vp):
        with open(vp, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the subscription matching block
        pattern = r'(\s+# Matched bills ONLY for this subscription.*?students_vindi\[f"\{email\}___\{course_name\}"\] = sub_data)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + '\n' + vindi_patch_code + content[match.end():]
            with open(vp, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched {vp}")
        else:
            print(f"Could not find regex match in {vp}")

# Remove cache to force fresh rebuild
cache_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json'
if os.path.exists(cache_file):
    os.remove(cache_file)
    print("Cleared vindi_cache.json")

print("vindi_service.py update completed.")

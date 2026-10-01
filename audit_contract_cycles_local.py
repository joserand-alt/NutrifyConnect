import os
import sys
import json
from datetime import datetime, date, timedelta
import calendar

dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"

# 1. Load bills from raw or cache
raw_bills_path = os.path.join(dash_dir, "all_vindi_bills_raw.json")
if not os.path.exists(raw_bills_path):
    raw_bills_path = r"C:\Users\DELL\Desktop\Acompanhamento de acessos\all_vindi_bills_raw.json"

with open(raw_bills_path, "r", encoding="utf-8") as f:
    bills = json.load(f)

# Count paid bills per subscription_id
paid_bills_by_sub = {}
for b in bills:
    sub_id = b.get("subscription_id")
    st = b.get("status")
    if sub_id and st in ["paid", "pago"]:
        paid_bills_by_sub[sub_id] = paid_bills_by_sub.get(sub_id, 0) + 1

# 2. Load Vindi Cache subscriptions
v_cache_path = os.path.join(dash_dir, "vindi_cache.json")
with open(v_cache_path, "r", encoding="utf-8") as f:
    vc = json.load(f)

# 3. Load Asaas Cache
a_cache_path = os.path.join(dash_dir, "asaas_cache.json")
with open(a_cache_path, "r", encoding="utf-8") as f:
    ac = json.load(f)

def normalize_course(c):
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

active_subs = []
for sub in vc.get("subscriptions", []):
    if sub.get("status_financeiro") == "adimplente":
        sub_id = sub.get("subscription_id")
        faturas = sub.get("faturas", [])
        paid_count = sum(1 for f in faturas if f.get("status") in ["paid", "pago"])
        if paid_count == 0 and sub_id in paid_bills_by_sub:
            paid_count = paid_bills_by_sub[sub_id]
        
        # Determine standard plan duration
        plan_name = sub.get("plano", "")
        # Orto, CCIH, Imuno, Ped are 18-month or 24-month post-graduations
        cycles = 18
        if "24" in plan_name:
            cycles = 24
        elif "12" in plan_name or "ANUAL" in plan_name.upper():
            cycles = 12
        elif "6" in plan_name or "SEMESTRAL" in plan_name.upper():
            cycles = 6
            
        remaining = max(0, cycles - paid_count)
        price = float(sub.get("valor_parcela") or 0.0)
        c_norm = normalize_course(sub.get("curso") or plan_name)
        
        active_subs.append({
            "sub_id": sub_id,
            "aluno": sub.get("customer_name"),
            "email": sub.get("customer_email"),
            "curso": c_norm,
            "price": price,
            "cycles": cycles,
            "paid_count": paid_count,
            "remaining_cycles": remaining,
            "proximo_vencimento": sub.get("proximo_vencimento")
        })

print(f"Total Active Vindi Subs Analisados: {len(active_subs)}")

# Add Asaas active contracts
email_to_course = {s["email"]: s["curso"] for s in active_subs}
asaas_faturas = ac.get("financeiro", {}).get("faturas_tabela", [])
# Group asaas pending faturas per student
asaas_pending_by_student = {}
today = date.today()

for f in asaas_faturas:
    st = f.get("status")
    if st in ["pendente", "pending", "a_vencer", "PENDING"]:
        em = (f.get("email") or "").strip().lower()
        val = float(f.get("valor") or 0.0)
        venc = f.get("vencimento_iso") or f.get("vencimento") or ""
        if em and venc:
            try:
                d_dt = datetime.strptime(venc[:10], "%Y-%m-%d").date() if "-" in venc else datetime.strptime(venc[:10], "%d/%m/%Y").date()
                if d_dt >= today:
                    asaas_pending_by_student.setdefault(em, []).append({
                        "valor": val,
                        "venc": d_dt,
                        "aluno": f.get("aluno")
                    })
            except:
                pass

# Group by course and simulate exact contract runoff
courses_list = sorted(list(set([s["curso"] for s in active_subs] + ["POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES"])))

print("\n" + "="*110)
print(f"{'CURSO':<42} | {'MRR ATIVO':<12} | {'PROJ 1M':<10} | {'PROJ 3M (REAL)':<15} | {'PROJ 6M (REAL)':<15} | {'PROJ 12M (REAL)':<15}")
print("="*110)

tot_mrr = 0.0
tot_p1m = 0.0
tot_p3m = 0.0
tot_p6m = 0.0
tot_p12m = 0.0

for c in courses_list:
    c_subs = [s for s in active_subs if s["curso"] == c]
    mrr_c = sum(s["price"] for s in c_subs)
    
    # Simulate months 1 to 12
    monthly_rev = [0.0] * 12
    for s in c_subs:
        pr = s["price"]
        rem = s["remaining_cycles"]
        for m in range(12):
            if m < rem:
                monthly_rev[m] += pr
                
    # Add Asaas for this course
    for em, pending_list in asaas_pending_by_student.items():
        c_em = email_to_course.get(em) or "PLATAFORMA GERAL"
        if c_em == c:
            for pf in pending_list:
                # calculate month offset
                diff_days = (pf["venc"] - today).days
                m_idx = min(11, max(0, diff_days // 30))
                monthly_rev[m_idx] += pf["valor"]

    p1m = monthly_rev[0]
    p3m = sum(monthly_rev[:3])
    p6m = sum(monthly_rev[:6])
    p12m = sum(monthly_rev[:12])
    
    tot_mrr += mrr_c
    tot_p1m += p1m
    tot_p3m += p3m
    tot_p6m += p6m
    tot_p12m += p12m
    
    p3m_flat = mrr_c * 3
    p6m_flat = mrr_c * 6
    p12m_flat = mrr_c * 12
    
    print(f"{c[:42]:<42} | R$ {mrr_c:>9,.2f} | R$ {p1m:>7,.2f} | R$ {p3m:>8,.2f} ({p3m/p3m_flat*100:>4.0f}%) | R$ {p6m:>8,.2f} ({p6m/p6m_flat*100:>4.0f}%) | R$ {p12m:>8,.2f} ({p12m/p12m_flat*100:>4.0f}%)" if p3m_flat > 0 else f"{c[:42]:<42} | R$ {mrr_c:>9,.2f} | R$ {p1m:>7,.2f} | R$ {p3m:>8,.2f} | R$ {p6m:>8,.2f} | R$ {p12m:>8,.2f}")

print("="*110)
print(f"{'TOTAL CONSOLIDADO CARTEIRA':<42} | R$ {tot_mrr:>9,.2f} | R$ {tot_p1m:>7,.2f} | R$ {tot_p3m:>8,.2f} ({(tot_p3m/(tot_mrr*3))*100:>4.0f}%) | R$ {tot_p6m:>8,.2f} ({(tot_p6m/(tot_mrr*6))*100:>4.0f}%) | R$ {tot_p12m:>8,.2f} ({(tot_p12m/(tot_mrr*12))*100:>4.0f}%)")

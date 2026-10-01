import sys
import json
from datetime import datetime, date, timedelta
import calendar

sys.path.insert(0, r"C:\Users\DELL\Desktop\Dash_InfectoCast")
import vindi_service
import asaas_service

subs = vindi_service.fetch_all_vindi_subscriptions()
bills = vindi_service.fetch_all_vindi_bills()

# Count paid bills per subscription_id
paid_bills_by_sub = {}
for b in bills:
    sub_id = b.get("subscription_id")
    st = b.get("status")
    if sub_id and st in ["paid", "pago"]:
        paid_bills_by_sub[sub_id] = paid_bills_by_sub.get(sub_id, 0) + 1

active_subs = []
for sub in subs:
    st = sub.get("status")
    if st == "active":
        sub_id = sub.get("id")
        cycles = sub.get("billing_cycles")
        if not cycles or cycles <= 0:
            cycles = 18  # default standard pos
        paid_count = paid_bills_by_sub.get(sub_id, 0)
        remaining = max(0, cycles - paid_count)
        plan_name = sub.get("plan", {}).get("name") or ""
        price = 0.0
        for it in sub.get("product_items", []):
            try:
                price += float(it.get("pricing_schema", {}).get("price") or 0)
            except:
                pass
        if price == 0 and sub.get("plan"):
            for it in sub.get("plan", {}).get("plan_items", []):
                try:
                    price += float(it.get("pricing_schema", {}).get("price") or 0)
                except:
                    pass

        active_subs.append({
            "sub_id": sub_id,
            "plan": plan_name,
            "curso": vindi_service.normalize_vindi_course(plan_name),
            "price": price,
            "cycles": cycles,
            "paid_count": paid_count,
            "remaining_cycles": remaining
        })

print(f"Total active Vindi subscriptions: {len(active_subs)}")

by_course = {}
for s in active_subs:
    c = s["curso"]
    if c not in by_course:
        by_course[c] = {"count": 0, "mrr": 0.0, "rem_dist": {}}
    by_course[c]["count"] += 1
    by_course[c]["mrr"] += s["price"]
    rem = s["remaining_cycles"]
    by_course[c]["rem_dist"][rem] = by_course[c]["rem_dist"].get(rem, 0) + 1

for c, d in sorted(by_course.items(), key=lambda x: x[1]["mrr"], reverse=True):
    cnt = d["count"]
    m = d["mrr"]
    print(f"\n--- {c} ({cnt} subs | MRR: R$ {m:,.2f}) ---")
    for rem in sorted(d["rem_dist"].keys()):
        num = d["rem_dist"][rem]
        print(f"    {rem} parcelas restantes: {num} alunos")

# Now calculate exact contract projections month by month (1m to 12m)
# For each future month m (1 to 12):
# revenue(m) = sum(s['price'] for s in active_subs if s['remaining_cycles'] >= m)
print("\n" + "="*80)
print("PROJEÇÕES REAIS CONSIDERANDO TEMPO RESTANTE DE CONTRATO (RUNOFF / ENCERRAMENTOS):")
print("="*80)

# Calculate for each course
for c, d in sorted(by_course.items(), key=lambda x: x[1]["mrr"], reverse=True):
    course_subs = [s for s in active_subs if s["curso"] == c]
    mrr_base = d["mrr"]
    
    # Month by month revenues
    monthly_rev = []
    for m in range(1, 13):
        m_rev = sum(s["price"] for s in course_subs if s["remaining_cycles"] >= m)
        monthly_rev.append(m_rev)
    
    p1m = monthly_rev[0]
    p3m = sum(monthly_rev[:3])
    p6m = sum(monthly_rev[:6])
    p12m = sum(monthly_rev[:12])
    
    # Comparison vs flat replication (MRR * n)
    p3m_flat = mrr_base * 3
    p6m_flat = mrr_base * 6
    p12m_flat = mrr_base * 12
    
    print(f"\nCurso: {c}")
    print(f"  MRR Base: R$ {mrr_base:,.2f}")
    print(f"  Mensalidades M1..M6: {[round(r, 2) for r in monthly_rev[:6]]}")
    print(f"  Proj 1M (30d real): R$ {p1m:,.2f}")
    print(f"  Proj 3M Contratual: R$ {p3m:,.2f} (vs R$ {p3m_flat:,.2f} linear -> redução de {((1 - p3m/p3m_flat)*100):.1f}%)" if p3m_flat > 0 else "")
    print(f"  Proj 6M Contratual: R$ {p6m:,.2f} (vs R$ {p6m_flat:,.2f} linear -> redução de {((1 - p6m/p6m_flat)*100):.1f}%)" if p6m_flat > 0 else "")
    print(f"  Proj 12M Contratual: R$ {p12m:,.2f} (vs R$ {p12m_flat:,.2f} linear -> redução de {((1 - p12m/p12m_flat)*100):.1f}%)" if p12m_flat > 0 else "")

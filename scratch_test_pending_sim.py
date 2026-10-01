import sys
sys.path.insert(0, r"c:\Users\DELL\Desktop\Dash_InfectoCast")
import asaas_service, cativa_api, json
from datetime import datetime

# Test Asaas enrichment and pending student inclusion
payments = asaas_service.fetch_all_payments()
customers = asaas_service.fetch_all_customers()
asaas_service._enrich_customers_with_academy_api(customers)

cust_by_id = {c['id']: c for c in customers}

print(f"Total customers: {len(customers)}, Total payments: {len(payments)}")

# Check all customers with pending faturas
pending_custs = []
for cid, cust in cust_by_id.items():
    c_payments = [p for p in payments if p.get('customer') == cid]
    paid_p = [p for p in c_payments if p.get('status') in ('RECEIVED', 'CONFIRMED')]
    pending_p = [p for p in c_payments if p.get('status') in ('PENDING', 'OVERDUE')]
    
    # Sort pending payments by dateCreated or dueDate
    pending_p.sort(key=lambda x: str(x.get('dateCreated') or x.get('dueDate') or ''), reverse=True)
    
    if not paid_p and pending_p:
        pending_custs.append({
            'name': cust.get('name'),
            'email': (cust.get('email') or '').lower().strip(),
            'most_recent_charge': pending_p[0],
            'all_charges': pending_p
        })

print(f"\nFound {len(pending_custs)} customers who are pending (no paid charges):")
for pc in pending_custs:
    mrc = pc['most_recent_charge']
    print(f"  {pc['name']} ({pc['email']}) -> Recent charge: {mrc.get('dateCreated')} | Due: {mrc.get('dueDate')} | Status: {mrc.get('status')} | R$ {mrc.get('value')} | {mrc.get('description')}")

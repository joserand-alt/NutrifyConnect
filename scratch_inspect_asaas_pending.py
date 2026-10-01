import sys, os
sys.path.insert(0, r"c:\Users\DELL\Desktop\Dash_InfectoCast")
import asaas_service, json, re
from datetime import datetime

# Fetch live payments and customers from Asaas
payments = asaas_service.fetch_all_payments()
customers = asaas_service.fetch_all_customers()
asaas_service._enrich_customers_with_academy_api(customers)

cust_by_id = {c['id']: c for c in customers}

print(f"Total customers: {len(customers)}, Total payments: {len(payments)}")

now = datetime.now()
print(f"Now is: {now}")

pending_list = []
for p in payments:
    st = p.get('status')
    due = p.get('dueDate') or p.get('originalDueDate') or ''
    dt_created = p.get('dateCreated') or ''
    cid = p.get('customer')
    cust = cust_by_id.get(cid, {})
    email = (cust.get('email') or '').strip().lower()
    name = (cust.get('name') or '').strip()
    val = p.get('value') or 0
    desc = p.get('description') or ''
    
    if st in ['PENDING', 'OVERDUE']:
        pending_list.append({
            'id': p.get('id'),
            'cid': cid,
            'name': name,
            'email': email,
            'status': st,
            'value': val,
            'due': due,
            'created': dt_created,
            'desc': desc
        })

print(f"Total PENDING / OVERDUE payments: {len(pending_list)}")
# Sort by created or due
pending_list.sort(key=lambda x: str(x['created'] or x['due']), reverse=True)

print("\nTop 30 most recent PENDING / OVERDUE payments in Asaas:")
for p in pending_list[:30]:
    print(f"  Created: {p['created']} | Due: {p['due']} | Status: {p['status']} | {p['name']} ({p['email']}) | R$ {p['value']} | {p['desc']}")

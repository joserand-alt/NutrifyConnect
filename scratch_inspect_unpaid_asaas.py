import sys
sys.path.insert(0, r"c:\Users\DELL\Desktop\Dash_InfectoCast")
import asaas_service, json

payments = asaas_service.fetch_all_payments()
customers = asaas_service.fetch_all_customers()
asaas_service._enrich_customers_with_academy_api(customers)

cust_by_id = {c['id']: c for c in customers}

# Let's inspect customers who have NO paid payments (total_pago == 0)
unpaid_customers = []
for cid, cust in cust_by_id.items():
    cust_payments = [p for p in payments if p.get('customer') == cid]
    paid_p = [p for p in cust_payments if p.get('status') in ('RECEIVED', 'CONFIRMED')]
    pending_p = [p for p in cust_payments if p.get('status') in ('PENDING', 'OVERDUE')]
    
    if not paid_p and pending_p:
        unpaid_customers.append({
            'cid': cid,
            'name': cust.get('name'),
            'email': cust.get('email'),
            'ext': cust.get('externalReference'),
            'pending_count': len(pending_p),
            'payments': pending_p
        })

print(f"Total unpaid customers with pending charges: {len(unpaid_customers)}")
for uc in unpaid_customers:
    print(f"\nCustomer: {uc['name']} ({uc['email']}) | Ext: {uc['ext']}")
    for p in uc['payments']:
        print(f"   Created: {p.get('dateCreated')} | Due: {p.get('dueDate')} | Status: {p.get('status')} | R$ {p.get('value')} | {p.get('description')}")

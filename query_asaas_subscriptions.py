"""
Query Asaas API directly to find subscription/product info for PG students.
Asaas has: /v3/subscriptions?customer={customerId}
Each subscription has a 'description' field which usually contains the product name.
"""
import json, os, urllib.request

def _load_key():
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asaas_config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8-sig") as f:
            return json.load(f).get("api_key", "")
    return ""

API_KEY = os.environ.get("ASAAS_API_KEY") or _load_key()
BASE_URL = "https://api.asaas.com/v3/"

def api_get(endpoint):
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", headers={
        "access_token": API_KEY, "Content-Type": "application/json", "User-Agent": "InfectoCast-Dashboard/2.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

# Load PG student customer IDs from asaas_cache
with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

pg_emails = [
    'danielesarto@yahoo.com.br', 'beatriz.grinsztejn@gmail.com',
    'markus_braga@hotmail.com', 'laura_orlandi@hotmail.com',
    'mclaramdp@gmail.com',
]

print("=== Querying Asaas API for subscriptions & payment details ===\n")

for email in pg_emails:
    data = asaas.get('data', {}).get(email)
    if not data:
        print(f"[{email}] NÃO no cache\n")
        continue
    
    cid = data.get('customer_id', '')
    print(f"[{email}] customer_id={cid}")
    
    # 1. Try subscriptions endpoint
    subs = api_get(f"subscriptions?customer={cid}")
    if subs and subs.get('data'):
        for s in subs['data']:
            print(f"  SUBSCRIPTION: id={s.get('id')}")
            print(f"    description: {s.get('description')}")
            print(f"    value: {s.get('value')}")
            print(f"    status: {s.get('status')}")
            print(f"    externalReference: {s.get('externalReference')}")
            print(f"    billingType: {s.get('billingType')}")
    else:
        print("  No subscriptions found")
    
    # 2. Try first payment details
    fats = data.get('faturas', [])
    if fats:
        pay_id = fats[0].get('id', '')
        pay_detail = api_get(f"payments/{pay_id}")
        if pay_detail:
            print(f"  PAYMENT DETAIL ({pay_id}):")
            print(f"    description: {pay_detail.get('description')}")
            print(f"    externalReference: {pay_detail.get('externalReference')}")
            print(f"    installment: {pay_detail.get('installment')}")
            # Check if installment has description
            inst_id = pay_detail.get('installment')
            if inst_id:
                inst_detail = api_get(f"installments/{inst_id}")
                if inst_detail:
                    print(f"  INSTALLMENT ({inst_id}):")
                    print(f"    description: {inst_detail.get('description')}")
                    print(f"    externalReference: {inst_detail.get('externalReference')}")
                    print(f"    paymentExternalReference: {inst_detail.get('paymentExternalReference')}")
    
    print()

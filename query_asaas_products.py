"""
Query Asaas API: try paymentLinks and check if there's product/course info
Also check the Academy course catalog prices for matching
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
        return {"error": str(e)}

# Check what Asaas knows about these external references
ext_refs = ['100070', '100105', '100078', '100084', '100079']

print("=== Checking Asaas payments by externalReference ===\n")
for ref in ext_refs[:3]:
    result = api_get(f"payments?externalReference={ref}")
    if 'error' not in result and result.get('data'):
        for p in result['data'][:2]:
            print(f"  ExtRef {ref}: id={p.get('id')}")
            print(f"    description: {p.get('description')}")
            print(f"    subscription: {p.get('subscription')}")
            print(f"    installment: {p.get('installment')}")
            print(f"    paymentLink: {p.get('paymentLink')}")
            print(f"    externalReference: {p.get('externalReference')}")
            print(f"    value: {p.get('value')}")
            break
    print()

# Try the paymentLinks endpoint
print("\n=== Checking Asaas payment links ===")
result = api_get("paymentLinks?limit=10")
if 'error' not in result:
    links = result.get('data', [])
    print(f"  Found {len(links)} payment links")
    for l in links[:5]:
        print(f"  Link: {l.get('name')} | value={l.get('value')} | id={l.get('id')}")
        print(f"    description: {l.get('description')}")

# KEY APPROACH: Check the Academy API /api/turmas/{id}/alunos or /api/matriculas
print("\n\n=== Academy API: check products endpoint ===")
ACADEMY_TOKEN = "idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ"

def academy_get(endpoint):
    url = f"https://academy.infectocast.com.br/api/{endpoint}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {ACADEMY_TOKEN}",
        "Accept": "application/json", "User-Agent": "Mozilla/5.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

# Try /api/matriculas 
for endpoint in ['matriculas', 'turmas', 'produtos', 'orders', 'pedidos']:
    r = academy_get(endpoint)
    if 'error' not in r:
        print(f"  /api/{endpoint}: OK - keys={list(r.keys()) if isinstance(r, dict) else type(r)}")
        if isinstance(r, dict) and r.get('data'):
            d = r['data']
            if isinstance(d, list) and len(d) > 0:
                print(f"    First item keys: {list(d[0].keys()) if isinstance(d[0], dict) else d[0]}")
    else:
        print(f"  /api/{endpoint}: {r['error'][:60]}")

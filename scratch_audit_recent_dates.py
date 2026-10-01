import json, os, datetime

base_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"

# 1. Inspect cativa_cache.json
cativa_path = os.path.join(base_dir, "cativa_cache.json")
with open(cativa_path, "r", encoding="utf-8") as f:
    cativa = json.load(f)

print("=== CATIVA DIGITAL STUDENTS WITH RECENT DATES ===")
students_cativa = cativa.get("students", [])
print(f"Total students in Cativa cache: {len(students_cativa)}")
for s in students_cativa:
    created = s.get("createdAt") or s.get("created_at") or s.get("creationDate")
    courses = s.get("courses", [])
    em = s.get("email")
    nm = s.get("fullName") or s.get("name")
    
    # Check if student or course has recent dates
    dates = [created] + [c.get("enrollmentDate") or c.get("createdAt") for c in courses]
    dates = [d for d in dates if d]
    
    recent = any(str(d).startswith("2026-09-22") or str(d).startswith("2026-09-23") or str(d).startswith("2026-09-24") or "22/09/2026" in str(d) or "23/09/2026" in str(d) or "24/09/2026" in str(d) for d in dates)
    if recent:
        print(f" -> {em} | {nm} | created: {created} | courses: {[(c.get('courseName'), c.get('enrollmentDate')) for c in courses]}")

# 2. Inspect asaas_cache.json for pending payments or customers created recently
asaas_path = os.path.join(base_dir, "asaas_cache.json")
with open(asaas_path, "r", encoding="utf-8") as f:
    asaas = json.load(f)

print("\n=== ASAAS CUSTOMERS / PAYMENTS WITH RECENT DATES ===")
asaas_data = asaas.get("data", {})
for k, st in asaas_data.items():
    fats = st.get("faturas", [])
    for ft in fats:
        dt = ft.get("data_pagamento") or ft.get("vencimento") or ft.get("data_criacao") or ft.get("dueDate")
        if any(x in str(dt) for x in ["2026-09-22", "2026-09-23", "2026-09-24", "22/09/2026", "23/09/2026", "24/09/2026"]):
            print(f" -> Asaas: {st.get('customer_email')} | {st.get('customer_name')} | status: {ft.get('status')} | val: {ft.get('valor')} | date: {dt} | desc: {ft.get('descricao')}")

# 3. Inspect RD Conversas / RD Leads
rd_conv_path = os.path.join(base_dir, "rd_conversas_cache.json")
if os.path.exists(rd_conv_path):
    with open(rd_conv_path, "r", encoding="utf-8") as f:
        rd_c = json.load(f)
    print(f"\nRD Conversas contacts count: {len(rd_c.get('contatos', []))}")
    for c in rd_c.get("contatos", [])[:15]:
        print(f" -> RD: {c.get('nome')} | {c.get('telefone')} | {c.get('ultima_mensagem_data')}")

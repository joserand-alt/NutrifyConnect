import os
import re

asaas_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py'
gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'

# 1. Update asaas_service.py
with open(asaas_path, 'r', encoding='utf-8') as f:
    as_code = f.read()

# Add ThreadPoolExecutor import if not present
if 'from concurrent.futures import ThreadPoolExecutor' not in as_code:
    as_code = as_code.replace('from datetime import datetime, timedelta', 'from datetime import datetime, timedelta\nfrom concurrent.futures import ThreadPoolExecutor')

# In _process(customers, payments), add Academy API enrichment before loop
old_process_start = """def _process(customers, payments):
    now = datetime.now(); current_ym = now.strftime("%Y-%m")
    cust_by_id = {c["id"]: c for c in customers}"""

new_process_start = """def _enrich_customers_with_academy_api(customers):
    print("[ASAAS] Enriquecendo customers via API da Academy (/api/alunos/{id})...")
    ACADEMY_TOKEN = "idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ"
    enriched = 0
    def fetch_acad(c):
        nonlocal enriched
        ext = (c.get("externalReference") or "").strip()
        if not ext: return
        url = f"https://academy.infectocast.com.br/api/alunos/{ext}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {ACADEMY_TOKEN}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                d = json.loads(resp.read().decode("utf-8"))
                if d.get("success") and d.get("data"):
                    st = d["data"]
                    if st.get("email"):
                        c["email"] = st["email"].strip()
                    if st.get("nome"):
                        c["name"] = st["nome"].strip()
                    enriched += 1
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(fetch_acad, customers))
    print(f"[ASAAS] {enriched} customers enriquecidos com email/nome direto da API Academy!")

def _process(customers, payments):
    now = datetime.now(); current_ym = now.strftime("%Y-%m")
    _enrich_customers_with_academy_api(customers)
    cust_by_id = {c["id"]: c for c in customers}"""

if old_process_start in as_code:
    as_code = as_code.replace(old_process_start, new_process_start)
    print("Enrichment added to asaas_service.py")
else:
    print("Could not find old_process_start directly")

# In students_asaas dictionary building, also index by email
old_students_build = """        students_asaas[ext] = {
            "has_asaas": True, "customer_id": cid, "customer_name": cust.get("name",""),
            "customer_email": cust.get("email",""), "cpfcnpj": cust.get("cpfCnpj",""),
            "aluno_id_extref": ext, "status_financeiro": st_fin, "status_assinatura": st_fin,
            "status_label": st_lbl, "status_color": st_clr, "status_bg": st_bg,
            "dias_atraso": dias_at, "valor_atraso": val_at,
            "total_pago": round(sum(f["valor"] for f in faturas if f["status"]=="pago"),2),
            "faturas": sorted(faturas, key=lambda x: x.get("vencimento_iso") or "", reverse=True),
        }"""

new_students_build = """        st_obj = {
            "has_asaas": True, "customer_id": cid, "customer_name": cust.get("name",""),
            "customer_email": cust.get("email",""), "cpfcnpj": cust.get("cpfCnpj",""),
            "aluno_id_extref": ext, "status_financeiro": st_fin, "status_assinatura": st_fin,
            "status_label": st_lbl, "status_color": st_clr, "status_bg": st_bg,
            "dias_atraso": dias_at, "valor_atraso": val_at,
            "total_pago": round(sum(f["valor"] for f in faturas if f["status"]=="pago"),2),
            "faturas": sorted(faturas, key=lambda x: x.get("vencimento_iso") or "", reverse=True),
        }
        students_asaas[ext] = st_obj
        c_mail = (cust.get("email") or "").lower().strip()
        if c_mail:
            students_asaas[c_mail] = st_obj"""

if old_students_build in as_code:
    as_code = as_code.replace(old_students_build, new_students_build)
    print("Email indexing added to asaas_service.py")

with open(asaas_path, 'w', encoding='utf-8') as f:
    f.write(as_code)
print("Saved asaas_service.py")

# 2. Update gerador.py
with open(gerador_path, 'r', encoding='utf-8') as f:
    g_code = f.read()

# Update Asaas integration block in gerador.py to match by email and add missing API students
p_asaas_gerador = re.compile(
    r"# ============================================\s*"
    r"# ASAAS FINANCEIRO.*?# ============================================\s*"
    r"asaas_matched = 0[\s\S]*?print\(f\"\[ASAAS\] \{asaas_matched\} estudantes vinculados com dados financeiros do Asaas\.\"\)"
)

new_asaas_gerador = """    # ============================================
    # ASAAS FINANCEIRO — 100% via API (Asaas + Academy API)
    # ============================================
    asaas_matched = 0
    asaas_financeiro = {}
    try:
        from asaas_service import get_asaas_data
        asaas_res = get_asaas_data(force_reload=False)
        asaas_map = asaas_res.get('data', {}) if isinstance(asaas_res, dict) else {}
        asaas_financeiro = asaas_res.get('financeiro', {}) if isinstance(asaas_res, dict) else {}

        # 1. Vincular aos estudantes existentes por e-mail (resolvido pela API) ou ID
        for s in students:
            em = str(s.get('email', '')).lower().strip()
            aluno_id = str(s.get('id_aluno', '')).strip()
            matched = False
            if em and em in asaas_map:
                s['asaas'] = asaas_map[em]
                asaas_matched += 1
                matched = True
            elif aluno_id and aluno_id in asaas_map:
                s['asaas'] = asaas_map[aluno_id]
                asaas_matched += 1
                matched = True
            if not matched:
                s['asaas'] = None

        # 2. Adicionar alunos do Asaas/Academy API que ainda não estavam na lista de estudantes
        existing_emails = set(str(s.get('email', '')).lower().strip() for s in students if s.get('email'))
        added_from_api = 0
        for key, asaas_st in asaas_map.items():
            if not isinstance(asaas_st, dict): continue
            st_email = (asaas_st.get('customer_email') or '').lower().strip()
            if st_email and st_email not in existing_emails:
                existing_emails.add(st_email)
                students.append({
                    "email": st_email,
                    "nome": asaas_st.get('customer_name') or 'Aluno Academy',
                    "curso": "PLATAFORMA GERAL",
                    "telefone": "",
                    "acessou": False,
                    "data_insc": None,
                    "data_inscricao": None,
                    "inscricao": None,
                    "dias_desde_insc": 0,
                    "plataforma": "Academy",
                    "id_aluno": str(asaas_st.get('aluno_id_extref', '')),
                    "events": [],
                    "vindi": None,
                    "asaas": asaas_st
                })
                added_from_api += 1
                asaas_matched += 1

        print(f"[ASAAS] {asaas_matched} estudantes vinculados 100% via API ({added_from_api} matriculados adicionados da API Academy).")"""

g_code, n_g = p_asaas_gerador.subn(new_asaas_gerador, g_code)
print(f"gerador.py Asaas block updated: {n_g}")

with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(g_code)
print("Saved gerador.py")

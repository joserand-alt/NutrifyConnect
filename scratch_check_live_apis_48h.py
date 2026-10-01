import os, json, datetime
from datetime import timedelta

now = datetime.datetime.now()
t48h = now - timedelta(hours=48)
print(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"48 Hours Window cutoff: {t48h.strftime('%Y-%m-%d %H:%M:%S')}")

# 1. Cativa Digital Live API
print("\n--- 1. CONSULTANDO API CATIVA DIGITAL AO VIVO ---")
try:
    import cativa_api
    cativa_data = cativa_api.get_cativa_data(force_reload=True)
    st_cativa = cativa_data.get("students", [])
    print(f"Total de alunos na API Cativa: {len(st_cativa)}")
    for s in st_cativa:
        dt_raw = s.get("createdAt") or s.get("created_at") or s.get("creationDate")
        courses = s.get("courses", [])
        for c in courses:
            c_dt = c.get("enrollmentDate") or c.get("createdAt") or dt_raw
            print(f"   Aluno Cativa: {s.get('fullName')} ({s.get('email')}) - Curso: {c.get('courseName')} - Data: {c_dt}")
except Exception as e:
    print(f"Erro Cativa: {e}")

# 2. Academy Live API
print("\n--- 2. CONSULTANDO ACADEMY API / ALUNOS AO VIVO ---")
try:
    import academy_service
    # If academy_service has student fetch
    if hasattr(academy_service, 'fetch_academy_students'):
        st_acad = academy_service.fetch_academy_students()
        print(f"Alunos Academy: {len(st_acad)}")
except Exception as e:
    print(f"Academy note: {e}")

# 3. Asaas Live API
print("\n--- 3. CONSULTANDO ASAAS API AO VIVO ---")
try:
    import asaas_service
    asaas_data = asaas_service.get_asaas_data(force_reload=True)
    as_map = asaas_data.get("data", {})
    print(f"Total de clientes Asaas: {len(as_map)}")
    for k, st in as_map.items():
        fats = st.get("faturas", [])
        for ft in fats:
            stt = str(ft.get("status") or "").upper()
            dt = str(ft.get("data_pagamento") or ft.get("vencimento") or ft.get("dueDate") or "")
            if any(x in dt for x in ["22/09/2026", "23/09/2026", "24/09/2026", "2026-09-22", "2026-09-23", "2026-09-24"]):
                print(f"   Asaas: {st.get('customer_name')} ({st.get('customer_email')}) - Status: {stt} - Valor: {ft.get('valor')} - Data: {dt}")
except Exception as e:
    print(f"Erro Asaas: {e}")

# 4. Check all students in DATA with pending status
print("\n--- 4. ANALISANDO TODOS OS ALUNOS PENDENTES NO DATASET ---")
with open("dashboard_gerado.html", "r", encoding="utf-8") as f:
    html = f.read()

pos = html.find("const DATA = {")
end_pos = html.find("let CURRENT_DATA", pos)
semicolon_pos = html.rfind(";", pos, end_pos + 10)
data = json.loads(html[pos + len("const DATA = "):semicolon_pos])
students = data.get("students", [])
print(f"Total students in DATA: {len(students)}")
for s in students:
    # Check if pendente
    dt_insc = s.get("data_insc") or s.get("data_inscricao") or s.get("data_matricula")
    aulas = s.get("aulas_feitas", 0)
    print_flag = any(x in str(dt_insc) for x in ["2026-09-18", "2026-09-19", "2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "18/09/2026", "19/09/2026", "20/09/2026", "21/09/2026", "22/09/2026", "23/09/2026", "24/09/2026"])
    if print_flag:
        print(f"   Student: {s.get('nome')} ({s.get('email')}) - Curso: {s.get('curso')} - DataInsc: {dt_insc} - Aulas: {aulas} - Vindi: {bool(s.get('vindi'))} - Asaas: {bool(s.get('asaas'))}")

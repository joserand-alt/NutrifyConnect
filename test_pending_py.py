import os, json, re
from datetime import datetime, timedelta

BASE_DIR = r"C:\Users\DELL\Desktop\Dash_InfectoCast"

def parse_date_universal(d_str):
    if not d_str: return None
    s = str(d_str).strip()
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"]:
        try:
            return datetime.strptime(s.split('+')[0].split('.')[0], fmt if '.' not in fmt else "%Y-%m-%d")
        except:
            pass
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None

def is_internal_or_test(email, nome=""):
    em = str(email or "").lower().strip()
    nm = str(nome or "").lower().strip()
    if not em or "@" not in em:
        return True
    if any(x in em for x in ['@infectocast', '@integralmedica', '@nutrify', '@cativa', '@estrategia1', '@adtivo', 'teste']):
        return True
    if 'teste' in nm or em in ['gcotta29@gmail.com', 'j.o.s.e.r.a.n.d@gmail.com', 'email@email.com', 'wgww@gmail.com']:
        return True
    return False

def get_pending_enrollments(days=30):
    html_path = os.path.join(BASE_DIR, "dashboard_gerado.html")
    students = []
    v_fats = []
    a_fats = []

    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        pos = html.find('const DATA = {')
        if pos != -1:
            end_pos = html.find('let CURRENT_DATA', pos)
            semicolon_pos = html.rfind(';', pos, end_pos + 10)
            data_str = html[pos + len('const DATA = '):semicolon_pos]
            data = json.loads(data_str)
            students = data.get("students", [])
            v_fats = (data.get("financeiro") or {}).get("faturas_tabela", [])
            a_fats = (data.get("financeiro_asaas") or {}).get("faturas_tabela", [])

    # Paid emails
    paid_emails = set()
    for f in v_fats + a_fats:
        st = str(f.get("status") or "").lower()
        if st in ["pago", "paid", "received", "confirmed"]:
            em = str(f.get("email") or "").lower().strip()
            if em:
                paid_emails.add(em)

    now = datetime.now()
    cutoff_date = now - timedelta(days=days)

    pending_list = []
    seen = set()

    for s in students:
        em = str(s.get("email") or "").lower().strip()
        nm = str(s.get("nome") or "Lead / Inscrição").strip()
        if is_internal_or_test(em, nm):
            continue

        curso = s.get("curso") or "PLATAFORMA GERAL"
        pair_key = f"{em}|{curso}"
        if pair_key in seen:
            continue
        seen.add(pair_key)

        # Regra de pendente
        v_st = str((s.get("vindi") or {}).get("status_financeiro") or "").lower()
        a_st = str((s.get("asaas") or {}).get("status_financeiro") or "").lower()
        v_active = v_st in ["active", "ativo", "adimplente", "em_dia"]
        a_active = a_st in ["active", "ativo", "received", "confirmed", "adimplente", "em_dia"]
        v_f = (s.get("vindi") or {}).get("faturas") or []
        a_f = (s.get("asaas") or {}).get("faturas") or []
        v_paid = any(str(x.get("status") or "").lower() in ["pago", "paid"] or x.get("pago") for x in v_f)
        a_paid = any(str(x.get("status") or "").lower() in ["pago", "paid", "received", "confirmed"] or x.get("pago") for x in a_f)

        has_fin = (em in paid_emails) or v_active or a_active or v_paid or a_paid
        has_consumo = float(s.get("aulas_feitas") or 0) > 0

        if not has_fin and not has_consumo and s.get("status") != "Concluído":
            dt_insc = parse_date_universal(s.get("data_insc") or s.get("data_inscricao") or s.get("data_matricula") or s.get("first"))
            if dt_insc and dt_insc >= cutoff_date:
                pending_list.append({
                    "email": em,
                    "nome": nm,
                    "curso": curso,
                    "data_inscricao": dt_insc.strftime("%Y-%m-%d %H:%M:%S"),
                    "plataforma": s.get("plataforma") or "Academy",
                    "aulas_feitas": s.get("aulas_feitas") or 0
                })

    return pending_list

if __name__ == '__main__':
    res = get_pending_enrollments(30)
    print(f"Extracted {len(res)} pending enrollments in 30 days:")
    for r in res:
        print(" ->", r)

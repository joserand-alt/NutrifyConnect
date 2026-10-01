import json, os, re
from datetime import datetime, timedelta

def test_pending():
    base_dir = r'C:\Users\DELL\Desktop\Dash_InfectoCast'
    html_file = os.path.join(base_dir, 'dashboard_gerado.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    idx_start = html.find('const DATA = ')
    if idx_start == -1:
        idx_start = html.find('window.DATA = ')
    if idx_start != -1:
        json_start = html.find('{', idx_start)
        # Find closing matching brace or search for script tag
        # or load from cativa_cache.json + vindi_cache.json + asaas_cache.json
        pass

    # Better yet, let's load cativa_cache.json, vindi_cache.json, asaas_cache.json directly!
    cativa_path = os.path.join(base_dir, 'cativa_cache.json')
    vindi_path = os.path.join(base_dir, 'vindi_cache.json')
    asaas_path = os.path.join(base_dir, 'asaas_cache.json')

    with open(cativa_path, 'r', encoding='utf-8') as f:
        cativa = json.load(f)
    with open(vindi_path, 'r', encoding='utf-8') as f:
        vindi = json.load(f)
    with open(asaas_path, 'r', encoding='utf-8') as f:
        asaas = json.load(f)

    # Let's inspect cativa students
    cativa_students = cativa.get('students', [])
    vindi_data = vindi.get('data', {})
    asaas_data = asaas.get('data', {})

    # Paid emails
    paid_emails = set()
    for em, st in vindi_data.items():
        fats = st.get('faturas', [])
        if any(str(f.get('status') or '').lower() in ['pago', 'paid'] for f in fats) or float(st.get('total_pago') or 0) > 0:
            paid_emails.add(str(em).lower().strip())

    for k, st in asaas_data.items():
        em = str(st.get('customer_email') or '').lower().strip()
        fats = st.get('faturas', [])
        if any(str(f.get('status') or '').lower() in ['pago', 'paid', 'received', 'confirmed'] for f in fats) or float(st.get('total_pago') or 0) > 0:
            paid_emails.add(em)

    def is_invalid(em, nm):
        em = (em or '').lower().strip()
        nm = (nm or '').lower().strip()
        if not em or '@' not in em: return True
        if any(x in em for x in ['@infectocast', '@integralmedica', '@nutrify', '@cativa', '@estrategia1', '@adtivo']): return True
        if 'teste' in em or 'teste' in nm: return True
        if em in ['gcotta29@gmail.com', 'j.o.s.e.r.a.n.d@gmail.com', 'email@email.com', 'wgww@gmail.com']: return True
        return False

    def parse_date(d_str):
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

    now = datetime.now()
    t30d = now - timedelta(days=30)

    pending_list = []
    seen = set()

    for s in cativa_students:
        em = str(s.get('email') or '').lower().strip()
        nm = str(s.get('fullName') or '').strip()
        if is_invalid(em, nm): continue

        courses = s.get('courses', [])
        for c in courses:
            c_name = c.get('courseName') or 'Pós-Graduação InfectoCast'
            pair = (em, c_name)
            if pair in seen: continue
            seen.add(pair)

            # Check if paid
            if em in paid_emails:
                continue

            dt_enr = parse_date(c.get('enrollmentDate') or s.get('createdAt') or s.get('created_at'))
            # Let's check if within 30d
            if dt_enr and dt_enr >= t30d:
                pending_list.append({
                    "email": em,
                    "nome": nm,
                    "curso": c_name,
                    "data_inscricao": dt_enr.strftime("%Y-%m-%d %H:%M:%S"),
                    "plataforma": "Cativa Digital"
                })

    print(f"Total pendentes nos últimos 30 dias: {len(pending_list)}")
    for p in pending_list:
        print(f" - {p['email']} | {p['nome']} | {p['curso']} | {p['data_inscricao']}")

if __name__ == '__main__':
    test_pending()

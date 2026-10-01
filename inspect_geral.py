import json, re, os

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

d_match = re.search(r'const DATA = ({[\s\S]*?});', text)
DATA = json.loads(d_match.group(1))

acad_logs = json.load(open('academy_logs_cache.json', encoding='utf-8')) if os.path.exists('academy_logs_cache.json') else []
vindi_data = json.load(open('vindi_cache.json', encoding='utf-8')) if os.path.exists('vindi_cache.json') else {}
asaas_data = json.load(open('asaas_cache.json', encoding='utf-8')) if os.path.exists('asaas_cache.json') else {}
rd_tagged = json.load(open('rd_tagged_matriculas.json', encoding='utf-8')) if os.path.exists('rd_tagged_matriculas.json') else {}
rd_students = json.load(open('rd_students_cache.json', encoding='utf-8')) if os.path.exists('rd_students_cache.json') else {}
cativa_data = json.load(open('cativa_cache.json', encoding='utf-8')) if os.path.exists('cativa_cache.json') else {}

geral_students = [s for s in DATA['students'] if s.get('curso') == 'PLATAFORMA GERAL']

print(f"=== INSPECTING {len(geral_students)} STUDENTS WITH PLATAFORMA GERAL ===")

for s in geral_students:
    em = (s.get('email') or '').lower().strip()
    nm = s.get('nome') or ''
    user_logs = [l for l in acad_logs if (l.get('E-mail') or '').lower().strip() == em]
    items_in_logs = list(set(f"{l.get('Ação / Local')} -> {l.get('ID Item')} ({l.get('Desc. Item')}) [Modulo: {l.get('Modulo')}]" for l in user_logs))
    
    # Check RD
    rd_info = rd_tagged.get(em) or rd_students.get(em) or {}
    
    # Check Vindi
    v_info = vindi_data.get('data', {}).get(em)
    
    # Check Asaas
    a_info = asaas_data.get('data', {}).get(em)
    
    # Check Cativa
    c_info = None
    for cs in cativa_data.get('students', []):
        if (cs.get('email') or '').lower().strip() == em:
            c_info = cs
            break

    print(f"\n------------------------------------------------------------")
    print(f"EMAIL: {em} | NOME: {nm}")
    print(f"  Acad Logs ({len(user_logs)}): {items_in_logs[:3]}")
    if rd_info:
        print(f"  RD: {rd_info}")
    if v_info:
        print(f"  Vindi plano: {v_info.get('plano')}")
    if a_info:
        print(f"  Asaas faturas: {[f.get('description') for f in a_info.get('faturas', [])]}")
    if c_info:
        print(f"  Cativa courses: {[c.get('courseName') for c in c_info.get('courses', [])]}")

import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    students = data.get('students', [])
    
    # Map email to course
    email_to_course = {}
    name_to_course = {}
    for s in students:
        em = str(s.get('email', '')).lower().strip()
        nm = str(s.get('nome', '')).lower().strip()
        curso = s.get('curso') or 'OUTROS / NÃO ESPECIFICADO'
        if em:
            email_to_course[em] = curso
        if nm:
            name_to_course[nm] = curso

    print(f"Total students: {len(students)}, mapped emails: {len(email_to_course)}")
    
    # Test Vindi faturas
    v_fat = data.get('financeiro', {}).get('faturas_tabela', [])
    matched_v = 0
    course_revenue = {}
    for f in v_fat:
        em = str(f.get('email', '')).lower().strip()
        nm = str(f.get('aluno', '')).lower().strip()
        c = email_to_course.get(em) or name_to_course.get(nm)
        if c:
            matched_v += 1
        else:
            c = 'OUTROS / PLATAFORMA GERAL'
        
        if c not in course_revenue:
            course_revenue[c] = {'pago': 0, 'atraso': 0, 'proj': 0, 'count': 0}
        
        val = float(f.get('valor') or 0)
        st = f.get('status')
        if st == 'pago' or st == 'paid':
            course_revenue[c]['pago'] += val
        elif st == 'em_atraso':
            course_revenue[c]['atraso'] += val
        elif st in ('a_vencer', 'futuro', 'pending', 'open'):
            course_revenue[c]['proj'] += val
        course_revenue[c]['count'] += 1

    print(f"Matched Vindi faturas to student courses: {matched_v} of {len(v_fat)}")
    
    # Test Asaas faturas
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])
    matched_a = 0
    for f in a_fat:
        em = str(f.get('email', '')).lower().strip()
        nm = str(f.get('aluno', '')).lower().strip()
        c = email_to_course.get(em) or name_to_course.get(nm)
        if c:
            matched_a += 1
        else:
            c = 'OUTROS / PLATAFORMA GERAL'
        
        if c not in course_revenue:
            course_revenue[c] = {'pago': 0, 'atraso': 0, 'proj': 0, 'count': 0}
        
        val = float(f.get('valor') or 0)
        st = f.get('status')
        if st == 'pago' or st == 'paid':
            course_revenue[c]['pago'] += val
        elif st == 'em_atraso':
            course_revenue[c]['atraso'] += val
        elif st in ('a_vencer', 'futuro', 'pending', 'open'):
            course_revenue[c]['proj'] += val
        course_revenue[c]['count'] += 1

    print(f"Matched Asaas faturas to student courses: {matched_a} of {len(a_fat)}")
    print("\nCourse revenue breakdown:")
    for c, r in sorted(course_revenue.items(), key=lambda x: -x[1]['pago']):
        print(f"  {c}: Pago R$ {r['pago']:,.2f} | Atraso R$ {r['atraso']:,.2f} | Proj R$ {r['proj']:,.2f}")

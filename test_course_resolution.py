import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    students = data.get('students', [])
    v_fat = data.get('financeiro', {}).get('faturas_tabela', [])
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])
    
    # 1. Build lookup from students
    email_to_course = {}
    name_to_course = {}
    for s in students:
        em = str(s.get('email', '')).lower().strip()
        nm = str(s.get('nome', '')).lower().strip()
        c = s.get('curso')
        if em and c and c != 'PLATAFORMA GERAL':
            email_to_course[em] = c
        if nm and c and c != 'PLATAFORMA GERAL':
            name_to_course[nm] = c

    def resolve_course(email, aluno, plano, desc):
        em = str(email or '').lower().strip()
        nm = str(aluno or '').lower().strip()
        
        # Priority 1: Match with enrolled student in LMS
        if em and em in email_to_course:
            return email_to_course[em]
        if nm and nm in name_to_course:
            return name_to_course[nm]
            
        # Priority 2: Infer from plano or description text
        text_full = f"{plano or ''} {desc or ''}".lower()
        if 'ccih' in text_full or 'preven' in text_full or 'hospitalar' in text_full:
            return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'
        if 'ortop' in text_full or 'partes moles' in text_full:
            return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PELE E PARTES MOLES'
        if 'imuno' in text_full or 'inuno' in text_full:
            return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'
        if 'pediatria' in text_full or 'infectoped' in text_full:
            return 'POS-GRADUACAO EM INFECTOPEDIATRIA'
        if 'multi-r' in text_full or 'multi r' in text_full:
            return 'JORNADA MULTI-R'
        if 'fungo' in text_full or 'antifung' in text_full:
            return 'DO FUNGO AO ANTIFUNGICO'
        if 's.o.s' in text_full or 'antibiotico' in text_full or 'antibitico' in text_full:
            return 'S.O.S ANTIBIOTICO'
        if 'qualidade' in text_full:
            return 'FERRAMENTAS DE QUALIDADE'
            
        return 'PLATAFORMA GERAL'

    all_fat = [('Vindi', f) for f in v_fat] + [('Asaas', f) for f in a_fat]
    resolved_counts = {}
    for gw, f in all_fat:
        c = resolve_course(f.get('email'), f.get('aluno'), f.get('plano'), f.get('description'))
        resolved_counts[c] = resolved_counts.get(c, 0) + 1

    print(f"Total faturas tested: {len(all_fat)}")
    print("Resolved course distribution:")
    for c, cnt in sorted(resolved_counts.items(), key=lambda x: -x[1]):
        print(f"  {c}: {cnt} faturas")

    # Specifically check the 8 students from the user's screenshot:
    screenshot_emails = [
        'leticia.figueiredogomes@gmail.com',
        'alicia_morais@hotmail.com',
        'silviamariane11@hotmail.com',
        'priscila.brandao3005@gmail.com',
        'tatianacamposm2014@gmail.com',
        'marcoseduardocabral@hotmail.com',
        'laurawarlitzer@gmail.com',
        'victorialopes3021@gmail.com'
    ]
    print("\nResolution for students in screenshot:")
    for gw, f in all_fat:
        em = str(f.get('email', '')).lower().strip()
        if em in screenshot_emails:
            c = resolve_course(f.get('email'), f.get('aluno'), f.get('plano'), f.get('description'))
            print(f"  {f.get('aluno')} ({em}) -> {c}")
            screenshot_emails.remove(em)

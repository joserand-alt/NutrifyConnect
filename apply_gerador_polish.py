import re

gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'
with open(gerador_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Fix canonicalize_curso to return None on numeric / unmapped turma
old_can = """        if 'FERRAMENTAS' in t_norm or 'QUALIDADE' in t_norm:
            return normalize_curso('FERRAMENTAS DE QUALIDADE')
        if 'INFECTOXPERT' in t_norm or 'EXPERT' in t_norm:
            return normalize_curso('INFECTOXPERT')
        return normalize_curso(turma)"""

new_can = """        if 'FERRAMENTAS' in t_norm or 'QUALIDADE' in t_norm:
            return normalize_curso('FERRAMENTAS DE QUALIDADE')
        if 'INFECTOXPERT' in t_norm or 'EXPERT' in t_norm:
            return normalize_curso('INFECTOXPERT')
        if not t_norm or t_norm.replace('.', '').replace(' ', '').isdigit():
            return None
        return normalize_curso(turma)"""

if old_can in code:
    code = code.replace(old_can, new_can, 1)
    print("Fixed canonicalize_curso numeric check!")

# 2. Fix pg_events loop to check if canonicalize_curso returned None
old_pg = """    pg_events = df_log[df_log['Ação / Local'] == 'PG INSCRIÇÃO TURMA']
    for _, row in pg_events.iterrows():
        email = str(row['E-mail']).strip()
        turma = str(row['ID Item'] or row['Desc. Item'] or '').strip()
        if turma and turma != 'nan' and email not in student_course_map:
            student_course_map[email] = canonicalize_curso(turma)"""

new_pg = """    pg_events = df_log[df_log['Ação / Local'] == 'PG INSCRIÇÃO TURMA']
    for _, row in pg_events.iterrows():
        email = str(row['E-mail']).strip()
        turma = str(row['ID Item'] or row['Desc. Item'] or '').strip()
        if turma and turma != 'nan' and email not in student_course_map:
            c_norm = canonicalize_curso(turma)
            if c_norm:
                student_course_map[email] = c_norm"""

if old_pg in code:
    code = code.replace(old_pg, new_pg, 1)
    print("Fixed pg_events loop in gerador.py!")

# 3. Update get_student_course_and_date and student loop to check RD hints
old_acad_loop = """        curso_aluno, dt_insc_aluno = get_student_course_and_date(email, logs, None)
        
        # Safely compute dias_desde_insc and data_insc
        try:
            if dt_insc_aluno is not None and pd.notna(dt_insc_aluno):
                if hasattr(dt_insc_aluno, 'date'):
                    dias_desde_insc = (hoje - dt_insc_aluno.date()).days
                    data_insc_fmt = dt_insc_aluno.strftime("%d/%m/%Y")
                else:
                    dias_desde_insc = 0
                    data_insc_fmt = None
            else:
                dias_desde_insc = 0
                data_insc_fmt = None
        except Exception:
            dias_desde_insc = 0
            data_insc_fmt = None
        
        telefone = ""
        if email_str in cativa_users_meta:
            telefone = normalize_phone(cativa_users_meta[email_str].get('phone', ''))
            
        student_data = {
            "email": str(email),
            "nome": nome_aluno,
            "curso": curso_aluno,
            "curso_inferido": False,
            "curso_origem": "Log de Acesso",
            "telefone": telefone,
            "acessou": acessou,
            "data_insc": data_insc_fmt,
            "data_inscricao": data_insc_fmt,
            "inscricao": data_insc_fmt,
            "dias_desde_insc": dias_desde_insc,
            "plataforma": "Academy",
            "id_aluno": ""
        }"""

new_acad_loop = """        curso_aluno, dt_insc_aluno = get_student_course_and_date(email, logs, None)
        
        c_inferido = False
        c_origem = "Log de Acesso"
        if curso_aluno in ["PLATAFORMA GERAL", "SEM CURSO", "CURSO DESCONHECIDO"] and 'rd_course_hints' in locals() and email_str in rd_course_hints:
            curso_aluno = rd_course_hints[email_str]
            c_inferido = True
            c_origem = "RD Station"
        
        # Safely compute dias_desde_insc and data_insc
        try:
            if dt_insc_aluno is not None and pd.notna(dt_insc_aluno):
                if hasattr(dt_insc_aluno, 'date'):
                    dias_desde_insc = (hoje - dt_insc_aluno.date()).days
                    data_insc_fmt = dt_insc_aluno.strftime("%d/%m/%Y")
                else:
                    dias_desde_insc = 0
                    data_insc_fmt = None
            else:
                dias_desde_insc = 0
                data_insc_fmt = None
        except Exception:
            dias_desde_insc = 0
            data_insc_fmt = None
        
        telefone = ""
        if email_str in cativa_users_meta:
            telefone = normalize_phone(cativa_users_meta[email_str].get('phone', ''))
            
        student_data = {
            "email": str(email),
            "nome": nome_aluno,
            "curso": curso_aluno,
            "curso_inferido": c_inferido,
            "curso_origem": c_origem,
            "telefone": telefone,
            "acessou": acessou,
            "data_insc": data_insc_fmt,
            "data_inscricao": data_insc_fmt,
            "inscricao": data_insc_fmt,
            "dias_desde_insc": dias_desde_insc,
            "plataforma": "Academy",
            "id_aluno": ""
        }"""

if old_acad_loop in code:
    code = code.replace(old_acad_loop, new_acad_loop, 1)
    print("Updated student loop course inference!")

# 4. Link Vindi by (email + curso)
old_vindi_link = """        # Link Vindi to existing students
        for s in students:
            em = str(s.get('email', '')).lower().strip()
            if em in vindi_map:
                s['vindi'] = vindi_map[em]
                vindi_matched += 1
            else:
                s['vindi'] = None"""

new_vindi_link = """        # Link Vindi to existing students (matching by email + course first)
        for s in students:
            em = str(s.get('email', '')).lower().strip()
            c_s = str(s.get('curso', '')).strip()
            key_ec = f"{em}___{c_s}"
            if key_ec in vindi_map:
                s['vindi'] = vindi_map[key_ec]
                vindi_matched += 1
            elif em in vindi_map:
                s['vindi'] = vindi_map[em]
                vindi_matched += 1
            else:
                s['vindi'] = None"""

if old_vindi_link in code:
    code = code.replace(old_vindi_link, new_vindi_link, 1)
    print("Updated Vindi linking by email + course!")

with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved gerador.py final polish successfully!")

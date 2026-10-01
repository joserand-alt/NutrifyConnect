import sys, os, re, json, unicodedata
import pandas as pd

gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'
with open(gerador_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update main() imports and loading of sheets
old_load = """    inscricoes_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\Inscrições.xlsx'
    cursos_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\CURSOS.xlsx'
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')
    
    print("Carregando planilhas...")
    df_insc = pd.read_excel(inscricoes_path)
    df_log = fetch_logs_from_api(df_insc)
    xls_cursos = pd.ExcelFile(cursos_path)
    
    df_mods = xls_cursos.parse(1)
    df_aulas = xls_cursos.parse(2)
    
    df_insc['Data Inscrição'] = pd.to_datetime(df_insc['Data Inscrição'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    hoje = df_log['Data log'].max().date() + datetime.timedelta(days=1)
    inscritos = df_insc['E-mail'].dropna().unique()"""

new_load = """    cursos_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\CURSOS.xlsx'
    log_uso_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\Log de uso.xlsx'
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')
    
    print("Carregando logs de uso da plataforma Academy...")
    if os.path.exists(log_uso_path):
        df_log = pd.read_excel(log_uso_path)
        df_log['Data log'] = pd.to_datetime(df_log['Data log'], errors='coerce')
        df_log['Plataforma'] = 'Academy'
    else:
        df_log = pd.DataFrame(columns=['Data log', 'Nome aluno', 'E-mail', 'Ação / Local', 'ID Item', 'Desc. Item', 'Plataforma'])
        
    xls_cursos = pd.ExcelFile(cursos_path)
    df_mods = xls_cursos.parse(1)
    df_aulas = xls_cursos.parse(2)
    
    hoje = df_log['Data log'].max().date() + datetime.timedelta(days=1) if not df_log['Data log'].dropna().empty else datetime.date.today()
    inscritos = df_log['E-mail'].dropna().unique()"""

if old_load in code:
    code = code.replace(old_load, new_load, 1)
    print("Replaced main load block successfully!")
else:
    # Try regex replacement for main load
    pat_load = r'inscricoes_path = [^\n]+\n\s*cursos_path = [^\n]+\n\s*template_path = [^\n]+\n\s*print\([^\n]+\)\n\s*df_insc = [^\n]+\n\s*df_log = [^\n]+\n\s*xls_cursos = [^\n]+\n\s*df_mods = [^\n]+\n\s*df_aulas = [^\n]+\n\s*df_insc\[[^\n]+\n\s*hoje = [^\n]+\n\s*inscritos = [^\n]+'
    code = re.sub(pat_load, new_load.strip(), code, count=1)
    print("Replaced main load block via regex!")

# 2. Update student_course_map construction (remove df_insc reference)
old_course_map = """    # Second pass: infer from content for students without PG event
    for _, insc in df_insc.dropna(subset=['E-mail']).drop_duplicates(subset=['E-mail']).iterrows():
        email = str(insc['E-mail']).strip()
        if email in student_course_map:
            continue
        
        excel_curso = str(insc.get('CURSO', '')).strip()
        core_excel = get_core_subject(excel_curso)
        
        if core_excel == 'INFECTOPEDIATRIA':
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')
            continue
        elif core_excel == 'ORTOPEDIA':
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')
            continue
        elif core_excel == 'CCIH':
            if 'FARM' in norm_title(excel_curso) or 'ENF' in norm_title(excel_curso):
                student_course_map[email] = canonicalize_curso(excel_curso)
            else:
                student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')
            continue
        elif core_excel == 'IMUNODEPRIMIDOS':
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS')
            continue
        elif core_excel == 'SOS':
            student_course_map[email] = normalize_curso('S.O.S ANTIBIÓTICO')
            continue

        student_logs = df_log[df_log['E-mail'] == email]
        aula_logs = student_logs[student_logs['Ação / Local'].isin(['INICIOU AULA', 'CONCLUIU AULA'])]
        all_text = ' '.join(aula_logs['ID Item'].fillna('').astype(str)).upper()
        all_text = norm_title(all_text)

        if any(w in all_text for w in ['PEDIATRIA', 'INFECTOPEDIATRIA', 'NEONATAL', 'CRIANCA', 'SIFILIS CONGENITA']):
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')
        elif any(w in all_text for w in ['ORTOPEDIA', 'ORTO', 'PARTES MOLES', 'MUSCULOESQUELETICA']):
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')
        elif any(w in all_text for w in ['CCIH', 'INFECCAO HOSPITALAR', 'PREVENCAO', 'VIGILANCIA', 'PAV', 'ISC', 'IPCSL']):
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')
        elif any(w in all_text for w in ['ANTIBIOTICO', 'S.O.S', 'ESBL', 'KPC', 'NDM', 'CRAB', 'PARC', 'MDR']):
            student_course_map[email] = normalize_curso('S.O.S ANTIBIÓTICO')
        elif any(w in all_text for w in ['FERRAMENTAS', 'ISHIKAWA', 'PARETO', 'PDCA', 'SIPOC', 'BRAINSTORMING', 'GEMBA']):
            student_course_map[email] = normalize_curso('FERRAMENTAS DE QUALIDADE')
        else:
            excel_curso = str(insc.get('CURSO', '')).strip()
            if excel_curso and excel_curso != 'nan':
                student_course_map[email] = canonicalize_curso(excel_curso)
            else:
                student_course_map[email] = normalize_curso('CURSO DESCONHECIDO')"""

new_course_map = """    # Second pass: infer from watched lessons content for students without explicit PG event
    for email in df_log['E-mail'].dropna().unique():
        email = str(email).strip()
        if email in student_course_map:
            continue

        student_logs = df_log[df_log['E-mail'] == email]
        aula_logs = student_logs[student_logs['Ação / Local'].isin(['INICIOU AULA', 'CONCLUIU AULA'])]
        all_text = ' '.join(aula_logs['ID Item'].fillna('').astype(str)).upper()
        all_text = norm_title(all_text)

        if any(w in all_text for w in ['PEDIATRIA', 'INFECTOPEDIATRIA', 'NEONATAL', 'CRIANCA', 'SIFILIS CONGENITA']):
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')
        elif any(w in all_text for w in ['ORTOPEDIA', 'ORTO', 'PARTES MOLES', 'MUSCULOESQUELETICA']):
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')
        elif any(w in all_text for w in ['CCIH', 'INFECCAO HOSPITALAR', 'PREVENCAO', 'VIGILANCIA', 'PAV', 'ISC', 'IPCSL']):
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')
        elif any(w in all_text for w in ['IMUNO', 'IMUNODEPRIMIDO', 'TRANSPLANTE']):
            student_course_map[email] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS')
        elif any(w in all_text for w in ['ANTIBIOTICO', 'S.O.S', 'ESBL', 'KPC', 'NDM', 'CRAB', 'PARC', 'MDR']):
            student_course_map[email] = normalize_curso('S.O.S ANTIBIÓTICO')
        elif any(w in all_text for w in ['FERRAMENTAS', 'ISHIKAWA', 'PARETO', 'PDCA', 'SIPOC', 'BRAINSTORMING', 'GEMBA']):
            student_course_map[email] = normalize_curso('FERRAMENTAS DE QUALIDADE')
        else:
            student_course_map[email] = normalize_curso('PLATAFORMA GERAL')"""

if old_course_map in code:
    code = code.replace(old_course_map, new_course_map, 1)
    print("Replaced course map block successfully!")
else:
    pat_cmap = r'# Second pass: infer from content for students without PG event\s*for _, insc in df_insc[\s\S]*?student_course_map\[email\] = normalize_curso\(\'CURSO DESCONHECIDO\'\)'
    code = re.sub(pat_cmap, new_course_map.strip(), code, count=1)
    print("Replaced course map block via regex!")

# 3. Update the student loop to iterate over df_log unique emails
old_loop_header = """    students = []
    
    unique_insc = df_insc.dropna(subset=['E-mail']).drop_duplicates(subset=['E-mail', 'CURSO'])
    
    for _, insc in unique_insc.iterrows():
        email = insc['E-mail']
        email_str = str(email).lower()
        if 'teste' in email_str or '@infectocast' in email_str or '@vectorcomunica' in email_str or 'gcotta29@gmail.com' in email_str or 'rand' in email_str:
            continue
            
        logs = df_log[df_log['E-mail'] == email]
        acessou = len(logs) > 0

        excel_d = insc['Data Inscrição'] if pd.notna(insc['Data Inscrição']) else None
        curso_aluno, dt_insc_aluno = get_student_course_and_date(email, logs, excel_d)"""

new_loop_header = """    students = []
    
    df_acad = df_log[df_log.get('Plataforma', 'Academy') == 'Academy'] if 'Plataforma' in df_log.columns else df_log
    unique_academy_students = df_acad.dropna(subset=['E-mail']).drop_duplicates(subset=['E-mail'])
    
    for _, log_row in unique_academy_students.iterrows():
        email = str(log_row['E-mail']).strip()
        email_str = email.lower()
        if not email_str or email_str == 'nan' or 'teste' in email_str or '@infectocast' in email_str or '@vectorcomunica' in email_str or 'rand' in email_str:
            continue
            
        logs = df_log[df_log['E-mail'] == email]
        acessou = len(logs) > 0
        nome_aluno = str(logs['Nome aluno'].dropna().iloc[0]).strip() if not logs['Nome aluno'].dropna().empty else email_str

        curso_aluno, dt_insc_aluno = get_student_course_and_date(email, logs, None)"""

if old_loop_header in code:
    code = code.replace(old_loop_header, new_loop_header, 1)
    print("Replaced loop header successfully!")
else:
    pat_lhead = r'students = \[\]\s*unique_insc = df_insc[\s\S]*?curso_aluno, dt_insc_aluno = get_student_course_and_date\(email, logs, excel_d\)'
    code = re.sub(pat_lhead, new_loop_header.strip(), code, count=1)
    print("Replaced loop header via regex!")

# Update student_data dictionary in the loop (replace insc['Aluno'], insc['Telefone'], etc.)
old_st_dict = """        telefone = str(insc['Telefone']).strip() if 'Telefone' in insc and pd.notna(insc['Telefone']) else ""
        if telefone.endswith('.0'): telefone = telefone[:-2]
        if telefone == 'nan': telefone = ""
        
        has_acad = any(logs['Plataforma'] == 'Academy')
        has_cat = any(logs['Plataforma'] == 'Cativa')
        plat_str = 'Ambas' if (has_acad and has_cat) else ('Cativa' if has_cat else 'Academy')
        if not telefone and email_str in cativa_users_meta:
            telefone = normalize_phone(cativa_users_meta[email_str].get('phone', ''))
        student_data = {
            "email": str(email),
            "nome": str(insc['Aluno']),
            "curso": curso_aluno,
            "telefone": telefone,
            "acessou": acessou,
            "data_insc": data_insc_fmt,
            "data_inscricao": data_insc_fmt,
            "inscricao": data_insc_fmt,
            "dias_desde_insc": dias_desde_insc,
            "plataforma": plat_str,
            "id_aluno": str(int(insc['ID Aluno'])) if pd.notna(insc.get('ID Aluno')) else ""
        }"""

new_st_dict = """        telefone = ""
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

if old_st_dict in code:
    code = code.replace(old_st_dict, new_st_dict, 1)
    print("Replaced student_data dict successfully!")
else:
    pat_stdict = r'telefone = str\(insc\[\'Telefone\'\]\)[\s\S]*?"id_aluno": str\(int\(insc\[\'ID Aluno\'\]\)\) if pd\.notna\(insc\.get\(\'ID Aluno\'\)\) else ""\s*\}'
    code = re.sub(pat_stdict, new_st_dict.strip(), code, count=1)
    print("Replaced student_data dict via regex!")

# Also clean up references to insc.get('Telefone') in WA history mapping:
code = code.replace("phone1 = normalize_phone(insc.get('Telefone'))\n            phone2 = normalize_phone(insc.get('Celular'))", "phone1 = telefone\n            phone2 = ''")
code = code.replace("(first_log.date() - insc['Data Inscrição'].date()).days if pd.notna(insc['Data Inscrição']) else 0", "0")

# 4. Update Funil references to df_insc
code = code.replace(
    "emails_inscritos_set = set(str(e).lower().strip() for e in df_insc['E-mail'].dropna().unique())",
    "emails_inscritos_set = set(str(s['email']).lower().strip() for s in students if s.get('email'))"
)
code = code.replace(
    "for _, row in df_insc.dropna(subset=['E-mail']).iterrows():\n            em = str(row['E-mail']).lower().strip()\n            if pd.notna(row['Data Inscrição']):\n                insc_dates[em] = row['Data Inscrição'].date()",
    "for s in students:\n            em = str(s.get('email', '')).lower().strip()\n            dt_i = s.get('data_insc') or s.get('data_inscricao')\n            if dt_i:\n                try: insc_dates[em] = pd.to_datetime(dt_i, dayfirst=True).date()\n                except: pass"
)

# 5. Add Vindi students who do not yet have access logs as inferred students
vindi_integration_snippet = """    # ============================================
    # VINDI FINANCEIRO
    # ============================================
    vindi_matched = 0
    financeiro_data = {}
    try:
        from vindi_service import get_vindi_data
        vindi_res = get_vindi_data(force_reload=False)
        vindi_map = vindi_res.get('data', {}) if isinstance(vindi_res, dict) and 'data' in vindi_res else vindi_res
        financeiro_data = vindi_res.get('financeiro', {}) if isinstance(vindi_res, dict) else {}
        
        # Link Vindi to existing students
        for s in students:
            em = str(s.get('email', '')).lower().strip()
            if em in vindi_map:
                s['vindi'] = vindi_map[em]
                vindi_matched += 1
            else:
                s['vindi'] = None
                
        # Add Vindi subscribers who don't have access logs yet (as inferred students)
        existing_vindi_emails = set(str(s.get('email', '')).lower().strip() for s in students if s.get('email'))
        for em, v_obj in vindi_map.items():
            em_clean = str(em).lower().strip()
            if em_clean and em_clean not in existing_vindi_emails and isinstance(v_obj, dict):
                # Infer course from Vindi plan or RD hints
                plano_v = v_obj.get('plano', '')
                c_inferido = "PLATAFORMA GERAL"
                c_orig = "Plano Vindi"
                if 'rd_course_hints' in locals() and em_clean in rd_course_hints:
                    c_inferido = rd_course_hints[em_clean]
                    c_orig = "RD Station"
                elif plano_v:
                    p_up = plano_v.upper()
                    if 'ORTOPED' in p_up: c_inferido = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')
                    elif 'CCIH' in p_up or 'PREVENCAO' in p_up: c_inferido = normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')
                    elif 'IMUNO' in p_up: c_inferido = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS')
                    elif 'PED' in p_up: c_inferido = normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')
                    elif 'SOS' in p_up: c_inferido = normalize_curso('S.O.S ANTIBIÓTICO')
                
                existing_vindi_emails.add(em_clean)
                new_v_st = {
                    "email": em_clean,
                    "nome": v_obj.get('customer_name') or 'Aluno Vindi',
                    "curso": c_inferido,
                    "curso_inferido": True,
                    "curso_origem": c_orig,
                    "telefone": "",
                    "acessou": False,
                    "data_insc": None,
                    "data_inscricao": None,
                    "inscricao": None,
                    "dias_desde_insc": 0,
                    "plataforma": "Academy",
                    "id_aluno": str(v_obj.get('customer_id', '')),
                    "events": [],
                    "vindi": v_obj,
                    "asaas": None
                }
                if 'rd_events_map' in locals() and em_clean in rd_events_map:
                    new_v_st['rd_funnel'] = dict(rd_events_map[em_clean])
                students.append(new_v_st)
                vindi_matched += 1
                
        print(f"[VINDI] {vindi_matched} estudantes vinculados com dados financeiros da Vindi.")
    except Exception as e_vindi:
        print(f"[VINDI] Erro ao integrar Vindi no gerador: {e_vindi}")
        for s in students:
            s['vindi'] = None"""

pat_vindi = r'# =+\s*# VINDI FINANCEIRO[\s\S]*?print\(f"\[VINDI\] \{vindi_matched\} estudantes vinculados com dados financeiros da Vindi\."\)\s*except Exception as e_vindi:[\s\S]*?s\[\'vindi\'\] = None'
m_vindi = re.search(pat_vindi, code)
if m_vindi:
    code = code[:m_vindi.start()] + vindi_integration_snippet.strip() + code[m_vindi.end():]
    print("Updated Vindi integration block in gerador.py!")

with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved updated gerador.py successfully!")

import os

target_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'
with open(target_file, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Ensure rd_course_hints is created and available
old_rd = """        # Extract RD history for enrolled students to embed in their object
        rd_events_map = {}
        for _, row in df_rd[df_rd['e_aluno']].iterrows():"""

new_rd = """        # Extract RD history and course hints from LogRD
        rd_events_map = {}
        rd_course_hints = {}
        for _, row in df_rd.iterrows():
            email_k = str(row['email_lower']).strip()
            if not email_k or email_k == 'nan': continue
            
            # Infer course hint from RD lead tags and events
            tags_r = str(row.get('Tags', '')).lower()
            events_r = str(row.get(ev_col_name, '')).lower() if ev_col_name else ''
            curso_r = str(row.get('Curso', '')).lower()
            pos_r = str(row.get('Curso da Pós-graduação InfectoCast', '')).lower()
            comb_r = f"{tags_r} {events_r} {curso_r} {pos_r}"
            
            if '[ccih]' in tags_r or 'pos-ccih' in comb_r or 'ebook ccih' in comb_r or 'pga enfermagem' in comb_r or 'prevenção e controle' in comb_r:
                rd_course_hints[email_k] = normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')
            elif '[ped]' in tags_r or 'pos-ped' in comb_r or 'infectoped' in comb_r or 'pediatria' in comb_r:
                rd_course_hints[email_k] = normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')
            elif '[ortoped]' in tags_r or 'ortoped' in comb_r or 'partes moles' in comb_r:
                rd_course_hints[email_k] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')
            elif '[imuno]' in tags_r or 'imuno' in comb_r or 'imunodeprimidos' in comb_r:
                rd_course_hints[email_k] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS')
            elif 'sos-antibiotico' in comb_r or 'sos atb' in comb_r or 'ebook-novos-antibioticos' in comb_r or 'jornada multi-r' in comb_r:
                rd_course_hints[email_k] = normalize_curso('S.O.S ANTIBIÓTICO')"""

if old_rd in code:
    code = code.replace(old_rd, new_rd, 1)
    print("Replaced old_rd successfully!")
else:
    print("Warning: old_rd not found, checking alternatives...")

# 2. Update _infer_curso_from_asaas
old_infer = """        def _infer_curso_from_asaas(asaas_st, email):
            \"\"\"Tenta resolver o curso do aluno Asaas usando student_course_map ou valor do plano.\"\"\"
            # 1. Verifica student_course_map (logs + planilhas)
            if email in student_course_map:
                return student_course_map[email]"""

new_infer = """        def _infer_curso_from_asaas(asaas_st, email):
            \"\"\"Tenta resolver o curso do aluno Asaas usando student_course_map, RD Station ou descrição da fatura.\"\"\"
            # 1. Verifica student_course_map (logs + planilhas)
            if email in student_course_map:
                return student_course_map[email]
            
            # 2. Verifica dicas do RD Station (Tags e Eventos)
            if 'rd_course_hints' in locals() and email in rd_course_hints:
                return rd_course_hints[email]"""

if old_infer in code:
    code = code.replace(old_infer, new_infer, 1)
    print("Replaced old_infer successfully!")
else:
    print("Warning: old_infer not found, checking alternatives...")

# 3. Attach rd_funnel when adding Asaas student
old_append = """                students.append({
                    "email": st_email,
                    "nome": asaas_st.get('customer_name') or 'Aluno Academy',
                    "curso": curso_resolved,
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
                })"""

new_append = """                new_st = {
                    "email": st_email,
                    "nome": asaas_st.get('customer_name') or 'Aluno Academy',
                    "curso": curso_resolved,
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
                }
                if 'rd_events_map' in locals() and st_email in rd_events_map:
                    new_st['rd_funnel'] = dict(rd_events_map[st_email])
                students.append(new_st)"""

if old_append in code:
    code = code.replace(old_append, new_append, 1)
    print("Replaced old_append successfully!")
else:
    print("Warning: old_append not found, checking alternatives...")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved gerador.py successfully!")

import os, re, json

gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'
with open(gerador_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Move LogRD processing before students = []
# Find LogRD block
rd_block_pattern = r'# =+\s*# FUNIL DE LEADS — Processamento LogRD\.csv\s*# =+[\s\S]*?rd_api_data = \{\}'
m_rd = re.search(rd_block_pattern, code)

if m_rd:
    rd_code = m_rd.group(0)
    print("Found LogRD block!")

# Let's extract LogRD loading and place it right before students = []
# Specifically, we can load LogRD and build rd_course_hints and rd_events_map
rd_init_snippet = """    # ============================================
    # LEITURA LOGRD.CSV & DICAS DE CURSO
    # ============================================
    logrd_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\LogRD.csv'
    rd_events_map = {}
    rd_course_hints = {}
    
    if os.path.exists(logrd_path):
        df_rd = pd.read_csv(logrd_path, encoding='utf-8', low_memory=False)
        df_rd['email_lower'] = df_rd['Email'].astype(str).str.lower().str.strip()
        
        # Build hints and events for all rows
        ev_col_name = 'Eventos (Últimos 100)' if 'Eventos (Últimos 100)' in df_rd.columns else None
        for _, row in df_rd.iterrows():
            email_k = str(row['email_lower']).strip()
            if not email_k or email_k == 'nan': continue
            
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
                rd_course_hints[email_k] = normalize_curso('S.O.S ANTIBIÓTICO')
"""

# Place rd_init_snippet right before students = []
if "LEITURA LOGRD.CSV & DICAS DE CURSO" not in code:
    code = code.replace("    students = []\n    \n    df_acad =", rd_init_snippet + "\n    students = []\n    \n    df_acad =", 1)
    print("Placed LogRD init before students = []!")

# 2. Fix Vindi new students loop to avoid synthetic '___' emails
old_vindi_new_loop = """        # Add Vindi subscribers who don't have access logs yet (as inferred students)
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
                vindi_matched += 1"""

new_vindi_new_loop = """        # Add Vindi subscribers who don't have access logs yet (as inferred students)
        existing_vindi_keys = set((str(s.get('email', '')).lower().strip(), str(s.get('curso', '')).strip()) for s in students if s.get('email'))
        for em, v_obj in vindi_map.items():
            if '___' in em: continue # Skip composite dictionary keys
            em_clean = str(em).lower().strip()
            if not em_clean or not isinstance(v_obj, dict): continue
            
            c_inferido = v_obj.get('curso') or "PLATAFORMA GERAL"
            c_orig = "Plano Vindi"
            if c_inferido == "PLATAFORMA GERAL" and 'rd_course_hints' in locals() and em_clean in rd_course_hints:
                c_inferido = rd_course_hints[em_clean]
                c_orig = "RD Station"
                
            pair_key = (em_clean, c_inferido)
            if pair_key not in existing_vindi_keys:
                existing_vindi_keys.add(pair_key)
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
                vindi_matched += 1"""

if old_vindi_new_loop in code:
    code = code.replace(old_vindi_new_loop, new_vindi_new_loop, 1)
    print("Fixed Vindi new students loop!")

with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved gerador.py reorganization successfully!")

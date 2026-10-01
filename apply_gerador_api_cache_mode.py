import os, json, re

def update_gerador_to_apis_and_caches():
    for base_dir in ['c:/Users/DELL/Desktop/Dash_InfectoCast', 'c:/Users/DELL/Desktop/Acompanhamento de acessos']:
        fpath = os.path.join(base_dir, 'gerador.py')
        if not os.path.exists(fpath):
            continue
            
        with open(fpath, 'r', encoding='utf-8') as f:
            code = f.read()

        # 1. Replace the initial load of CURSOS.xlsx and Log de uso.xlsx
        old_init_target = """    cursos_path = get_bd_file('CURSOS.xlsx')
    log_uso_path = get_bd_file('Log de uso.xlsx')
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
    df_aulas = xls_cursos.parse(2)"""

        new_init_replacement = """    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')
    
    print("Carregando logs de uso da plataforma Academy (100% API & Cache)...")
    academy_cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'academy_logs_cache.json')
    log_records = []
    if os.path.exists(academy_cache_path):
        try:
            with open(academy_cache_path, 'r', encoding='utf-8') as f_l:
                acad_l = json.load(f_l)
                for item in acad_l:
                    log_records.append({
                        'Data log': pd.to_datetime(item.get('Data log'), errors='coerce'),
                        'Nome aluno': str(item.get('Nome aluno', '')).strip(),
                        'E-mail': str(item.get('E-mail', '')).lower().strip(),
                        'Ação / Local': item.get('Ação / Local', 'AÇÃO'),
                        'ID Item': item.get('ID Item', ''),
                        'Desc. Item': item.get('Desc. Item', ''),
                        'Plataforma': 'Academy'
                    })
        except Exception as e:
            print(f"[ACADEMY LOGS] Erro ao carregar cache de logs: {e}")

    df_log = pd.DataFrame(log_records) if log_records else pd.DataFrame(columns=['Data log', 'Nome aluno', 'E-mail', 'Ação / Local', 'ID Item', 'Desc. Item', 'Plataforma'])
    
    # Currículo 100% dinâmico via API / Cache da Academy
    curric_cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'academy_curriculum_cache.json')
    curric_data = {}
    if os.path.exists(curric_cache_path):
        with open(curric_cache_path, 'r', encoding='utf-8') as f_cur:
            curric_data = json.load(f_cur)
    else:
        try:
            from academy_service import AcademyService
            curric_data = AcademyService().get_curriculo_completo()
        except Exception:
            curric_data = {}

    mods_records = []
    aulas_records = []
    for c_name, m_list in curric_data.items():
        if not isinstance(m_list, list): continue
        for m in m_list:
            m_id = m.get('id_modulo')
            m_nome = m.get('modulo', '')
            mods_records.append({
                'Curso': c_name,
                'ID': m_id,
                'Modulo': m_nome,
                'Descricao': m_nome
            })
            for a in m.get('aulas', []):
                aulas_records.append({
                    'Curso': c_name,
                    'ID Modulo': m_id,
                    'ID Aula': a.get('id'),
                    'Nome Aula': a.get('nome'),
                    'Nome': a.get('nome')
                })

    df_mods = pd.DataFrame(mods_records) if mods_records else pd.DataFrame(columns=['Curso', 'ID', 'Modulo', 'Descricao'])
    df_aulas = pd.DataFrame(aulas_records) if aulas_records else pd.DataFrame(columns=['Curso', 'ID Modulo', 'ID Aula', 'Nome Aula', 'Nome'])"""

        if old_init_target in code:
            code = code.replace(old_init_target, new_init_replacement, 1)
            print(f"[{base_dir}] Replaced init target")
        else:
            print(f"[{base_dir}] Warning: old_init_target not found!")

        # 2. Replace df_mods iteration to handle both DataFrame columns and indices safely
        old_mod_iter = """    for _, row in df_mods.iterrows():
        m_curso = canonicalize_curso(str(row.iloc[0]).strip())
        m_id = row.iloc[1]
        m_nome = clean_module_name(row.iloc[3])
        mod_id_to_name[m_id] = m_nome
        mod_id_to_curso[m_id] = m_curso

    for _, row in df_aulas.iterrows():
        m_id = row.iloc[1]
        a_nome = str(row.iloc[4])
        a_norm = norm_title(a_nome)
        if m_id in mod_id_to_name and a_norm:
            m_nome = mod_id_to_name[m_id]
            m_curso = mod_id_to_curso.get(m_id, '')
            course_lesson_to_module[(m_curso, a_norm)] = m_nome"""

        new_mod_iter = """    for _, row in df_mods.iterrows():
        m_curso = canonicalize_curso(str(row.get('Curso', row.iloc[0] if len(row) > 0 else '')).strip())
        m_id = row.get('ID', row.iloc[1] if len(row) > 1 else '')
        m_nome = clean_module_name(row.get('Modulo', row.iloc[3] if len(row) > 3 else ''))
        mod_id_to_name[m_id] = m_nome
        mod_id_to_curso[m_id] = m_curso

    for _, row in df_aulas.iterrows():
        m_id = row.get('ID Modulo', row.iloc[1] if len(row) > 1 else '')
        a_nome = str(row.get('Nome Aula', row.iloc[4] if len(row) > 4 else ''))
        a_norm = norm_title(a_nome)
        if m_id in mod_id_to_name and a_norm:
            m_nome = mod_id_to_name[m_id]
            m_curso = mod_id_to_curso.get(m_id, '')
            course_lesson_to_module[(m_curso, a_norm)] = m_nome"""

        if old_mod_iter in code:
            code = code.replace(old_mod_iter, new_mod_iter, 1)
            print(f"[{base_dir}] Replaced mod iter")

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(code)
            
    print("gerador.py updated successfully!")

if __name__ == '__main__':
    update_gerador_to_apis_and_caches()

import os, json

def patch_gerador_cativa_telemetry_and_curriculum():
    for base_dir in ['c:/Users/DELL/Desktop/Dash_InfectoCast', 'c:/Users/DELL/Desktop/Acompanhamento de acessos']:
        fpath = os.path.join(base_dir, 'gerador.py')
        if not os.path.exists(fpath): continue

        with open(fpath, 'r', encoding='utf-8') as f:
            code = f.read()

        # Target block for loading logs and curriculum
        target_start = 'print("Carregando logs de uso da plataforma Academy (100% API & Cache)...")'
        target_end = 'df_aulas = pd.DataFrame(aulas_records) if aulas_records else pd.DataFrame(columns=[\'Curso\', \'ID Modulo\', \'ID Aula\', \'Nome Aula\', \'Nome\'])'

        idx_s = code.find(target_start)
        idx_e = code.find(target_end)

        if idx_s == -1 or idx_e == -1:
            print(f"[{base_dir}] Target block not found!")
            continue

        idx_e = idx_e + len(target_end)

        replacement = """print("Carregando logs de uso e telemetria (Academy API + Cativa API)...")
    academy_cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'academy_logs_cache.json')
    log_records = []
    
    # 1. Logs da Academy API
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
                        'Modulo': item.get('Modulo', 'Geral'),
                        'Curso': item.get('Curso', 'PLATAFORMA GERAL'),
                        'Plataforma': 'Academy'
                    })
        except Exception as e:
            print(f"[ACADEMY LOGS] Erro ao carregar cache de logs: {e}")

    # 2. Telemetria e Logs de Aulas da Cativa Digital API
    try:
        import cativa_api
        cativa_logs = cativa_api.get_cativa_telemetry_logs()
        log_records.extend(cativa_logs)
        print(f"[CATIVA LOGS] Integrados {len(cativa_logs)} eventos de telemetria da Cativa Digital.")
    except Exception as e_cat_log:
        print(f"[CATIVA LOGS] Erro ao carregar logs da Cativa: {e_cat_log}")

    df_log = pd.DataFrame(log_records) if log_records else pd.DataFrame(columns=['Data log', 'Nome aluno', 'E-mail', 'Ação / Local', 'ID Item', 'Desc. Item', 'Modulo', 'Curso', 'Plataforma'])
    
    # ============================================
    # CURRÍCULO UNIFICADO (Academy API + Cativa API)
    # ============================================
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

    # Integrar Currículo da Cativa API
    try:
        import cativa_api
        cativa_curric = cativa_api.get_cativa_curriculum()
        for c_cat_name, m_cat_list in cativa_curric.items():
            if c_cat_name not in curric_data:
                curric_data[c_cat_name] = m_cat_list
            else:
                existing_mod_names = set(m.get('modulo') for m in curric_data[c_cat_name])
                for m_c in m_cat_list:
                    if m_c.get('modulo') not in existing_mod_names:
                        curric_data[c_cat_name].append(m_c)
        print(f"[CATIVA CURRÍCULO] Integrados cursos e módulos da Cativa API.")
    except Exception as e_cat_cur:
        print(f"[CATIVA CURRÍCULO] Erro ao carregar currículo da Cativa: {e_cat_cur}")

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

        new_code = code[:idx_s] + replacement + code[idx_e:]
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"Patched {fpath} successfully!")

if __name__ == '__main__':
    patch_gerador_cativa_telemetry_and_curriculum()

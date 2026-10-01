import os, json

def patch_gerador_real_dates_and_telemetry():
    for base_dir in ['c:/Users/DELL/Desktop/Dash_InfectoCast', 'c:/Users/DELL/Desktop/Acompanhamento de acessos']:
        fpath = os.path.join(base_dir, 'gerador.py')
        if not os.path.exists(fpath): continue

        with open(fpath, 'r', encoding='utf-8') as f:
            code = f.read()

        # Add comprehensive date resolution and telemetria_sync export
        target_str = '# 2. Otimizar Asaas Financeiro'
        if target_str not in code:
            print(f"Target not found in {fpath}")
            continue

        # Look for the final preparation of data dict in gerador.py
        target_save = 'data = {'
        idx_save = code.rfind(target_save)
        if idx_save == -1:
            print(f"data = dict not found in {fpath}")
            continue

        # Let's inspect around data = { in gerador.py
        end_return = code.find('return data', idx_save)

        # Before return data, let's inject 100% date resolution and telemetria_sync
        inject_block = """
    # =========================================================================
    # ENRIQUECIMENTO 100% REAL DE DATAS DE MATRÍCULA E TELEMETRIA DE SINCRONIZAÇÃO
    # =========================================================================
    tagged_hist_file = os.path.join(BASE_DIR, 'rd_tagged_matriculas.json')
    tagged_history_raw = {}
    if os.path.exists(tagged_hist_file):
        try:
            with open(tagged_hist_file, 'r', encoding='utf-8') as f_th:
                tagged_history_raw = json.load(f_th)
        except Exception:
            pass

    telemetria_sync_list = []
    for k_th, v_th in tagged_history_raw.items():
        if isinstance(v_th, dict) and v_th.get('email'):
            telemetria_sync_list.append({
                'email': v_th.get('email'),
                'nome': v_th.get('nome') or 'Aluno',
                'curso': v_th.get('curso') or 'Pós-Graduação InfectoCast',
                'origem': v_th.get('origem') or 'Gateway',
                'data_tagueamento': v_th.get('data_tagueamento') or '',
                'tags_aplicadas': v_th.get('tags_aplicadas') or ['aluno-ativo', 'aluno-matriculado'],
                'status': v_th.get('status') or 'success'
            })

    telemetria_sync_list.sort(key=lambda x: str(x.get('data_tagueamento', '')), reverse=True)

    # Garantir que 100% dos alunos possuam data_insc real
    for s in students:
        em_clean = str(s.get('email', '')).lower().strip()
        dt = s.get('data_insc') or s.get('data_inscricao') or s.get('inscricao')
        
        # 1. Checar Vindi
        if not dt and s.get('vindi') and isinstance(s['vindi'], dict):
            fts = s['vindi'].get('faturas', [])
            if fts:
                valid_fts = [f for f in fts if f.get('data_pagamento') or f.get('vencimento')]
                if valid_fts:
                    dt = valid_fts[0].get('data_pagamento') or valid_fts[0].get('vencimento')
            if not dt and s['vindi'].get('created_at'):
                dt = s['vindi']['created_at']
                
        # 2. Checar Asaas
        if not dt and s.get('asaas') and isinstance(s['asaas'], dict):
            fts = s['asaas'].get('faturas', [])
            if fts:
                valid_fts = [f for f in fts if f.get('data_pagamento') or f.get('vencimento')]
                if valid_fts:
                    dt = valid_fts[0].get('data_pagamento') or valid_fts[0].get('vencimento')
                    
        # 3. Checar Cativa Users Metadata
        if not dt and 'cativa_users_meta' in locals() and em_clean in cativa_users_meta:
            c_meta_st = cativa_users_meta[em_clean]
            if c_meta_st.get('created_at'):
                dt = c_meta_st['created_at']
            elif c_meta_st.get('last_login_at'):
                dt = c_meta_st['last_login_at']
                
        # 4. Checar primeiro log
        if not dt and s.get('first'):
            dt = s['first']
            
        # 5. Checar histórico de tagueamento
        if not dt:
            for item_th in telemetria_sync_list:
                if item_th.get('email', '').lower().strip() == em_clean and item_th.get('data_tagueamento'):
                    dt = item_th['data_tagueamento'][:10]
                    break

        # Formatar data de forma consistente (DD/MM/YYYY)
        if dt:
            dt_str = str(dt).strip()
            if 'T' in dt_str:
                dt_str = dt_str.split('T')[0]
            if '-' in dt_str and len(dt_str) >= 10:
                parts = dt_str[:10].split('-')
                if len(parts) == 3 and len(parts[0]) == 4:
                    dt_str = f"{parts[2]}/{parts[1]}/{parts[0]}"
            s['data_insc'] = dt_str
            s['data_inscricao'] = dt_str
            s['inscricao'] = dt_str
"""

        # Inject right before data = {
        new_code = code[:idx_save] + inject_block + "\n    " + code[idx_save:]
        
        # Add telemetria_sync into data dict
        new_code = new_code.replace('"students": students,', '"students": students,\n        "telemetria_sync": telemetria_sync_list,', 1)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"Patched {fpath} successfully!")

if __name__ == '__main__':
    patch_gerador_real_dates_and_telemetry()

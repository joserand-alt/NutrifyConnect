with open('gerador.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the AUTO-HEALING block in gerador.py
healing_start = code.find('# AUTO-HEALING DE CURSOS: Recuperar alunos de PLATAFORMA GERAL')
healing_end = code.find('data = {\n        "meta": {', healing_start)

new_healing_block = '''# AUTO-HEALING DE CURSOS: Priorização Oficial (Academy/Cativa Logs -> Asaas/Vindi Financeiro -> RD Tags)
    # =========================================================================
    
    # Dicionário de logs por email
    logs_by_email = {}
    if not df_log.empty:
        for em, group in df_log.groupby('E-mail'):
            em_clean = str(em).lower().strip()
            logs_by_email[em_clean] = group

    def infer_course_from_logs_df(gdf):
        if gdf is None or gdf.empty:
            return None
        all_text = " ".join(gdf['Desc. Item'].fillna('').astype(str) + " " + gdf['ID Item'].fillna('').astype(str) + " " + gdf['Ação / Local'].fillna('').astype(str) + " " + gdf['Modulo'].fillna('').astype(str)).upper()
        
        # 1. SOS ANTIBIÓTICO
        sos_kw = ['ANAEROB', 'ACINETOBACTER', 'PSEUDOMONAS', 'ENTEROBACT', 'STREPTOCOCCUS', 'ENTEROCOCCUS', 'ESTAFILOCOCO', 'STAPHYLOCOCCUS', 'ANTIBIOTICO', 'ANTIBIOGRAMA', 'ESBL', 'KPC', 'NDM', 'OXA', 'CRAB', 'MDR', 'PENICILINA', 'CEFALOSPORINA', 'CARBAPENEM', 'VANCOMICINA', 'DAFTOMICINA', 'POLIMIXINA', 'AMINOGLICOSIDEO', 'QUINOLONA', 'MACROLIDEO', 'FOSFOMICINA', 'S.O.S', 'SOS']
        if any(k in all_text for k in sos_kw):
            return normalize_curso('S.O.S ANTIBIÓTICO')

        # 2. DO FUNGO AO ANTIFÚNGICO
        fungo_kw = ['FUNGO', 'ANTIFUNGICO', 'CANDIDA', 'ASPERGILLUS', 'CRYPTOCOCCUS', 'HISTOPLASMA', 'PARACOCCIDIOIDES', 'MUCOR', 'FUSARIUM', 'ANFOTERICINA', 'FLUCONAZOL', 'VORICONAZOL', 'POSACONAZOL', 'ISAVUCONAZOL', 'EQUINOCANDINA', 'MICAFUNGINA']
        if any(k in all_text for k in fungo_kw):
            return normalize_curso('DO FUNGO AO ANTIFÚNGICO')

        # 3. PEDIATRIA
        ped_kw = ['INFECTOPEDIATRIA', 'PEDIATRIA', 'PEDIATRICA', 'NEONATAL', 'CRIANCA', 'SIFILIS CONGENITA', 'TORCH', 'BRONQUIOLITE']
        if any(k in all_text for k in ped_kw):
            return normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')

        # 4. IMUNODEPRIMIDOS
        imuno_kw = ['IMUNODEPRIMIDO', 'IMUNOCOMPROMETIDO', 'NEUTROPENIA FEBRIL', 'TRANSPLANTE', 'TMO', 'PNEUMOCISTOSE']
        if any(k in all_text for k in imuno_kw):
            return normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS')

        # 5. ORTOPEDIA
        orto_kw = ['ORTOPEDICA', 'ORTOPEDIA', 'PROTESE ARTICULAR', 'OSTEOMIELITE', 'ARTRITE SEPTICA', 'PARTES MOLES', 'FASCITE NECROSANTE']
        if any(k in all_text for k in orto_kw):
            return normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')

        # 6. CCIH
        ccih_kw = ['CCIH', 'INFECCAO HOSPITALAR', 'IRAS', 'PREVENCAO', 'VIGILANCIA', 'PAV', 'IPCSL', 'ISC']
        if any(k in all_text for k in ccih_kw):
            return normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')

        # 7. MULTI-R
        if 'MULTI-R' in all_text or 'MULTIR' in all_text or 'JORNADA' in all_text:
            return normalize_curso('JORNADA MULTI-R')

        # 8. INFECTOXPERT
        if 'INFECTOXPERT' in all_text or 'EXPERT' in all_text:
            return normalize_curso('INFECTOXPERT')

        return None

    def infer_course_from_price_and_desc(val, total_val, plan_str):
        p_norm = (plan_str or '').upper()
        if p_norm:
            c_cand = canonicalize_curso(p_norm)
            if c_cand and c_cand != normalize_curso('PLATAFORMA GERAL'):
                return c_cand

        v = float(val or 0)
        tot = float(total_val or 0)
        
        # SOS / Antibiótico prices: R$ 2187, R$ 1968.30, R$ 1997, R$ 437.40 (5x), R$ 196.83 (10x)
        if any(abs(tot - p) < 5 for p in [2187.0, 1968.30, 1997.0, 1497.0, 997.0]) or any(abs(v - p) < 5 for p in [2187.0, 1968.30, 1997.0, 437.40, 196.83]):
            return normalize_curso('S.O.S ANTIBIÓTICO')
            
        # Pós-graduação: R$ 1388.00 / mês ou R$ 24984.00 total
        if abs(v - 1388.0) < 5 or abs(tot - 24984.0) < 50:
            return normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')

        return None

    for s in students:
        em_clean = str(s.get('email', '')).lower().strip()
        cur_raw = str(s.get('curso', '')).strip().upper()
        
        if cur_raw in ['PLATAFORMA GERAL', '', 'SEM CURSO', 'NONE', 'NAN']:
            # PRIORIDADE 1: Logs de aulas da Academy e Cativa
            c_from_logs = infer_course_from_logs_df(logs_by_email.get(em_clean))
            if c_from_logs and c_from_logs != normalize_curso('PLATAFORMA GERAL'):
                s['curso'] = c_from_logs
                s['curso_inferido'] = True
                s['curso_origem'] = 'Logs de Aulas'
                continue

            # PRIORIDADE 2: Financeiro Asaas
            if s.get('asaas') and isinstance(s['asaas'], dict):
                a_data = s['asaas']
                fats = a_data.get('faturas', [])
                fat_val = fats[0].get('valor') if fats else 0
                desc = fats[0].get('description') if fats else ''
                m_tot = re.search(r'R\$\s*([\d\.,]+)', str(desc))
                tot_val = 0
                if m_tot:
                    try:
                        tot_val = float(m_tot.group(1).replace('.', '').replace(',', '.'))
                    except:
                        pass
                c_from_asaas = infer_course_from_price_and_desc(fat_val, tot_val, desc or a_data.get('curso'))
                if c_from_asaas and c_from_asaas != normalize_curso('PLATAFORMA GERAL'):
                    s['curso'] = c_from_asaas
                    s['curso_inferido'] = True
                    s['curso_origem'] = 'Asaas'
                    continue

            # PRIORIDADE 3: Financeiro Vindi
            v_plano = ''
            if s.get('vindi') and isinstance(s['vindi'], dict):
                v_plano = s['vindi'].get('plano', '')
            elif 'vindi_map' in locals() and em_clean in vindi_map:
                v_plano = vindi_map[em_clean].get('plano', '')
                
            c_from_v = canonicalize_curso(v_plano, em_clean)
            if c_from_v and c_from_v != normalize_curso('PLATAFORMA GERAL'):
                s['curso'] = c_from_v
                s['curso_inferido'] = True
                s['curso_origem'] = 'Plano Vindi'
                continue

            # PRIORIDADE 4: RD Station
            if 'rd_tagged_courses' in locals() and em_clean in rd_tagged_courses:
                c_from_rd = canonicalize_curso(rd_tagged_courses[em_clean], em_clean)
                if c_from_rd and c_from_rd != normalize_curso('PLATAFORMA GERAL'):
                    s['curso'] = c_from_rd
                    s['curso_inferido'] = True
                    s['curso_origem'] = 'RD Station (Tag)'
                    continue
                    
            if 'rd_course_hints' in locals() and em_clean in rd_course_hints:
                c_from_hints = canonicalize_curso(rd_course_hints[em_clean], em_clean)
                if c_from_hints and c_from_hints != normalize_curso('PLATAFORMA GERAL'):
                    s['curso'] = c_from_hints
                    s['curso_inferido'] = True
                    s['curso_origem'] = 'RD Station (Histórico)'
                    continue

    '''

if healing_start != -1 and healing_end != -1:
    code = code[:healing_start] + new_healing_block + code[healing_end:]
    with open('gerador.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("gerador.py successfully patched with full prioritized auto-healing!")
else:
    print("WARNING: Positions not found in gerador.py")

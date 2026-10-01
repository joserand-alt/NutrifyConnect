import os

target_paths = [
    r"c:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py",
    r"c:\Users\DELL\Desktop\Acompanhamento de acessos\gerador.py"
]

old_block = """        for key, asaas_st in asaas_map.items():
            if not isinstance(asaas_st, dict): continue
            # S\u00f3 considera como matriculado vindo da API se tiver ao menos um pagamento
            if (asaas_st.get('total_pago') or 0) <= 0:
                continue
            st_email = (asaas_st.get('customer_email') or '').lower().strip()
            if st_email and st_email not in existing_emails:
                existing_emails.add(st_email)
                curso_resolved, curso_inferido, curso_origem = _infer_curso_from_asaas(asaas_st, st_email)
                new_st = {
                    "email": st_email,
                    "nome": asaas_st.get('customer_name') or 'Aluno Academy',
                    "curso": curso_resolved,
                    "curso_inferido": curso_inferido,
                    "curso_origem": curso_origem,
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
                students.append(new_st)
                if curso_resolved != "PLATAFORMA GERAL":
                    tag_info = f" (INFERIDO via {curso_origem})" if curso_inferido else ""
                    print(f"  [ASAAS] Curso resolvido para {st_email}: {curso_resolved}{tag_info}")
                added_from_api += 1
                asaas_matched += 1"""

new_block = """        for key, asaas_st in asaas_map.items():
            if not isinstance(asaas_st, dict): continue
            st_email = (asaas_st.get('customer_email') or '').lower().strip()
            if not st_email or st_email in existing_emails:
                continue
            
            tot_pago = float(asaas_st.get('total_pago') or 0)
            faturas = asaas_st.get('faturas', [])
            if tot_pago <= 0 and not faturas:
                continue

            existing_emails.add(st_email)
            curso_resolved, curso_inferido, curso_origem = _infer_curso_from_asaas(asaas_st, st_email)
            
            # Data de inscricao/fatura
            dt_insc_str = None
            if faturas:
                f0 = faturas[0]
                dt_insc_str = f0.get('data_criacao') or f0.get('dateCreated') or f0.get('data_pagamento_iso') or f0.get('vencimento_iso')
            
            is_pending = (tot_pago <= 0)
            st_nome = asaas_st.get('customer_name') or ('Lead / Inscrição Academy' if is_pending else 'Aluno Academy')
            
            new_st = {
                "email": st_email,
                "nome": st_nome,
                "curso": curso_resolved,
                "curso_inferido": curso_inferido,
                "curso_origem": curso_origem,
                "telefone": "",
                "acessou": False,
                "data_insc": dt_insc_str,
                "data_inscricao": dt_insc_str,
                "inscricao": dt_insc_str,
                "dias_desde_insc": 0,
                "plataforma": "Academy",
                "id_aluno": str(asaas_st.get('aluno_id_extref', '')),
                "status": "Matrícula Pendente" if is_pending else "Em Andamento",
                "events": [],
                "vindi": None,
                "asaas": asaas_st
            }
            if 'rd_events_map' in locals() and st_email in rd_events_map:
                new_st['rd_funnel'] = dict(rd_events_map[st_email])
            students.append(new_st)
            if curso_resolved != "PLATAFORMA GERAL":
                tag_info = f" (INFERIDO via {curso_origem})" if curso_inferido else ""
                print(f"  [ASAAS] Curso resolvido para {st_email}: {curso_resolved}{tag_info}")
            added_from_api += 1
            asaas_matched += 1"""

for target_path in target_paths:
    if os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Try replacing or fuzzy search
        if 'for key, asaas_st in asaas_map.items():' in content:
            import re
            content_new = re.sub(
                r'for key, asaas_st in asaas_map\.items\(\):.*?asaas_matched \+= 1',
                new_block.strip(),
                content,
                flags=re.DOTALL
            )
            # Also add enrichment for missing data_insc
            enrich_block = '''
    for s in students:
        s.setdefault('curso_inferido', False)
        s.setdefault('curso_origem', 'Oficial')
        if not s.get('data_insc') and not s.get('data_inscricao'):
            if s.get('asaas') and s['asaas'].get('faturas'):
                f0 = s['asaas']['faturas'][0]
                d_found = f0.get('data_criacao') or f0.get('dateCreated') or f0.get('data_pagamento_iso') or f0.get('vencimento_iso')
                if d_found:
                    s['data_insc'] = d_found
                    s['data_inscricao'] = d_found
                    s['inscricao'] = d_found
            elif s.get('vindi') and s['vindi'].get('faturas'):
                f0 = s['vindi']['faturas'][0]
                d_found = f0.get('data_pagamento_iso') or f0.get('vencimento_iso')
                if d_found:
                    s['data_insc'] = d_found
                    s['data_inscricao'] = d_found
                    s['inscricao'] = d_found
'''
            target_default = "    for s in students:\n        s.setdefault('curso_inferido', False)\n        s.setdefault('curso_origem', 'Oficial')"
            if target_default in content_new:
                content_new = content_new.replace(target_default, enrich_block.strip(), 1)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content_new)
            print(f"Patched {target_path} successfully!")
        else:
            print(f"Pattern not found in {target_path}")

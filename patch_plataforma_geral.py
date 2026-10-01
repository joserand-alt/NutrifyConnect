"""
Patch: Resolver curso de alunos Asaas 'PLATAFORMA GERAL'
=========================================================
Quando alunos são adicionados pela integração Asaas/Academy API e não estão
na planilha de inscrições nem nos logs, o curso ficava como 'PLATAFORMA GERAL'.

Correção: Usa o student_course_map (montado dos logs + planilhas) e, como
fallback, infere o curso a partir do valor da parcela ou descrição do pagamento.
"""

template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The block that adds students from Asaas (line ~1368-1396)
old_block = '''        # 2. Adicionar alunos do Asaas/Academy API que ainda não estavam na lista de estudantes
        existing_emails = set(str(s.get('email', '')).lower().strip() for s in students if s.get('email'))
        added_from_api = 0
        for key, asaas_st in asaas_map.items():
            if not isinstance(asaas_st, dict): continue
            # Só considera como matriculado vindo da API se tiver ao menos um pagamento
            if (asaas_st.get('total_pago') or 0) <= 0:
                continue
            st_email = (asaas_st.get('customer_email') or '').lower().strip()
            if st_email and st_email not in existing_emails:
                existing_emails.add(st_email)
                students.append({
                    "email": st_email,
                    "nome": asaas_st.get('customer_name') or 'Aluno Academy',
                    "curso": "PLATAFORMA GERAL",
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
                })
                added_from_api += 1
                asaas_matched += 1'''

new_block = '''        # 2. Adicionar alunos do Asaas/Academy API que ainda não estavam na lista de estudantes
        existing_emails = set(str(s.get('email', '')).lower().strip() for s in students if s.get('email'))
        added_from_api = 0

        def _infer_curso_from_asaas(asaas_st, email):
            """Tenta resolver o curso do aluno Asaas usando student_course_map ou valor do plano."""
            # 1. Verifica student_course_map (logs + planilhas)
            if email in student_course_map:
                return student_course_map[email]
            
            # 2. Infere pelo valor total do plano (padrão de preços dos cursos)
            total = asaas_st.get('total_bruto') or 0
            if total <= 0:
                # Calcula total bruto a partir das faturas
                faturas = asaas_st.get('faturas', [])
                if faturas:
                    total = sum(f.get('valor', 0) for f in faturas)
            
            # 3. Tenta pela descrição do pagamento
            faturas = asaas_st.get('faturas', [])
            desc_text = ''
            for ft in faturas:
                d = ft.get('description', ft.get('descricao', ''))
                if d and d != 'N/A':
                    desc_text += ' ' + str(d).upper()
            
            desc_norm = desc_text.replace('Ã', 'A').replace('Ç', 'C').replace('Ó', 'O').replace('É', 'E').replace('Í', 'I')
            
            if any(w in desc_norm for w in ['CCIH', 'INFECCAO HOSPITALAR', 'PREVENCAO']):
                return normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')
            if any(w in desc_norm for w in ['INFECTOPED', 'PEDIATRIA']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')
            if any(w in desc_norm for w in ['ORTOPED', 'PARTES MOLES']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')
            if any(w in desc_norm for w in ['SOS', 'ANTIBIOTICO', 'ATB']):
                return normalize_curso('S.O.S ANTIBIÓTICO')
            if any(w in desc_norm for w in ['FERRAMENTA', 'QUALIDADE']):
                return normalize_curso('FERRAMENTAS DE QUALIDADE')
            if any(w in desc_norm for w in ['IMUNODEPRIMIDO']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS')
            
            # 4. Infere pelo valor total (preços conhecidos dos cursos)
            # Cursos de pós-graduação: ~R$2.187 (total)
            # SOS ATB: ~R$487 (total)
            # Ferramentas: valores menores
            # Não é possível distinguir apenas pelo valor qual pós-graduação
            
            return "PLATAFORMA GERAL"

        for key, asaas_st in asaas_map.items():
            if not isinstance(asaas_st, dict): continue
            # Só considera como matriculado vindo da API se tiver ao menos um pagamento
            if (asaas_st.get('total_pago') or 0) <= 0:
                continue
            st_email = (asaas_st.get('customer_email') or '').lower().strip()
            if st_email and st_email not in existing_emails:
                existing_emails.add(st_email)
                curso_resolved = _infer_curso_from_asaas(asaas_st, st_email)
                students.append({
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
                })
                if curso_resolved != "PLATAFORMA GERAL":
                    print(f"  [ASAAS] Curso resolvido para {st_email}: {curso_resolved}")
                added_from_api += 1
                asaas_matched += 1'''

if old_block in content:
    content = content.replace(old_block, new_block)
    print("PATCH aplicado com sucesso!")
else:
    print("BLOCO NÃO ENCONTRADO - tentando variação...")
    # Try to find it with encoded chars
    if 'PLATAFORMA GERAL' in content and 'added_from_api' in content:
        print("Markers found, checking encoding issues...")
        # Look at the actual bytes around the area
        idx = content.index("# 2. Adicionar alunos do Asaas")
        print(f"Found at index {idx}")
        snippet = content[idx:idx+200]
        print(f"Snippet: {repr(snippet[:200])}")

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("gerador.py salvo!")

import os
import re

gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'

with open(gerador_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Vindi subscriber addition to skip cancelled with 0 payments
old_vindi_add = """        # Add Vindi subscribers who don't have access logs yet (as inferred students)
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
                existing_vindi_keys.add(pair_key)"""

new_vindi_add = """        # Add Vindi subscribers who don't have access logs yet (as inferred students)
        existing_vindi_keys = set((str(s.get('email', '')).lower().strip(), str(s.get('curso', '')).strip()) for s in students if s.get('email'))
        for em, v_obj in vindi_map.items():
            if '___' in em: continue # Skip composite dictionary keys
            em_clean = str(em).lower().strip()
            if not em_clean or not isinstance(v_obj, dict): continue
            
            # Cadastro != Matrícula: se foi cancelado sem pagamento e sem acesso, descarta
            v_sub_st = str(v_obj.get('status_assinatura', '')).lower()
            v_fin_st = str(v_obj.get('status_financeiro', '')).lower()
            fats = v_obj.get('faturas', [])
            has_paid = any(f.get('status') in ['paid', 'pago'] for f in fats)
            if v_sub_st in ['canceled', 'inactive'] and v_fin_st == 'cancelado' and not has_paid:
                continue
            
            c_inferido = v_obj.get('curso') or "PLATAFORMA GERAL"
            c_orig = "Plano Vindi"
            if c_inferido == "PLATAFORMA GERAL" and 'rd_course_hints' in locals() and em_clean in rd_course_hints:
                c_inferido = rd_course_hints[em_clean]
                c_orig = "RD Station"
                
            c_inferido = canonicalize_curso(c_inferido, em_clean)
            pair_key = (em_clean, c_inferido)
            if pair_key not in existing_vindi_keys:
                existing_vindi_keys.add(pair_key)"""

if old_vindi_add in code:
    code = code.replace(old_vindi_add, new_vindi_add)
    print("Updated Vindi subscriber addition!")
else:
    print("Could not find exact old_vindi_add pattern.")

# 2. Update _infer_curso_from_asaas
old_asaas_infer = """        def _infer_curso_from_asaas(asaas_st, email):
            \"\"\"Tenta resolver o curso do aluno Asaas usando student_course_map, RD Station ou descrio da fatura.
            Retorna: (curso_nome, is_inferred, origem_str)\"\"\"
            # 1. Verifica student_course_map (logs + planilhas) -> OFICIAL (no inferido)
            if email in student_course_map:
                return student_course_map[email], False, "Oficial"
            
            # 2. Verifica dicas do RD Station (Tags e Eventos de Leads) -> INFERIDO
            if 'rd_course_hints' in locals() and email in rd_course_hints:
                return rd_course_hints[email], True, "RD Station"
            
            # 3. Tenta pela descrio do pagamento
            faturas = asaas_st.get('faturas', [])
            desc_text = ''
            for ft in faturas:
                d = ft.get('description', ft.get('descricao', ''))
                if d and d != 'N/A':
                    desc_text += ' ' + str(d).upper()
            
            desc_norm = desc_text.replace('', 'A').replace('', 'C').replace('', 'O').replace('', 'E').replace('', 'I')
            
            if any(w in desc_norm for w in ['CCIH', 'INFECCAO HOSPITALAR', 'PREVENCAO']):
                return normalize_curso('PS-GRADUAO EM PREVENO E CONTROLE DE INFECO HOSPITALAR (CCIH)'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['INFECTOPED', 'PEDIATRIA']):
                return normalize_curso('PS-GRADUAO EM INFECTOPEDIATRIA'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['ORTOPED', 'PARTES MOLES']):
                return normalize_curso('PS-GRADUAO EM INFECES ORTOPDICAS E DE PARTES MOLES'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['SOS', 'ANTIBIOTICO', 'ATB']):
                return normalize_curso('S.O.S ANTIBITICO'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['FERRAMENTA', 'QUALIDADE']):
                return normalize_curso('FERRAMENTAS DE QUALIDADE'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['IMUNODEPRIMIDO']):
                return normalize_curso('PS-GRADUAO EM INFECES EM IMUNODEPRIMIDOS'), True, "Fatura Asaas"
            
            return "PLATAFORMA GERAL", False, "Geral" """

new_asaas_infer = """        def _infer_curso_from_asaas(asaas_st, email):
            \"\"\"Tenta resolver o curso do aluno Asaas usando student_course_map, RD Station ou descrição da fatura.
            Retorna: (curso_nome, is_inferred, origem_str)\"\"\"
            if email in student_course_map and student_course_map[email] != normalize_curso('PLATAFORMA GERAL'):
                return student_course_map[email], False, "Oficial"
            
            if 'rd_course_hints' in locals() and email in rd_course_hints:
                return rd_course_hints[email], True, "RD Station"
            
            faturas = asaas_st.get('faturas', [])
            desc_text = ' '.join(str(ft.get('description', ft.get('descricao', ''))) for ft in faturas)
            c_res = canonicalize_curso(desc_text, email)
            if c_res and c_res != normalize_curso('PLATAFORMA GERAL'):
                return c_res, True, "Fatura Asaas"
            
            return normalize_curso('PLATAFORMA GERAL'), False, "Geral" """

pattern_asaas = r'(\s+def _infer_curso_from_asaas\(asaas_st, email\):.*?return ["\']PLATAFORMA GERAL["\'], False, ["\']Geral["\'])'
match_asaas = re.search(pattern_asaas, code, re.DOTALL)
if match_asaas:
    code = code[:match_asaas.start()] + '\n' + new_asaas_infer + code[match_asaas.end():]
    print("Updated _infer_curso_from_asaas!")
else:
    print("Could not find _infer_curso_from_asaas pattern with regex.")

with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Gerador.py updated successfully.")

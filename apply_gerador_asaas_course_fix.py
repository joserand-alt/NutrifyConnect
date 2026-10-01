import os, json

def patch_gerador():
    for base in ['c:/Users/DELL/Desktop/Dash_InfectoCast', 'c:/Users/DELL/Desktop/Acompanhamento de acessos']:
        fpath = os.path.join(base, 'gerador.py')
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            code = f.read()

        target = "def _infer_curso_from_asaas(asaas_st, email):"
        if target not in code:
            print(f"Target not found in {fpath}")
            continue

        # Look for the block
        idx = code.find(target)
        # find the start of the indentation
        start_idx = code.rfind('\n', 0, idx) + 1
        end_idx = code.find('return normalize_curso(\'PLATAFORMA GERAL\'), False, "Geral"', idx)
        if end_idx == -1:
            print("End of block not found")
            continue
        end_idx = code.find('\n', end_idx)

        replacement = """        tagged_hist_file = os.path.join(BASE_DIR, 'rd_tagged_matriculas.json')
        rd_tagged_courses = {}
        if os.path.exists(tagged_hist_file):
            try:
                with open(tagged_hist_file, 'r', encoding='utf-8') as f_th:
                    t_data = json.load(f_th)
                    for k, v in t_data.items():
                        if isinstance(v, dict) and v.get('email') and v.get('curso'):
                            rd_tagged_courses[v['email'].lower().strip()] = normalize_curso(v['curso'])
            except Exception:
                pass

        def _infer_curso_from_asaas(asaas_st, email):
            \"\"\"Tenta resolver o curso do aluno Asaas usando student_course_map, RD Station, preço ou descrição da fatura.
            Retorna: (curso_nome, is_inferred, origem_str)\"\"\"
            if email in student_course_map and student_course_map[email] != normalize_curso('PLATAFORMA GERAL'):
                return student_course_map[email], False, "Oficial"
            
            if email in rd_tagged_courses:
                return rd_tagged_courses[email], False, "RD Station (Matrícula)"

            if 'rd_course_hints' in locals() and email in rd_course_hints:
                return rd_course_hints[email], True, "RD Station"
            
            faturas = asaas_st.get('faturas', [])
            desc_text = ' '.join(str(ft.get('description', ft.get('descricao', ''))) for ft in faturas)
            c_res = canonicalize_curso(desc_text, email)
            if c_res and c_res != normalize_curso('PLATAFORMA GERAL'):
                return c_res, True, "Fatura Asaas"

            # Detecção por preço / produto oficial
            tot_pago = float(asaas_st.get('total_pago') or 0)
            if abs(tot_pago - 487.0) < 5 or any(abs(float(ft.get('valor') or 0) - 487.0) < 5 for ft in faturas):
                return normalize_curso('S.O.S ANTIBIÓTICO'), True, "Preço Asaas (R$ 487,00)"
            
            return normalize_curso('PLATAFORMA GERAL'), False, "Geral" """

        new_code = code[:start_idx] + replacement + code[end_idx:]
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"Patched {fpath} successfully!")

if __name__ == '__main__':
    patch_gerador()

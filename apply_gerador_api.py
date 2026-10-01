gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'

with open(gerador_path, 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = "    # ASAAS FINANCEIRO"
end_marker = "    data = {"

start_idx = text.find(start_marker)
end_idx = text.find(end_marker, start_idx)

new_block = """    # ASAAS FINANCEIRO — 100% via API (Asaas + Academy API)
    # ============================================
    asaas_matched = 0
    asaas_financeiro = {}
    try:
        from asaas_service import get_asaas_data
        asaas_res = get_asaas_data(force_reload=True)
        asaas_map = asaas_res.get('data', {}) if isinstance(asaas_res, dict) else {}
        asaas_financeiro = asaas_res.get('financeiro', {}) if isinstance(asaas_res, dict) else {}

        # 1. Vincular aos estudantes existentes por e-mail (resolvido 100% pela API) ou ID
        for s in students:
            em = str(s.get('email', '')).lower().strip()
            aluno_id = str(s.get('id_aluno', '')).strip()
            matched = False
            if em and em in asaas_map:
                s['asaas'] = asaas_map[em]
                asaas_matched += 1
                matched = True
            elif aluno_id and aluno_id in asaas_map:
                s['asaas'] = asaas_map[aluno_id]
                asaas_matched += 1
                matched = True
            if not matched:
                s['asaas'] = None

        # 2. Adicionar alunos do Asaas/Academy API que ainda não estavam na lista de estudantes
        existing_emails = set(str(s.get('email', '')).lower().strip() for s in students if s.get('email'))
        added_from_api = 0
        for key, asaas_st in asaas_map.items():
            if not isinstance(asaas_st, dict): continue
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
                asaas_matched += 1

        print(f"[ASAAS] {asaas_matched} estudantes vinculados 100% via API ({added_from_api} matriculados adicionados da API Academy).")
    except Exception as e_asaas:
        print(f"[ASAAS] Erro ao integrar Asaas no gerador: {e_asaas}")
        for s in students:
            s['asaas'] = None

"""

text = text[:start_idx] + new_block + text[end_idx:]
with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("gerador.py updated with API-only matching!")

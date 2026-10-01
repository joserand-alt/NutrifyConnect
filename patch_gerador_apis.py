import sys

fp = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'
with open(fp, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Ensure User-Agent is in fetch_student_logs
old_req = "req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'})"
new_req = "req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})"
if old_req in code:
    code = code.replace(old_req, new_req, 1)

# 2. Update Academy loading and Cativa force_refresh
target_block = """    # 1. Integração com logs em tempo real da API InfectoCast Academy
    academy_cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'academy_logs_cache.json')
    academy_api_logs = []
    if os.path.exists(academy_cache_path):
        try:
            with open(academy_cache_path, 'r', encoding='utf-8') as f:
                acad_data = json.load(f)
                for item in acad_data:
                    academy_api_logs.append({
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
            print(f"[ACADEMY API] Carregados {len(academy_api_logs)} logs em tempo real do Academy.")
        except Exception as e:
            print(f"[ACADEMY API] Erro lendo cache de logs: {e}")

    if academy_api_logs:
        df_acad_api = pd.DataFrame(academy_api_logs)
        df_log = pd.concat([df_log, df_acad_api], ignore_index=True)

    df_log['Plataforma'] = df_log['Plataforma'].fillna('Academy')

    # 2. Integração com logs e alunos em tempo real da Cativa Digital
    import cativa_api
    cativa_data = cativa_api.fetch_all_cativa_data(force_refresh=False)"""

replacement_block = """    # 1. Integração com logs em tempo real da API InfectoCast Academy
    academy_cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'academy_logs_cache.json')
    academy_api_logs = []
    
    inscricoes_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\Inscrições.xlsx'
    if os.path.exists(inscricoes_path):
        try:
            df_insc = pd.read_excel(inscricoes_path)
            df_acad_live = fetch_logs_from_api(df_insc)
            if not df_acad_live.empty:
                for _, row in df_acad_live.iterrows():
                    academy_api_logs.append({
                        'Data log': pd.to_datetime(row['Data log'], errors='coerce'),
                        'Nome aluno': str(row.get('Nome aluno', '')).strip(),
                        'E-mail': str(row.get('E-mail', '')).lower().strip(),
                        'Ação / Local': row.get('Ação / Local', 'AÇÃO'),
                        'ID Item': row.get('ID Item', ''),
                        'Desc. Item': row.get('Desc. Item', ''),
                        'Modulo': 'Geral',
                        'Curso': 'PLATAFORMA GERAL',
                        'Plataforma': 'Academy'
                    })
                with open(academy_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(df_acad_live.to_dict(orient='records'), f, default=str, ensure_ascii=False)
                print(f"[ACADEMY API] Consultados {len(academy_api_logs)} logs ao vivo diretamente da API InfectoCast Academy.")
        except Exception as e:
            print(f"[ACADEMY API] Erro ao consultar API ao vivo: {e}")

    if not academy_api_logs and os.path.exists(academy_cache_path):
        try:
            with open(academy_cache_path, 'r', encoding='utf-8') as f:
                acad_data = json.load(f)
                for item in acad_data:
                    academy_api_logs.append({
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
            print(f"[ACADEMY API] Carregados {len(academy_api_logs)} logs de backup do cache local.")
        except Exception as e:
            print(f"[ACADEMY API] Erro lendo cache de logs: {e}")

    if academy_api_logs:
        df_acad_api = pd.DataFrame(academy_api_logs)
        df_log = pd.concat([df_log, df_acad_api], ignore_index=True)

    df_log['Plataforma'] = df_log['Plataforma'].fillna('Academy')

    # 2. Integração com logs e alunos em tempo real da Cativa Digital (forçando consulta ao vivo da API)
    import cativa_api
    cativa_data = cativa_api.fetch_all_cativa_data(force_refresh=True)"""

assert target_block in code, "Target block not found in gerador.py!"
code = code.replace(target_block, replacement_block, 1)

with open(fp, 'w', encoding='utf-8') as f:
    f.write(code)

print("gerador.py successfully patched to query Academy and Cativa live APIs!")

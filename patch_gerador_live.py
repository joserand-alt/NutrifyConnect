import sys
import re

with open('C:/Users/DELL/Desktop/Dash_InfectoCast/gerador.py', 'r', encoding='utf-8-sig') as f:
    text = f.read()

# Replace cativa and academy loading section in gerador.py
target_pattern = """    # Integração com logs e alunos da Cativa Digital
    df_log['Plataforma'] = 'Academy'
    import cativa_api
    cativa_data = cativa_api.fetch_all_cativa_data(force_refresh=False)
    cativa_users_meta = cativa_data.get('users_metadata', {})
    cativa_students = cativa_data.get('students', [])
    cativa_logs = []

    for s in cativa_students:
        em = str(s.get('email', '')).lower().strip()
        nome = str(s.get('fullName', '')).strip()
        for c in s.get('courses', []):
            c_canon = canonicalize_curso(c.get('courseName', ''))
            for l in c.get('lessons', []):
                dt_s = l.get('watchedAt', '')[:19]
                dt_val = pd.to_datetime(dt_s, errors='coerce')
                lesson_name = str(l.get('lessonName', '')).strip()
                mod_name = str(l.get('moduleName', '')).strip() or 'Geral'
                cativa_logs.append({
                    'Data log': dt_val,
                    'Nome aluno': nome,
                    'E-mail': em,
                    'Ação / Local': 'CONCLUIU AULA',
                    'ID Item': lesson_name,
                    'Desc. Item': lesson_name,
                    'Modulo': mod_name,
                    'Curso': c_canon,
                    'Plataforma': 'Cativa'
                })

    df_cativa_logs = pd.DataFrame(cativa_logs)
    print(f"Total de {len(df_cativa_logs)} registros de logs carregados via API Cativa Digital.")
    df_log = pd.concat([df_log, df_cativa_logs], ignore_index=True)
    if not df_log['Data log'].dropna().empty:
        hoje = df_log['Data log'].max().date() + datetime.timedelta(days=1)"""

replacement = """    # 1. Integração com logs em tempo real da API InfectoCast Academy
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
    cativa_data = cativa_api.fetch_all_cativa_data(force_refresh=False)
    cativa_users_meta = cativa_data.get('users_metadata', {})
    cativa_students = cativa_data.get('students', [])
    cativa_logs = []

    for s in cativa_students:
        em = str(s.get('email', '')).lower().strip()
        nome = str(s.get('fullName', '')).strip()
        for c in s.get('courses', []):
            c_canon = canonicalize_curso(c.get('courseName', ''))
            for l in c.get('lessons', []):
                dt_s = l.get('watchedAt', '')[:19]
                dt_val = pd.to_datetime(dt_s, errors='coerce')
                lesson_name = str(l.get('lessonName', '')).strip()
                mod_name = str(l.get('moduleName', '')).strip() or 'Geral'
                cativa_logs.append({
                    'Data log': dt_val,
                    'Nome aluno': nome,
                    'E-mail': em,
                    'Ação / Local': 'CONCLUIU AULA',
                    'ID Item': lesson_name,
                    'Desc. Item': lesson_name,
                    'Modulo': mod_name,
                    'Curso': c_canon,
                    'Plataforma': 'Cativa'
                })

    # Adicionar acessos/logins da Cativa de users_metadata
    for em, meta in cativa_users_meta.items():
        last_log = meta.get('last_login_at')
        if last_log:
            dt_val = pd.to_datetime(last_log[:19], errors='coerce')
            first_n = meta.get('first_name') or ''
            last_n = meta.get('last_name') or ''
            full_n = f"{first_n} {last_n}".strip() or em
            cativa_logs.append({
                'Data log': dt_val,
                'Nome aluno': full_n,
                'E-mail': em.lower().strip(),
                'Ação / Local': 'LOGIN WEB',
                'ID Item': 'Ambiente de Aprendizagem Cativa',
                'Desc. Item': 'Acesso Web à Plataforma Cativa',
                'Modulo': 'Geral',
                'Curso': 'PLATAFORMA GERAL',
                'Plataforma': 'Cativa'
            })

    df_cativa_logs = pd.DataFrame(cativa_logs)
    print(f"Total de {len(df_cativa_logs)} registros de logs (aulas + logins) carregados da Cativa Digital.")
    df_log = pd.concat([df_log, df_cativa_logs], ignore_index=True)
    
    # Garantir ordenação temporal e data de hoje oficial
    df_log = df_log.dropna(subset=['Data log']).sort_values('Data log')
    hoje = datetime.date.today()"""

assert target_pattern in text, "Target pattern not found in gerador.py!"
text = text.replace(target_pattern, replacement)

with open('C:/Users/DELL/Desktop/Dash_InfectoCast/gerador.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('gerador.py updated successfully with live Academy and Cativa logs!')

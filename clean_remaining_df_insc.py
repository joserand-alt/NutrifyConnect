import sys, re

gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'
with open(gerador_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Fix fetch_logs_from_api definition
old_fetch = """def fetch_logs_from_api(df_insc):
    print("Buscando logs de uso via API InfectoCast Academy (substituindo planilha)...")
    token = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'
    students = df_insc[['ID Aluno', 'Aluno', 'E-mail']].dropna(subset=['ID Aluno']).drop_duplicates(subset=['ID Aluno'])"""

new_fetch = """def fetch_logs_from_api(students_df=None):
    print("Buscando logs de uso via API InfectoCast Academy...")
    token = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'
    if students_df is None or students_df.empty:
        return pd.DataFrame(columns=['Data log', 'Nome aluno', 'E-mail', 'Ação / Local', 'ID Item', 'Desc. Item'])
    students = students_df[['ID Aluno', 'Aluno', 'E-mail']].dropna(subset=['ID Aluno']).drop_duplicates(subset=['ID Aluno'])"""

if old_fetch in code:
    code = code.replace(old_fetch, new_fetch, 1)
    print("Fixed fetch_logs_from_api!")

# 2. Fix line 906
old_insc_dates = """        # Cruzar com data de inscrição
        insc_dates = {}
        for _, row in df_insc.dropna(subset=['E-mail']).iterrows():
            em = str(row['E-mail']).lower().strip()
            dt = row['Data Inscrição']
            if pd.notna(dt):
                if em not in insc_dates or dt < insc_dates[em]:
                    insc_dates[em] = dt
        for s in cativa_students:
            em = str(s.get('email', '')).lower().strip()
            dt_raw = s.get('data_insc') or s.get('data_inscricao') or s.get('inscricao')
            if em and dt_raw:
                try:
                    dt = pd.to_datetime(dt_raw, dayfirst=True)
                    if em not in insc_dates or dt < insc_dates[em]:
                        insc_dates[em] = dt
                except Exception:
                    pass"""

new_insc_dates = """        # Cruzar com data de inscrição
        insc_dates = {}
        for s in students:
            em = str(s.get('email', '')).lower().strip()
            dt_raw = s.get('data_insc') or s.get('data_inscricao') or s.get('inscricao')
            if em and dt_raw:
                try:
                    dt = pd.to_datetime(dt_raw, dayfirst=True)
                    if em not in insc_dates or dt < insc_dates[em]:
                        insc_dates[em] = dt
                except Exception:
                    pass"""

if old_insc_dates in code:
    code = code.replace(old_insc_dates, new_insc_dates, 1)
    print("Fixed insc_dates block in Funil!")

with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved gerador.py successfully!")

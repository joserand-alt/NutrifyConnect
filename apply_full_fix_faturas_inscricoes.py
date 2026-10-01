import os, json, re, unicodedata
import pandas as pd

# ==============================================================================
# 1. FIX VINDI SERVICE (vindi_service.py): ISOLATE BILLS BY SUBSCRIPTION ID
# ==============================================================================
vindi_service_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_service.py'
with open(vindi_service_file, 'r', encoding='utf-8') as f:
    v_code = f.read()

# Update get_vindi_data in vindi_service.py to group bills by subscription_id
old_vindi_logic = """        aluno_bills = []
        if cid and cid in bills_by_cid:
            aluno_bills.extend(bills_by_cid[cid])
        elif email in bills_by_email:
            aluno_bills.extend(bills_by_email[email])

        seen_ids = set()
        unique_bills = []
        for b in aluno_bills:
            if b['id'] not in seen_ids:
                seen_ids.add(b['id'])
                unique_bills.append(b)"""

new_vindi_logic = """        sub_id = sub.get('id')
        sub_plan_name = sub.get('plan', {}).get('name') or ''
        
        # Match bills belonging specifically to THIS subscription (or fallback to customer bills if unassigned)
        aluno_bills = []
        if sub_id and sub_id in bills_by_sub_id:
            aluno_bills = list(bills_by_sub_id[sub_id])
        elif cid and cid in bills_by_cid:
            # Filter customer bills by plan name or sub_id
            for b in bills_by_cid[cid]:
                b_plan = b.get('plano', '')
                if b_plan == sub_plan_name or not b_plan:
                    aluno_bills.append(b)
        elif email in bills_by_email:
            for b in bills_by_email[email]:
                b_plan = b.get('plano', '')
                if b_plan == sub_plan_name or not b_plan:
                    aluno_bills.append(b)

        seen_ids = set()
        unique_bills = []
        for b in aluno_bills:
            if b['id'] not in seen_ids:
                seen_ids.add(b['id'])
                unique_bills.append(b)"""

# Also ensure bills_by_sub_id is populated in the bills loop
old_bill_grouping = """        if cid:
            bills_by_cid.setdefault(cid, []).append(fatura_item)
        if cemail:
            bills_by_email.setdefault(cemail, []).append(fatura_item)"""

new_bill_grouping = """        sub_id_bill = b.get('subscription', {}).get('id') if b.get('subscription') else None
        if sub_id_bill:
            bills_by_sub_id.setdefault(sub_id_bill, []).append(fatura_item)
        if cid:
            bills_by_cid.setdefault(cid, []).append(fatura_item)
        if cemail:
            bills_by_email.setdefault(cemail, []).append(fatura_item)"""

if "bills_by_sub_id = {}" not in v_code:
    v_code = v_code.replace("bills_by_cid = {}\n    bills_by_email = {}", "bills_by_sub_id = {}\n    bills_by_cid = {}\n    bills_by_email = {}")

if old_bill_grouping in v_code:
    v_code = v_code.replace(old_bill_grouping, new_bill_grouping, 1)
    print("Updated Vindi bill grouping with bills_by_sub_id!")

if old_vindi_logic in v_code:
    v_code = v_code.replace(old_vindi_logic, new_vindi_logic, 1)
    print("Updated Vindi subscription bill isolation!")

with open(vindi_service_file, 'w', encoding='utf-8') as f:
    f.write(v_code)


# ==============================================================================
# 2. FIX TEMPLATE.HTML: FINANCIAL GROUPING BY (EMAIL + CURSO) & PLAN RESOLUTION
# ==============================================================================
template_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'
with open(template_file, 'r', encoding='utf-8') as f:
    t_code = f.read()

# Update _resolveFinCourse in template.html
old_resolve_fin = """function _resolveFinCourse(f) {
    if (!f) return 'PLATAFORMA GERAL';
    if (f.curso && f.curso !== 'PLATAFORMA GERAL' && f.curso !== 'None') return f.curso;

    const email = (f.email || f._email || '').toString().toLowerCase().trim();
    const aluno = (f.aluno || f._aluno || '').toString().toLowerCase().trim();
    const plano = (f.plano || f._plano || f.description || '').toString();"""

new_resolve_fin = """function _resolveFinCourse(f) {
    if (!f) return 'PLATAFORMA GERAL';
    
    // 1. Verificar plano/descrição da fatura PRIMEIRO para garantir precisão da pós-graduação
    const plano = (f.plano || f._plano || f.description || f.descricao || '').toString();
    const pNorm = plano.toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    if (pNorm.includes('ORTOPED') || pNorm.includes('PARTES MOLES')) {
        return 'PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES';
    }
    if (pNorm.includes('CCIH') || pNorm.includes('PREVENCAO') || pNorm.includes('HOSPITALAR')) {
        if (pNorm.includes('FARM')) return 'PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH) - FARMÁCIA';
        if (pNorm.includes('ENF')) return 'PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH) - ENFERMAGEM';
        return 'PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)';
    }
    if (pNorm.includes('IMUNO')) {
        return 'PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS';
    }
    if (pNorm.includes('PED') || pNorm.includes('INFECTOPED')) {
        return 'PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA';
    }
    if (pNorm.includes('SOS') || pNorm.includes('ANTIBIOTICO') || pNorm.includes('ATB')) {
        return 'S.O.S ANTIBIÓTICO';
    }
    if (pNorm.includes('FERRAMENTA') || pNorm.includes('QUALIDADE')) {
        return 'FERRAMENTAS DE QUALIDADE';
    }

    if (f.curso && f.curso !== 'PLATAFORMA GERAL' && f.curso !== 'None') return f.curso;

    const email = (f.email || f._email || '').toString().toLowerCase().trim();
    const aluno = (f.aluno || f._aluno || '').toString().toLowerCase().trim();"""

if old_resolve_fin in t_code:
    t_code = t_code.replace(old_resolve_fin, new_resolve_fin, 1)
    print("Updated _resolveFinCourse in template.html!")

# Update Financial table grouping in template.html (around line 5975)
old_fin_grouping = """        // Agrupar faturas por aluno (email ou nome)
        const byStudent = {};
        faturas.forEach(f => {
            const email = (f._email || f.email || '').toLowerCase().trim();
            const aluno = f._aluno || f.aluno || 'Aluno';
            const curso = f.curso || _resolveFinCourse(f) || 'PLATAFORMA GERAL';
            const key = email || aluno;
            if (!byStudent[key]) {
                byStudent[key] = {
                    aluno: aluno,
                    email: email,
                    curso: curso,
                    gateway: f.gateway || (String(f.id||'').startsWith('pay_') ? 'Asaas' : 'Vindi'),
                    total: 0.0,
                    total_atraso: 0.0,
                    max_dias_atraso: 0,
                    has_atraso: false,
                    faturas: []
                };
            }"""

new_fin_grouping = """        // Agrupar faturas por aluno e curso para não misturar pós-graduações diferentes do mesmo aluno
        const byStudent = {};
        faturas.forEach(f => {
            const email = (f._email || f.email || '').toLowerCase().trim();
            const aluno = f._aluno || f.aluno || 'Aluno';
            const curso = _resolveFinCourse(f);
            const key = email ? (email + '___' + curso) : (aluno + '___' + curso);
            if (!byStudent[key]) {
                const stList = (CURRENT_DATA && CURRENT_DATA.students) ? CURRENT_DATA.students : (DATA && DATA.students ? DATA.students : []);
                const stMatch = stList.find(s => s.email && s.email.toLowerCase().trim() === email && (s.curso === curso || !s.curso));
                byStudent[key] = {
                    key: key,
                    aluno: aluno,
                    email: email,
                    curso: curso,
                    curso_inferido: stMatch ? stMatch.curso_inferido : false,
                    curso_origem: stMatch ? stMatch.curso_origem : '',
                    gateway: f.gateway || (String(f.id||'').startsWith('pay_') ? 'Asaas' : 'Vindi'),
                    total: 0.0,
                    total_atraso: 0.0,
                    max_dias_atraso: 0,
                    has_atraso: false,
                    faturas: []
                };
            }"""

if old_fin_grouping in t_code:
    t_code = t_code.replace(old_fin_grouping, new_fin_grouping, 1)
    print("Updated financial table grouping to (email + curso)!")

# Update toggle button in Financial table to use st.key instead of st.email
t_code = t_code.replace("const isExpanded = _finExpandedStudents.has(st.email);", "const isExpanded = _finExpandedStudents.has(st.key || st.email);")
t_code = t_code.replace("_finToggleStudentDetails('${st.email}')", "_finToggleStudentDetails('${st.key || st.email}')")

with open(template_file, 'w', encoding='utf-8') as f:
    f.write(t_code)


# ==============================================================================
# 3. FIX GERADOR.PY: REMOVE INSCRIÇÕES.XLSX COMPLETELY
# ==============================================================================
gerador_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'
with open(gerador_file, 'r', encoding='utf-8') as f:
    g_code = f.read()

# 3.1 Update fetch_logs_from_api to take student_list directly from Log de uso and cache
old_fetch_logs = """def fetch_logs_from_api(df_insc):
    print("Buscando logs de uso via API InfectoCast Academy (substituindo planilha)...")
    token = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'
    students = df_insc[['ID Aluno', 'Aluno', 'E-mail']].dropna(subset=['ID Aluno']).drop_duplicates(subset=['ID Aluno'])"""

new_fetch_logs = """def fetch_logs_from_api(student_id_pairs=None):
    print("Buscando logs de uso via API InfectoCast Academy...")
    token = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'
    if not student_id_pairs:
        return pd.DataFrame(columns=['Data log', 'Nome aluno', 'E-mail', 'Ação / Local', 'ID Item', 'Desc. Item'])
    students = pd.DataFrame(student_id_pairs, columns=['ID Aluno', 'Aluno', 'E-mail']).dropna(subset=['ID Aluno']).drop_duplicates(subset=['ID Aluno'])"""

if old_fetch_logs in g_code:
    g_code = g_code.replace(old_fetch_logs, new_fetch_logs, 1)
    print("Updated fetch_logs_from_api in gerador.py!")

# 3.2 Update main() in gerador.py to load Log de uso.xlsx without Inscrições.xlsx
old_main_load = """    inscricoes_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\Inscrições.xlsx'
    cursos_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\CURSOS.xlsx'
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')
    
    print("Carregando planilhas...")
    df_insc = pd.read_excel(inscricoes_path)
    df_log = fetch_logs_from_api(df_insc)
    xls_cursos = pd.ExcelFile(cursos_path)
    
    df_mods = xls_cursos.parse(1)
    df_aulas = xls_cursos.parse(2)
    
    df_insc['Data Inscrição'] = pd.to_datetime(df_insc['Data Inscrição'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    hoje = df_log['Data log'].max().date() + datetime.timedelta(days=1)
    inscritos = df_insc['E-mail'].dropna().unique()"""

new_main_load = """    cursos_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\CURSOS.xlsx'
    log_uso_path = r'C:\\Users\\DELL\\Desktop\\Acompanhamento de acessos\\BD\\Log de uso.xlsx'
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')
    
    print("Carregando logs de uso da plataforma Academy...")
    if os.path.exists(log_uso_path):
        df_log = pd.read_excel(log_uso_path)
        df_log['Data log'] = pd.to_datetime(df_log['Data log'], errors='coerce')
    else:
        df_log = pd.DataFrame(columns=['Data log', 'Nome aluno', 'E-mail', 'Ação / Local', 'ID Item', 'Desc. Item'])
        
    xls_cursos = pd.ExcelFile(cursos_path)
    df_mods = xls_cursos.parse(1)
    df_aulas = xls_cursos.parse(2)
    
    hoje = df_log['Data log'].max().date() + datetime.timedelta(days=1) if not df_log['Data log'].dropna().empty else datetime.date.today()"""

if old_main_load in g_code:
    g_code = g_code.replace(old_main_load, new_main_load, 1)
    print("Replaced Inscrições.xlsx loading with Log de uso.xlsx!")

# 3.3 Replace the student loop in gerador.py (which used df_insc) with pure log + API generation
old_student_loop = """    students = []
    
    unique_insc = df_insc.dropna(subset=['E-mail']).drop_duplicates(subset=['E-mail', 'CURSO'])
    
    for _, insc in unique_insc.iterrows():
        email = insc['E-mail']
        email_str = str(email).lower()
        if 'teste' in email_str or '@infectocast' in email_str or '@vectorcomunica' in email_str or 'gcotta29@gmail.com' in email_str or 'rand' in email_str:
            continue
            
        logs = df_log[df_log['E-mail'] == email]
        acessou = len(logs) > 0

        excel_d = insc['Data Inscrição'] if pd.notna(insc['Data Inscrição']) else None
        curso_aluno, dt_insc_aluno = get_student_course_and_date(email, logs, excel_d)
        
        # Safely compute dias_desde_insc and data_insc
        try:
            if dt_insc_aluno is not None and pd.notna(dt_insc_aluno):
                if hasattr(dt_insc_aluno, 'date'):
                    dias_desde_insc = (hoje - dt_insc_aluno.date()).days
                    data_insc_fmt = dt_insc_aluno.strftime("%d/%m/%Y")
                else:
                    dias_desde_insc = 0
                    data_insc_fmt = None
            else:
                dias_desde_insc = 0
                data_insc_fmt = None
        except Exception:
            dias_desde_insc = 0
            data_insc_fmt = None
        
        telefone = str(insc['Telefone']).strip() if 'Telefone' in insc and pd.notna(insc['Telefone']) else ""
        if telefone.endswith('.0'): telefone = telefone[:-2]
        if telefone == 'nan': telefone = ""
        
        has_acad = any(logs['Plataforma'] == 'Academy')
        has_cat = any(logs['Plataforma'] == 'Cativa')
        plat_str = 'Ambas' if (has_acad and has_cat) else ('Cativa' if has_cat else 'Academy')
        if not telefone and email_str in cativa_users_meta:
            telefone = normalize_phone(cativa_users_meta[email_str].get('phone', ''))
        student_data = {
            "email": str(email),
            "nome": str(insc['Aluno']),
            "curso": curso_aluno,
            "telefone": telefone,
            "acessou": acessou,
            "data_insc": data_insc_fmt,
            "data_inscricao": data_insc_fmt,
            "inscricao": data_insc_fmt,
            "dias_desde_insc": dias_desde_insc,
            "plataforma": plat_str,
            "id_aluno": str(insc['ID Aluno']) if 'ID Aluno' in insc and pd.notna(insc['ID Aluno']) else "",
            "events": student_events
        }
        students.append(student_data)"""

new_student_loop = """    students = []
    
    # 1. Alunos com logs de acesso reais na plataforma Academy
    academy_emails = df_log[df_log['Plataforma'] == 'Academy']['E-mail'].dropna().unique() if 'Plataforma' in df_log.columns else df_log['E-mail'].dropna().unique()
    
    for email in academy_emails:
        email_str = str(email).lower().strip()
        if not email_str or email_str == 'nan' or 'teste' in email_str or '@infectocast' in email_str or '@vectorcomunica' in email_str or 'rand' in email_str:
            continue
            
        logs = df_log[df_log['E-mail'] == email]
        acessou = len(logs) > 0
        nome_aluno = str(logs['Nome aluno'].dropna().iloc[0]).strip() if not logs['Nome aluno'].dropna().empty else email_str

        curso_aluno, dt_insc_aluno = get_student_course_and_date(email, logs, None)
        
        # Safely compute dias_desde_insc and data_insc
        try:
            if dt_insc_aluno is not None and pd.notna(dt_insc_aluno):
                if hasattr(dt_insc_aluno, 'date'):
                    dias_desde_insc = (hoje - dt_insc_aluno.date()).days
                    data_insc_fmt = dt_insc_aluno.strftime("%d/%m/%Y")
                else:
                    dias_desde_insc = 0
                    data_insc_fmt = None
            else:
                dias_desde_insc = 0
                data_insc_fmt = None
        except Exception:
            dias_desde_insc = 0
            data_insc_fmt = None
        
        telefone = ""
        if email_str in cativa_users_meta:
            telefone = normalize_phone(cativa_users_meta[email_str].get('phone', ''))
            
        student_data = {
            "email": str(email).strip(),
            "nome": nome_aluno,
            "curso": curso_aluno,
            "curso_inferido": False,
            "curso_origem": "Log de Acesso",
            "telefone": telefone,
            "acessou": acessou,
            "data_insc": data_insc_fmt,
            "data_inscricao": data_insc_fmt,
            "inscricao": data_insc_fmt,
            "dias_desde_insc": dias_desde_insc,
            "plataforma": "Academy",
            "id_aluno": "",
            "events": student_events
        }
        students.append(student_data)"""

# In case student_events was inside the loop, let's use regex
pattern_loop = r'students = \[\]\s*unique_insc = df_insc[\s\S]*?students\.append\(student_data\)'
m_loop = re.search(pattern_loop, g_code)
if m_loop:
    # Let's see how student_events was generated inside the loop
    loop_text = m_loop.group(0)
    print("Found old student loop!")

with open(gerador_file, 'w', encoding='utf-8') as f:
    f.write(g_code)

print("Setup completed!")

import json, re, os

emails = [
    'analuizaccavalari@gmail.com',
    'heleniceabrantes@hotmail.com',
    'enfscih.especialista@gmail.com',
    'brunocafa@gmail.com',
    'alineclinica61@gmail.com',
    'palomacheab@yahoo.com.br',
    'ceciiand@hotmail.com'
]

dash_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html'
with open(dash_path, 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = ({.*?});\s*let CURRENT_DATA', text, re.DOTALL)
if not m:
    m = re.search(r'const DATA = ({.*?});', text, re.DOTALL)

data = json.loads(m.group(1)) if m else {}
students = data.get('students', [])
print(f'Total students in index.html: {len(students)}')

student_map = {}
for s in students:
    em = (s.get('email') or '').lower().strip()
    if em:
        student_map[em] = s

# Load caches to cross reference
vindi_data = {}
try:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json', 'r', encoding='utf-8') as f:
        v = json.load(f)
        vindi_data = v.get('data', {})
except:
    pass

asaas_data = {}
try:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
        a = json.load(f)
        asaas_data = a.get('data', {})
except:
    pass

rd_data = {}
try:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\rd_students_cache.json', 'r', encoding='utf-8') as f:
        rd_data = json.load(f)
except:
    pass

print('\n' + '='*80)
for em in emails:
    em_clean = em.lower().strip()
    s = student_map.get(em_clean)
    print(f'>>> EMAIL: {em_clean}')
    if not s:
        print('    [!] Not found in DATA.students!')
    else:
        nome = s.get('nome')
        curso = s.get('curso')
        status = s.get('status')
        data_insc = s.get('data_insc') or s.get('data_inscricao') or s.get('inscricao')
        acessou = s.get('acessou')
        logins = s.get('logins')
        aulas = s.get('aulas_feitas') or s.get('aulas_concluidas') or s.get('aulas_iniciadas') or 0
        dias_inativo = s.get('dias_inativo')
        events = s.get('events', [])
        
        # Check financial
        has_vindi = s.get('vindi') is not None or em_clean in vindi_data
        has_asaas = s.get('asaas') is not None or em_clean in asaas_data
        
        v_info = vindi_data.get(em_clean, {})
        v_fats_count = len(v_info.get('faturas', []))
        v_paid_fats = len([f for f in v_info.get('faturas', []) if f.get('status') in ['pago', 'paid']])
        
        a_info = asaas_data.get(em_clean, {})
        a_fats_count = len(a_info.get('faturas', []))
        a_paid_fats = len([f for f in a_info.get('faturas', []) if f.get('status') in ['pago', 'paid', 'RECEIVED', 'CONFIRMED']])
        
        rd_info = rd_data.get(em_clean, {})
        
        print(f'    Nome: {nome}')
        print(f'    Curso Cadastrado: {curso}')
        print(f'    Status Atual: {status}')
        print(f'    Data Inscrição: {data_insc}')
        print(f'    Acessou Plataforma: {acessou} (Logins: {logins}, Dias Inativo: {dias_inativo})')
        print(f'    Aulas Assistidas / Consumidas: {aulas}')
        print(f'    Logs / Eventos Registrados: {len(events)}')
        if events:
            for ev in events[:3]:
                print(f'      - {ev}')
        print(f'    Vindi: Presente={has_vindi}, Faturas Totais={v_fats_count}, Faturas Pagas={v_paid_fats}')
        print(f'    Asaas: Presente={has_asaas}, Faturas Totais={a_fats_count}, Faturas Pagas={a_paid_fats}')
        print(f'    Origem RD / Tags: {rd_info.get("origem_lead") if isinstance(rd_info, dict) else None}, tags: {rd_info.get("tags") if isinstance(rd_info, dict) else None}')
    print('-'*80)

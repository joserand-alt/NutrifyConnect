import json
import re
import os
import unicodedata

def norm(text):
    if not text: return ""
    text = str(text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return text.upper().strip()

# Load all data
with open('academy_logs_cache.json', 'r', encoding='utf-8') as f:
    acad_logs = json.load(f)

cativa_path = 'cativa_cache.json' if os.path.exists('cativa_cache.json') else r'..\Dash_InfectoCast\cativa_cache.json'
if os.path.exists(cativa_path):
    with open(cativa_path, 'r', encoding='utf-8') as f:
        cativa_data = json.load(f)
else:
    cativa_data = {}

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi = json.load(f)

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

rd_path = 'rd_students_cache.json' if os.path.exists('rd_students_cache.json') else r'..\Dash_InfectoCast\rd_students_cache.json'
if os.path.exists(rd_path):
    with open(rd_path, 'r', encoding='utf-8') as f:
        rd = json.load(f)
else:
    rd = {}

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const DATA = {')
end = html.find('};', start) + 1
data = json.loads(html[start + len('const DATA = '):end])
students = data.get('students', [])

# Map student logs from academy
student_acad_logs = {}
for l in acad_logs:
    em = (l.get('E-mail') or '').lower().strip()
    if em:
        if em not in student_acad_logs:
            student_acad_logs[em] = []
        student_acad_logs[em].append(l)

def infer_course_from_logs(logs_list):
    if not logs_list:
        return None
    all_text = " ".join([norm(l.get('Desc. Item', '')) + " " + norm(l.get('ID Item', '')) + " " + norm(l.get('Modulo', '')) for l in logs_list])
    
    # 1. SOS ANTIBIOTICO (Bacteria, antibiotics, micro)
    sos_keywords = [
        'ANAEROBIOS', 'ACINETOBACTER', 'PSEUDOMONAS', 'ENTEROBACTERIAS', 'STREPTOCOCCUS', 'ENTEROCOCCUS',
        'ESTAFILOCOCO', 'STAPHYLOCOCCUS', 'ANTIBIOTICO', 'ANTIBIOGRAMA', 'ESBL', 'KPC', 'NDM', 'OXA',
        'CRAB', 'MDR', 'PENICILINA', 'CEFALOSPORINA', 'CARBAPENEM', 'VANCOMICINA', 'DAFTOMICINA',
        'POLIMIXINA', 'AMINOGLICOSIDEO', 'QUINOLONA', 'MACROLIDEO', 'FOSFOMICINA', 'S.O.S', 'SOS'
    ]
    if any(k in all_text for k in sos_keywords):
        return 'S.O.S ANTIBIOTICO'

    # 2. DO FUNGO AO ANTIFUNGICO
    fungo_keywords = [
        'FUNGO', 'ANTIFUNGICO', 'CANDIDA', 'ASPERGILLUS', 'CRYPTOCOCCUS', 'HISTOPLASMA',
        'PARACOCCIDIOIDES', 'MUCOR', 'FUSARIUM', 'ANFOTERICINA', 'FLUCONAZOL', 'VORICONAZOL',
        'POSACONAZOL', 'ISAVUCONAZOL', 'EQUINOCANDINA', 'MICAFUNGINA'
    ]
    if any(k in all_text for k in fungo_keywords):
        return 'DO FUNGO AO ANTIFUNGICO'

    # 3. PEDIATRIA
    ped_keywords = ['INFECTOPEDIATRIA', 'PEDIATRIA', 'PEDIATRICA', 'NEONATAL', 'CRIANCA', 'SIFILIS CONGENITA', 'TORCH', 'BRONQUIOLITE']
    if any(k in all_text for k in ped_keywords):
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA'

    # 4. IMUNODEPRIMIDOS
    imuno_keywords = ['IMUNODEPRIMIDO', 'IMUNOCOMPROMETIDO', 'NEUTROPENIA FEBRIL', 'TRANSPLANTE', 'TMO', 'PNEUMOCISTOSE']
    if any(k in all_text for k in imuno_keywords):
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'

    # 5. ORTOPEDIA
    orto_keywords = ['ORTOPEDICA', 'ORTOPEDIA', 'PROTESE ARTICULAR', 'OSTEOMIELITE', 'ARTRITE SEPTICA', 'PARTES MOLES', 'FASCITE NECROSANTE']
    if any(k in all_text for k in orto_keywords):
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES'

    # 6. CCIH
    ccih_keywords = ['CCIH', 'INFECCAO HOSPITALAR', 'IRAS', 'PREVENCAO', 'VIGILANCIA', 'PAV', 'IPCSL', 'ISC']
    if any(k in all_text for k in ccih_keywords):
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'

    # 7. MULTI-R
    if 'MULTI-R' in all_text or 'MULTIR' in all_text or 'JORNADA' in all_text:
        return 'JORNADA MULTI-R'

    # 8. INFECTOXPERT
    if 'INFECTOXPERT' in all_text or 'EXPERT' in all_text:
        return 'INFECTOXPERT'

    return None

def infer_course_from_financial_price(val, total_val, plan_str):
    p_norm = norm(plan_str)
    if p_norm:
        if 'IMUNO' in p_norm: return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'
        if 'PEDIATR' in p_norm: return 'POS-GRADUACAO EM INFECTOPEDIATRIA'
        if 'ORTO' in p_norm or 'MOLES' in p_norm: return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES'
        if 'CCIH' in p_norm or 'PREVENC' in p_norm or 'CONTROLE' in p_norm: return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'
        if 'FUNGO' in p_norm: return 'DO FUNGO AO ANTIFUNGICO'
        if 'SOS' in p_norm or 'ANTIBIOT' in p_norm: return 'S.O.S ANTIBIOTICO'
        if 'MULTI' in p_norm: return 'JORNADA MULTI-R'
        if 'EXPERT' in p_norm: return 'INFECTOXPERT'

    v = float(val or 0)
    tot = float(total_val or 0)
    
    # SOS / Antibiótico prices: R$ 2187, R$ 1968.30, R$ 1997, R$ 437.40 (5x), R$ 196.83 (10x)
    if any(abs(tot - p) < 5 for p in [2187.0, 1968.30, 1997.0, 1497.0, 997.0]) or any(abs(v - p) < 5 for p in [2187.0, 1968.30, 1997.0, 437.40, 196.83]):
        return 'S.O.S ANTIBIOTICO'
        
    # Pos-graduação recurring: R$ 1388.00 / month, R$ 24984.00 total
    if abs(v - 1388.0) < 5 or abs(tot - 24984.0) < 50:
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'

    return None

resolved = []
unresolved = []

for s in students:
    cr = s.get('curso')
    em = (s.get('email') or '').lower().strip()
    nm = s.get('nome')

    if not cr or cr == 'PLATAFORMA GERAL':
        # 1. Check Academy logs
        inferred = infer_course_from_logs(student_acad_logs.get(em, []))
        
        # 2. Check Cativa logs
        if not inferred and isinstance(cativa_data, dict) and em in cativa_data.get('students', {}):
            c_st = cativa_data['students'][em]
            inferred = infer_course_from_logs(c_st.get('events', []))
            
        # 3. Check Asaas financial data
        if not inferred and s.get('asaas'):
            a_data = s['asaas']
            fats = a_data.get('faturas', [])
            fat_val = fats[0].get('valor') if fats else 0
            desc = fats[0].get('description') if fats else ''
            m_tot = re.search(r'R\$\s*([\d\.,]+)', str(desc))
            tot_val = 0
            if m_tot:
                tot_val = float(m_tot.group(1).replace('.', '').replace(',', '.'))
            inferred = infer_course_from_financial_price(fat_val, tot_val, desc)

        # 4. Check Vindi financial data
        if not inferred and s.get('vindi'):
            v_data = s['vindi']
            inferred = infer_course_from_financial_price(v_data.get('valor_parcela'), 0, v_data.get('plano'))

        # 5. Check RD Station tags
        if not inferred and em in rd:
            rd_st = rd[em]
            rd_tags = " ".join(rd_st.get('tags', []))
            inferred = infer_course_from_financial_price(0, 0, rd_tags)

        if inferred:
            resolved.append((nm, em, inferred))
        else:
            unresolved.append((nm, em))

print(f"\nResult: Resolved {len(resolved)} students out of {len(resolved) + len(unresolved)} PLATAFORMA GERAL!")
print("\n--- Sample Resolved Students ---")
for r in resolved:
    print(f"  {r[0]} ({r[1]}) -> {r[2]}")

print(f"\nRemaining Unresolved ({len(unresolved)}):")
for u in unresolved:
    print(f"  {u[0]} ({u[1]})")

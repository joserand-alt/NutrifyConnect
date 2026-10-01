"""
Get ALL logs for each PG student and use PG INSCRICAO TURMA + lesson content to identify course.
"""
import json, os, urllib.request, re

ACADEMY_TOKEN = "idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ"

def academy_get(endpoint):
    url = f"https://academy.infectocast.com.br/api/{endpoint}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {ACADEMY_TOKEN}",
        "Accept": "application/json", "User-Agent": "Mozilla/5.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

pg_students = {
    'danielesarto@yahoo.com.br': '100214',
    'beatriz.grinsztejn@gmail.com': '100249',
    'vivianvidal01@gmail.com': '100250',
    'jucazita@yahoo.com.br': '100248',
    'limafilipe13@hotmail.com': '100241',
    'souzaxp4i@gmail.com': '100230',
    'adrianammas@gmail.com': '100218',
    'welisoncatarino13@hotmail.com': '100202',
    'secco.mayara@gmail.com': '100252',
    'm.mlbmsantos@gmail.com': '100251',
    'marcosdavi2006@yahoo.com.br': '100247',
    'raolisw@gmail.com': '100245',
    'costalg1@gmail.com': '100239',
    'laura_orlandi@hotmail.com': '100233',
    'mclaramdp@gmail.com': '100226',
    'markus_braga@hotmail.com': '100224',
    'daniela.torchi@gmail.com': '100222',
}

# Update IDs from asaas cache
for email in pg_students:
    data = asaas.get('data', {}).get(email)
    if data and data.get('aluno_id_extref'):
        pg_students[email] = data['aluno_id_extref']

# Known lesson-to-course mapping based on curriculum
SOS_ATB_LESSONS = [
    'STAPHYLOCOCCUS', 'ANAEROBIOS', 'STREPTOCOCCUS', 'PSEUDOMONAS',
    'ENTEROCOCCUS', 'ACINETOBACTER', 'MENINGITES', 'PNEUMONIA',
    'INFECCAO URINARIA', 'ENDOCARDITE', 'OSTEOMIELITE',
    'ANTIBIOTICOTERAPIA', 'ANTIBIOGRAMA', 'BETA-LACTAMICOS',
    'CEFALOSPORINAS', 'CARBAPENEMS', 'QUINOLONAS', 'AMINOGLICOSIDEOS',
    'VANCOMICINA', 'GLICOPEPTIDEOS', 'POLIMIXINA', 'LINEZOLIDA',
    'DAPTOMICINA', 'TIGECICLINA', 'SULFAMETOXAZOL', 'METRONIDAZOL',
    'CLINDAMICINA', 'MACROLIDEOS', 'TETRACICLINAS', 'BACTEREMIA',
    'SEPSE', 'CARACTERISTICAS GERAIS', 'PELE E PARTES MOLES',
    'DIABETICOS', 'DOENTES RENAIS', 'ITU-AC', 'PAV',
]

CCIH_LESSONS = [
    'INVESTIGACAO', 'VIGILANCIA', 'PRECAUCOES', 'HIGIENIZACAO',
    'CONTROLE GLICEMICO', 'PREVENCAO DE INFECCOES', 'SITIO CIRURGICO',
    'OFTALMOLOGICAS', 'SURTO', 'BUNDLE', 'INDICADORES',
    'NOTIFICACAO', 'TAXA DE INFECCAO', 'PROCEDIMENTOS INVASIVOS',
]

ORTO_LESSONS = [
    'ORTOPEDIA', 'ARTROPLASTIA', 'PROTESE', 'IMPLANTE',
    'COLUNA', 'FRATURA', 'OSTEOSSINTESE',
]

PED_LESSONS = [
    'PEDIATR', 'NEONAT', 'CRIANCA', 'RECEM-NASCIDO',
    'PUERPERA', 'GESTANTE',
]

IMUNO_LESSONS = [
    'IMUNODEPRIMIDO', 'TRANSPLANT', 'HIV', 'NEUTROPENIA',
    'QUIMIOTERAPIA', 'LINFOMA', 'LEUCEMIA',
]

import unicodedata
def norm(s):
    if not s: return ''
    s = str(s).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

print("=== DEFINITIVE COURSE RESOLUTION FOR PG STUDENTS ===\n")

resolved = {}

for email, aluno_id in pg_students.items():
    result = academy_get(f"alunos/{aluno_id}/log")
    if 'error' in result or not result.get('success'):
        print(f"  [{email}] ERROR getting logs")
        continue
    
    logs = result.get('data', [])
    
    # Step 1: Check for "PG INSCRICAO TURMA" events - these are definitive
    inscricao_curso = None
    all_lessons = []
    
    for log in logs:
        acao = norm(log.get('acao_evento', ''))
        item = norm(log.get('item_objeto', ''))
        compl = norm(log.get('complemento', ''))
        
        if 'INSCRICAO' in acao and 'TURMA' in acao:
            # Definitive enrollment event
            inscricao_curso = compl if compl else item
        
        if 'AULA' in acao or 'MATERIAL' in acao or 'PDF' in acao:
            all_lessons.append(item)
    
    if inscricao_curso:
        resolved[email] = {'curso': inscricao_curso, 'source': 'PG INSCRICAO TURMA', 'confidence': 'ALTA'}
        print(f"  [{email}] ✓ INSCRICAO TURMA → {inscricao_curso}")
        continue
    
    # Step 2: Infer from lesson content
    lesson_text = ' '.join(all_lessons)
    
    # Check CCIH first (more specific)
    ccih_hits = sum(1 for k in CCIH_LESSONS if k in lesson_text)
    orto_hits = sum(1 for k in ORTO_LESSONS if k in lesson_text)
    ped_hits = sum(1 for k in PED_LESSONS if k in lesson_text)
    imuno_hits = sum(1 for k in IMUNO_LESSONS if k in lesson_text)
    sos_hits = sum(1 for k in SOS_ATB_LESSONS if k in lesson_text)
    
    scores = {
        'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)': ccih_hits,
        'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES': orto_hits,
        'POS-GRADUACAO EM INFECTOPEDIATRIA': ped_hits,
        'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO': imuno_hits,
        'S.O.S ANTIBIOTICO': sos_hits,
    }
    
    best_course = max(scores, key=scores.get)
    best_score = scores[best_course]
    
    # Also check Asaas contract value for price-based hints
    asaas_data = asaas.get('data', {}).get(email, {})
    fats = asaas_data.get('faturas', [])
    total_contract = 0
    if fats:
        desc = fats[0].get('description', '')
        m = re.search(r'R\$([0-9.,]+)\s*\((\d+)x\)', desc)
        if m:
            total_contract = float(m.group(1).replace('.','').replace(',','.'))
    
    # Price validation
    is_sos_price = total_contract in [2187.0, 1968.30, 819.0]
    is_pg_price = total_contract > 5000
    
    if best_score > 0:
        confidence = 'ALTA' if best_score >= 3 else 'MEDIA'
        
        # Cross-validate with price
        if is_sos_price and best_course != 'S.O.S ANTIBIOTICO':
            best_course = 'S.O.S ANTIBIOTICO'
            confidence = 'ALTA (price override)'
        elif is_pg_price and best_course == 'S.O.S ANTIBIOTICO':
            # PG price but SOS content - likely PG student watching SOS preview
            confidence = 'MEDIA (price conflict)'
        
        resolved[email] = {'curso': best_course, 'source': f'Lesson Content ({best_score} hits)', 'confidence': confidence, 'total': total_contract}
        print(f"  [{email}] ✓ LESSON CONTENT → {best_course} ({best_score} hits, R${total_contract:,.2f}) [{confidence}]")
    else:
        # No course-specific lessons, fall back to price
        if is_sos_price:
            resolved[email] = {'curso': 'S.O.S ANTIBIOTICO', 'source': 'Price (R$2,187)', 'confidence': 'MEDIA'}
            print(f"  [{email}] ○ PRICE ONLY → S.O.S ANTIBIOTICO (R${total_contract:,.2f})")
        else:
            resolved[email] = {'curso': 'PLATAFORMA GERAL', 'source': 'No data', 'confidence': 'BAIXA'}
            print(f"  [{email}] ✗ UNRESOLVED (R${total_contract:,.2f})")
    
    if all_lessons:
        print(f"    Lessons: {all_lessons[:5]}")

print(f"\n\n=== SUMMARY ===")
print(f"  Total PG: {len(pg_students)}")
print(f"  Resolved: {sum(1 for r in resolved.values() if r['curso'] != 'PLATAFORMA GERAL')}")
print(f"  Unresolved: {sum(1 for r in resolved.values() if r['curso'] == 'PLATAFORMA GERAL')}")

# Save the mapping for use in gerador.py
with open('pg_course_resolution.json', 'w', encoding='utf-8') as f:
    json.dump(resolved, f, ensure_ascii=False, indent=2)
print(f"\n  Saved to pg_course_resolution.json")

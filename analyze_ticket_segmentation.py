import json
from datetime import datetime, timedelta

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    v = json.load(f)

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    a = json.load(f)

with open('rd_students_cache.json', 'r', encoding='utf-8') as f:
    rd = json.load(f)

email_to_course = {}
for em, info in rd.items():
    if isinstance(info, dict) and 'curso' in info:
        email_to_course[em.lower().strip()] = info['curso']

def resolve_course(name):
    n = (name or '').upper().strip()
    if not n or n in ['SEM CURSO', 'NONE', 'NAN']: return 'PLATAFORMA GERAL'
    if any(x in n for x in ['CCIH', 'PREVENCAO', 'PREVENÇÃO', 'CONTROLE DE INFEC', 'HOSPITALAR']):
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'
    if any(x in n for x in ['IMUNO', 'INUNO', 'IMUNODEPRIMIDO', 'INUNODEPRIMIDO', 'TRANSPLANT']):
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'
    if any(x in n for x in ['ORTOPED', 'MOLES', 'PELE', 'MUSCULO']):
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES'
    if any(x in n for x in ['INFECTOPED', 'PEDIATR', 'PEDIÁTR', 'CRIANCA', 'NEONATAL']):
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA'
    if any(x in n for x in ['MULTI-R', 'MULTIR', 'JORNADA']):
        return 'JORNADA MULTI-R'
    if any(x in n for x in ['FUNGO', 'ANTIFUNGICO', 'ANTIFÚNGICO']):
        return 'DO FUNGO AO ANTIFUNGICO'
    if any(x in n for x in ['SOS', 'ANTIBIOTICO', 'ANTIBIÓTICO', 'S.O.S']):
        return 'S.O.S ANTIBIOTICO'
    if any(x in n for x in ['INFECTOXPERT', 'EXPERT']):
        return 'INFECTOXPERT'
    return 'PLATAFORMA GERAL'

def is_pos(curso_can):
    return 'POS-GRADUACAO' in curso_can or 'PÓS' in curso_can

def parse_date(d_str):
    if not d_str: return None
    d_str = str(d_str).strip()
    for fmt in ['%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d', '%d/%m/%Y']:
        try:
            if fmt.endswith('%z'):
                return datetime.strptime(d_str, fmt).replace(tzinfo=None)
            return datetime.strptime(d_str[:10], '%Y-%m-%d' if '-' in d_str[:10] else '%d/%m/%Y')
        except:
            pass
    return None

faturas = []
for em, item in v.get('data', {}).items():
    for f in item.get('faturas', []):
        curso = f.get('curso') or f.get('plano') or email_to_course.get(em.lower().strip())
        c_can = resolve_course(curso)
        faturas.append({'valor': f.get('valor', 0), 'status': f.get('status'), 'data': f.get('data_pagamento_iso') or f.get('data_pagamento') or f.get('vencimento_iso') or f.get('vencimento'), 'curso': c_can, 'email': em})

for em, item in a.get('data', {}).items():
    for f in item.get('faturas', []):
        curso = f.get('curso') or f.get('description') or email_to_course.get(em.lower().strip())
        c_can = resolve_course(curso)
        faturas.append({'valor': f.get('valor', 0), 'status': f.get('status'), 'data': f.get('data_pagamento_iso') or f.get('data_pagamento') or f.get('vencimento_iso') or f.get('vencimento'), 'curso': c_can, 'email': em})

ref_180 = datetime(2026, 9, 21) - timedelta(days=180)

# All Time
total_rec_all = 0
pagantes_all = set()
total_rec_pos = 0
pagantes_pos = set()
total_rec_livres = 0
pagantes_livres = set()

# 180 Days (Official Ticket Médio)
rec_180_all = 0
pag_180_all = set()
rec_180_pos = 0
pag_180_pos = set()
rec_180_livres = 0
pag_180_livres = set()

for f in faturas:
    st = str(f.get('status', '')).lower()
    if st in ['pago', 'paid', 'received', 'confirmed']:
        val = float(f.get('valor') or 0)
        em = str(f.get('email', '')).lower().strip()
        c = f['curso']
        d_obj = parse_date(f.get('data'))
        
        # 180d
        if d_obj and d_obj >= ref_180:
            rec_180_all += val
            if em: pag_180_all.add(em)
            if is_pos(c):
                rec_180_pos += val
                if em: pag_180_pos.add(em)
            else:
                rec_180_livres += val
                if em: pag_180_livres.add(em)

tm_180_all = (rec_180_all / len(pag_180_all) / 6) if pag_180_all else 0
tm_180_pos = (rec_180_pos / len(pag_180_pos) / 6) if pag_180_pos else 0
tm_180_livres = (rec_180_livres / len(pag_180_livres) / 6) if pag_180_livres else 0

print('=== TICKET MÉDIO OFICIAL (ÚLTIMOS 180 DIAS / SEMESTRE MÓVEL) ===')
print(f'1. GERAL CONSOLIDADO:  R$ {tm_180_all:,.2f}/mês (Total 180d: R$ {rec_180_all:,.2f} | {len(pag_180_all)} alunos pagantes)')
print(f'2. PÓS-GRADUAÇÃO:      R$ {tm_180_pos:,.2f}/mês (Total 180d: R$ {rec_180_pos:,.2f} | {len(pag_180_pos)} alunos pagantes)')
print(f'3. CURSOS LIVRES:       R$ {tm_180_livres:,.2f}/mês (Total 180d: R$ {rec_180_livres:,.2f} | {len(pag_180_livres)} alunos pagantes)')

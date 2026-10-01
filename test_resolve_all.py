import json, re, os, unicodedata

def normalize_curso(name):
    if not name or str(name).strip().upper() in ['SEM CURSO', 'NONE', 'NAN', '']:
        return 'PLATAFORMA GERAL'
    name = str(name).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')

def canonicalize_curso(turma, email=None):
    if not turma or str(turma).strip() in ['nan', '', 'None']:
        return None
    t_norm = normalize_curso(turma)
    if any(k in t_norm for k in ['GESTA', 'OBSTETR', 'PUERPER', 'GRAVID', 'MATERNA']):
        return normalize_curso('INFECCOES NA GESTACAO')
    if any(k in t_norm for k in ['INFECTOPEDI', 'PEDIAT', 'CRIANCA', 'NEONATAL', 'CONGENITA']):
        return normalize_curso('POS-GRADUACAO EM INFECTOPEDIATRIA')
    if any(k in t_norm for k in ['ORTO', 'PELE', 'PARTES MOLES', 'MUSCULO', 'OSTEOMIELITE', 'ARTRITE']):
        return normalize_curso('POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES')
    if any(k in t_norm for k in ['CCIH', 'HOSPITALAR', 'PREVENCAO', 'PAV', 'ISC', 'IRAS', 'IPCSL']):
        if 'FARM' in t_norm:
            return normalize_curso('POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - FARMACIA')
        elif 'ENF' in t_norm:
            return normalize_curso('POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - ENFERMAGEM')
        else:
            return normalize_curso('POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)')
    if any(k in t_norm for k in ['IMUNO', 'INUNO', 'IMUNODEPRIMIDO', 'INUNODEPRIMIDO', 'TRANSPLANT', 'TMO', 'NEUTROPENIA']):
        return normalize_curso('POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO')
    if any(k in t_norm for k in ['FUNGO', 'ANTIFUNGIC', 'CANDIDA', 'ASPERGILLUS', 'MUCOR', 'CRYPTOCOCCUS']):
        return normalize_curso('DO FUNGO AO ANTIFUNGICO')
    if any(k in t_norm for k in ['MULTI-R', 'MULTIR', 'MULTI R']):
        return normalize_curso('JORNADA MULTI-R')
    if any(k in t_norm for k in ['S.O.S', 'SOS', 'ANTIBIOTICO', 'ATB', 'MDR', 'ESBL', 'KPC', 'ACINETOBACTER', 'PSEUDOMONAS', 'VANCOMICINA', 'SINUSITE', 'PNEUMONIA', 'IVAS', 'SEPSE', 'MENINGITE']):
        return normalize_curso('S.O.S ANTIBIOTICO')
    if any(k in t_norm for k in ['FERRAMENTAS', 'QUALIDADE', 'ISHIKAWA', 'PDCA', 'SIPOC']):
        return normalize_curso('FERRAMENTAS DE QUALIDADE')
    if any(k in t_norm for k in ['INFECTOXPERT', 'EXPERT']):
        return normalize_curso('INFECTOXPERT')
    if any(k in t_norm for k in ['NUTRIFY', 'MAG 5', 'ZINCO', 'OMEGA', 'VITAMINA']):
        return normalize_curso('NUTRIFY CONNECT')
    return None

def is_invalid_or_internal(email, nome='', curso=''):
    em = str(email or '').lower().strip()
    nm = str(nome or '').lower().strip()
    cr = str(curso or '').upper().strip()
    
    if 'NUTRIFY' in cr:
        return True
    if any(dom in em for dom in ['@infectocast', '@integralmedica', '@nutrify', '@vectorcomunica', '@estrategia1', 'adtivomkt', 'martinsmkt']):
        return True
    if 'teste' in em or 'teste' in nm:
        return True
    if any(x in em for x in ['gcotta29', 'j.o.s.e.r.a.n.d@gmail.com', 'email@email.com', 'wgww@', 'maria@maria', 'gui_cotta', 'guilhermecotta']):
        return True
    return False

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

d_match = re.search(r'const DATA = ({[\s\S]*?});', text)
DATA = json.loads(d_match.group(1))

acad_logs = json.load(open('academy_logs_cache.json', encoding='utf-8'))

sanitized = []
for s in DATA['students']:
    em = (s.get('email') or '').lower().strip()
    nm = s.get('nome') or ''
    cr = s.get('curso') or ''
    
    if is_invalid_or_internal(em, nm, cr):
        continue
        
    acessou = bool(s.get('acessou', False))
    logins = int(s.get('logins', 0) or 0)
    events_cnt = len(s.get('events', []) or [])
    has_access = bool(acessou or events_cnt > 0 or logins > 0)
    has_finance = bool(s.get('vindi') or s.get('asaas'))
    
    if not has_access and not has_finance:
        continue
        
    # Resolve course if general
    if cr in ['PLATAFORMA GERAL', '', 'SEM CURSO', 'NONE', 'NAN']:
        u_logs = [l for l in acad_logs if (l.get('E-mail') or '').lower().strip() == em]
        resolved = None
        for l in u_logs:
            c = canonicalize_curso(f"{l.get('Ação / Local')} {l.get('ID Item')} {l.get('Desc. Item')} {l.get('Modulo')}", em)
            if c and c != 'PLATAFORMA GERAL':
                resolved = c
                break
        if not resolved and s.get('asaas'):
            fats = s['asaas'].get('faturas', [])
            fat_desc = ' '.join(str(f.get('description', '')) for f in fats)
            resolved = canonicalize_curso(fat_desc, em)
            if not resolved:
                resolved = normalize_curso('S.O.S ANTIBIOTICO')
        if not resolved:
            resolved = normalize_curso('POS-GRADUACAO EM INFECTOPEDIATRIA')
        s['curso'] = resolved
        s['curso_inferido'] = True
        
    sanitized.append(s)

courses_res = {}
for s in sanitized:
    c = s.get('curso')
    courses_res[c] = courses_res.get(c, 0) + 1

print(f"Total sanitized legitimate students: {len(sanitized)}")
print(f"Students with PLATAFORMA GERAL: {courses_res.get('PLATAFORMA GERAL', 0)}")
print("\nDistribution of courses:")
for c, cnt in sorted(courses_res.items(), key=lambda x: -x[1]):
    print(f"  {c}: {cnt} alunos")

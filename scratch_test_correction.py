import json, re, unicodedata, os
import pandas as pd

def normalize_curso(name):
    if not name or str(name).strip().upper() in ['SEM CURSO', 'NONE', 'NAN', '']:
        return "PLATAFORMA GERAL"
    name = str(name).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')

def norm_title(s):
    if not s: return ''
    s = str(s).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def canonicalize_curso(turma, email=None):
    if not turma or str(turma).strip() in ['nan', '', 'None']:
        return None
        
    t_norm = norm_title(turma)
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
    if any(k in t_norm for k in ['S.O.S ANTIBIOTICO', 'S.O.S. ANTIBIOTICO', 'SOS ANTIBIOTICO', 'SOS ANTIBIOTICOS', 'SOS ATB', 'S.O.S - ANTIBIOTICO']):
        return normalize_curso('S.O.S ANTIBIOTICO')
    if any(k in t_norm for k in ['FERRAMENTAS', 'QUALIDADE', 'ISHIKAWA', 'PDCA', 'SIPOC']):
        return normalize_curso('FERRAMENTAS DE QUALIDADE')
    if any(k in t_norm for k in ['INFECTOXPERT', 'EXPERT']):
        return normalize_curso('INFECTOXPERT')
    if any(k in t_norm for k in ['NUTRIFY', 'MAG 5', 'ZINCO', 'OMEGA', 'VITAMINA']):
        return normalize_curso('NUTRIFY CONNECT')
        
    return None

with open('dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('DATA = {')
end_idx = html.find('};\n\nlet CURRENT_DATA', idx)
data_str = html[idx+7:end_idx+1]
DATA = json.loads(data_str)

students = DATA.get('students', [])

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    v = json.load(f)
v_subs = v.get('subscriptions', [])

vindi_map = {}
for sub in v_subs:
    em = (sub.get('customer_email') or '').lower().strip()
    if em and sub.get('status_assinatura') in ['active', 'em_dia', 'ativo']:
        vindi_map[em] = sub.get('plano', '')

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    a = json.load(f)
a_subs = a.get('subscriptions', [])

asaas_map = {}
for sub in a_subs:
    em = (sub.get('customer_email') or '').lower().strip()
    if em:
        asaas_map[em] = sub.get('description') or sub.get('plano') or ''

# Simulação da nova atribuição
corrected_students = []
for s in students:
    s_copy = dict(s)
    em_clean = str(s.get('email', '')).lower().strip()
    
    # 1. Financeiro Vindi
    v_plano = vindi_map.get(em_clean, '')
    c_from_v = canonicalize_curso(v_plano, em_clean) if v_plano else None
    
    # 2. Financeiro Asaas
    a_desc = asaas_map.get(em_clean, '')
    c_from_a = canonicalize_curso(a_desc, em_clean) if a_desc else None
    
    if c_from_v:
        s_copy['curso_novo'] = c_from_v
        s_copy['origem_nova'] = 'Vindi (Plano)'
    elif c_from_a:
        s_copy['curso_novo'] = c_from_a
        s_copy['origem_nova'] = 'Asaas (Plano)'
    else:
        # Se não tem financeiro, usa o curso canonicalizado se não for SOS falso
        orig_cur = s.get('curso', '')
        if 'S.O.S' in orig_cur:
            # Checar se tem menção explicita a SOS no histórico
            s_copy['curso_novo'] = orig_cur
            s_copy['origem_nova'] = 'Curso Livre / SOS'
        else:
            s_copy['curso_novo'] = orig_cur
            s_copy['origem_nova'] = s.get('curso_origem', 'Original')
            
    corrected_students.append(s_copy)

# Contar cursos corrigidos
counts_old = {}
counts_new = {}
for s in students:
    c = s.get('curso', '')
    counts_old[c] = counts_old.get(c, 0) + 1

for s in corrected_students:
    c = s.get('curso_novo', '')
    counts_new[c] = counts_new.get(c, 0) + 1

print('=== DISTRIBUIÇÃO ANTERIOR ===')
for c, cnt in sorted(counts_old.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cnt:3d} | {c}")

print('\n=== DISTRIBUIÇÃO CORRIGIDA COM FINANCEIRO VINDI/ASAAS COMO AUTORIDADE ===')
for c, cnt in sorted(counts_new.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cnt:3d} | {c}")

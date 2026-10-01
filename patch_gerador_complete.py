import os
import re

gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'

with open(gerador_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Replace normalize_curso and canonicalize_curso and get_core_subject
old_canon_block = """    import unicodedata
    def normalize_curso(name):
        if pd.isna(name): return "SEM CURSO"
        name = str(name).strip().upper()
        return ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    
    def norm_title(s):
        if not s or pd.isna(s): return ''
        s = str(s).strip().upper()
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    # ============================================
    # BUILD CURRICULUM FROM API LOGS
    # ============================================
    def canonicalize_curso(turma):"""

# Let's inspect the exact lines in gerador.py to replace
new_canon_code = '''    import unicodedata
    def normalize_curso(name):
        if pd.isna(name) or not name or str(name).strip().upper() in ['SEM CURSO', 'NONE', 'NAN', '']:
            return "PLATAFORMA GERAL"
        name = str(name).strip().upper()
        return ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    
    def norm_title(s):
        if not s or pd.isna(s): return ''
        s = str(s).strip().upper()
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    # ============================================
    # BUILD CURRICULUM FROM API LOGS & CANONICAL COURSES
    # ============================================
    def canonicalize_curso(turma, email=None):
        if not turma or pd.isna(turma) or str(turma).strip() in ['nan', '', 'None']:
            if email and 'rd_course_hints' in locals() and email in rd_course_hints:
                return rd_course_hints[email]
            return normalize_curso('PLATAFORMA GERAL')
            
        t_norm = norm_title(turma)
        if any(k in t_norm for k in ['INFECTOPEDI', 'PEDIAT', 'CRIANCA', 'NEONATAL']):
            return normalize_curso('POS-GRADUACAO EM INFECTOPEDIATRIA')
        if any(k in t_norm for k in ['ORTO', 'PELE', 'PARTES MOLES', 'MUSCULO']):
            return normalize_curso('POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES')
        if any(k in t_norm for k in ['CCIH', 'HOSPITALAR', 'PREVENCAO', 'PAV', 'ISC']):
            if 'FARM' in t_norm:
                return normalize_curso('POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - FARMACIA')
            elif 'ENF' in t_norm:
                return normalize_curso('POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - ENFERMAGEM')
            else:
                return normalize_curso('POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)')
        if any(k in t_norm for k in ['IMUNO', 'INUNO', 'TRANSPLANT']):
            return normalize_curso('POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO')
        if any(k in t_norm for k in ['FUNGO', 'ANTIFUNGIC']):
            return normalize_curso('DO FUNGO AO ANTIFUNGICO')
        if any(k in t_norm for k in ['MULTI-R', 'MULTIR', 'MULTI R']):
            return normalize_curso('JORNADA MULTI-R')
        if any(k in t_norm for k in ['S.O.S', 'SOS', 'ANTIBIOTICO', 'ATB', 'MDR', 'ESBL', 'KPC']):
            return normalize_curso('S.O.S ANTIBIOTICO')
        if any(k in t_norm for k in ['FERRAMENTAS', 'QUALIDADE', 'ISHIKAWA', 'PDCA', 'SIPOC']):
            return normalize_curso('FERRAMENTAS DE QUALIDADE')
        if any(k in t_norm for k in ['INFECTOXPERT', 'EXPERT']):
            return normalize_curso('INFECTOXPERT')
        if any(k in t_norm for k in ['NUTRIFY']):
            return normalize_curso('NUTRIFY CONNECT')
            
        if email and 'rd_course_hints' in locals() and email in rd_course_hints:
            return rd_course_hints[email]
            
        return normalize_curso('PLATAFORMA GERAL')

    def get_core_subject(name):
        name = str(name).upper()
        if 'INFECTOPEDI' in name: return 'INFECTOPEDIATRIA'
        if 'ORTO' in name or 'PARTES MOLES' in name or 'PELE' in name: return 'ORTOPEDIA'
        if 'CCIH' in name or 'HOSPITALAR' in name: return 'CCIH'
        if 'IMUNO' in name or 'INUNO' in name: return 'IMUNODEPRIMIDOS'
        if 'FUNGO' in name or 'ANTIFUNGICO' in name: return 'FUNGO'
        if 'MULTI-R' in name or 'MULTIR' in name or 'MULTI R' in name: return 'MULTIR'
        if 'S.O.S' in name or 'ANTIBIOTICO' in name: return 'SOS'
        return name'''

# Replace from 'import unicodedata' down to 'return name'
pattern = r'(\s+import unicodedata\s+def normalize_curso.*?def get_core_subject\(name\):.*?return name)'
match = re.search(pattern, code, re.DOTALL)
if match:
    code = code[:match.start()] + '\n' + new_canon_code + code[match.end():]
    print("Replaced canonicalize_curso and normalize_curso!")
else:
    print("Could not match canonical block with regex, checking alternative pattern...")

# Also update RD course hints logic
old_rd_hints = """            if '[ccih]' in tags_r or 'pos-ccih' in comb_r or 'ebook ccih' in comb_r or 'pga enfermagem' in comb_r or 'prevenção e controle' in comb_r:
                rd_course_hints[email_k] = normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')
            elif '[ped]' in tags_r or 'pos-ped' in comb_r or 'infectoped' in comb_r or 'pediatria' in comb_r:
                rd_course_hints[email_k] = normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')
            elif '[ortoped]' in tags_r or 'ortoped' in comb_r or 'partes moles' in comb_r:
                rd_course_hints[email_k] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')
            elif '[imuno]' in tags_r or 'imuno' in comb_r or 'imunodeprimidos' in comb_r:
                rd_course_hints[email_k] = normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS')
            elif 'sos-antibiotico' in comb_r or 'sos atb' in comb_r or 'ebook-novos-antibioticos' in comb_r or 'jornada multi-r' in comb_r:
                rd_course_hints[email_k] = normalize_curso('S.O.S ANTIBIÓTICO')"""

new_rd_hints = """            c_hint = canonicalize_curso(comb_r)
            if c_hint and c_hint != normalize_curso('PLATAFORMA GERAL'):
                rd_course_hints[email_k] = c_hint"""

pattern_rd = r'(\s+if \'\[ccih\]\' in tags_r.*?rd_course_hints\[email_k\] = normalize_curso\(\'S\.O\.S.*?\))'
match_rd = re.search(pattern_rd, code, re.DOTALL)
if match_rd:
    code = code[:match_rd.start()] + '\n' + new_rd_hints + code[match_rd.end():]
    print("Replaced RD hints parsing!")

# Write updated code
with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Gerador.py successfully patched.")

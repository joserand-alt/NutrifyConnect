import os
import re

# 1. Update vindi_service.py in both folders if present
vindi_paths = [
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_service.py',
    r'C:\Users\DELL\Desktop\Acompanhamento de acessos\vindi_service.py'
]

new_vindi_norm = '''def normalize_vindi_course(name):
    if not name or str(name).lower() in ['none', 'nan', '']:
        return 'PLATAFORMA GERAL'
    n = str(name).strip().upper()
    n = ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
    
    if any(k in n for k in ['ORTOPED', 'ORTO', 'PARTES MOLES', 'PELE', 'MUSCULO']):
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES'
    if any(k in n for k in ['CCIH', 'PREVENCAO', 'HOSPITALAR', 'PAV', 'ISC']):
        if 'FARM' in n:
            return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - FARMACIA'
        elif 'ENF' in n:
            return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - ENFERMAGEM'
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)'
    if any(k in n for k in ['IMUNO', 'INUNO', 'TRANSPLANT']):
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO'
    if any(k in n for k in ['PED', 'INFECTOPED', 'CRIANCA', 'NEONATAL']):
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA'
    if any(k in n for k in ['MULTI-R', 'MULTIR', 'MULTI R']):
        return 'JORNADA MULTI-R'
    if any(k in n for k in ['FUNGO', 'ANTIFUNGIC']):
        return 'DO FUNGO AO ANTIFUNGICO'
    if any(k in n for k in ['SOS', 'ANTIBIOTICO', 'ATB', 'MDR']):
        return 'S.O.S ANTIBIOTICO'
    if any(k in n for k in ['FERRAMENTA', 'QUALIDADE', 'ISHIKAWA', 'PDCA']):
        return 'FERRAMENTAS DE QUALIDADE'
    if any(k in n for k in ['INFECTOXPERT', 'EXPERT']):
        return 'INFECTOXPERT'
    if any(k in n for k in ['NUTRIFY']):
        return 'NUTRIFY CONNECT'
        
    return 'PLATAFORMA GERAL'
'''

for vp in vindi_paths:
    if os.path.exists(vp):
        with open(vp, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the normalize_vindi_course function definition
        content = re.sub(r'def normalize_vindi_course\(name\):.*?(?=\ndef get_vindi_data)', new_vindi_norm + '\n', content, flags=re.DOTALL)
        with open(vp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {vp}")

# 2. Delete cached vindi files so it refreshes with clean course names
cache_paths = [
    r'C:\Users\DELL\Desktop\Dash_InfectoCast\vindi_cache.json',
    r'C:\Users\DELL\Desktop\Acompanhamento de acessos\vindi_cache.json'
]
for cp in cache_paths:
    if os.path.exists(cp):
        os.remove(cp)
        print(f"Removed cache {cp}")

print("Vindi service update complete.")

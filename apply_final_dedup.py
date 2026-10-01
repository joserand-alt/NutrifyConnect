with open('gerador.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove earlier deduplication block
old_dedup_early = '''    # =========================================================================
    # DEDUPLICAÇÃO & UNIFICAÇÃO PERFEITA DE ESTUDANTES (1 REGISTRO POR ALUNO/CURSO)
    # =========================================================================
    unified_students_map = {}
    for s in students:
        em_clean = str(s.get('email', '')).lower().strip()
        c_clean = canonicalize_curso(str(s.get('curso', '')).strip(), em_clean)
        key = (em_clean, c_clean)
        
        if key not in unified_students_map:
            s_copy = dict(s)
            s_copy['curso'] = c_clean
            unified_students_map[key] = s_copy
        else:
            target = unified_students_map[key]
            nm_curr = str(s.get('nome', '')).strip()
            nm_targ = str(target.get('nome', '')).strip()
            if nm_curr and (not nm_targ or nm_targ == em_clean or (len(nm_curr) > len(nm_targ) and not nm_curr.isupper())):
                target['nome'] = nm_curr
            elif nm_curr and not nm_targ:
                target['nome'] = nm_curr
                
            if s.get('telefone') and not target.get('telefone'):
                target['telefone'] = s['telefone']
                
            if s.get('acessou'):
                target['acessou'] = True
            if (s.get('aulas_feitas') or 0) > (target.get('aulas_feitas') or 0):
                target['aulas_feitas'] = s['aulas_feitas']
            if (s.get('aulas_concluidas') or 0) > (target.get('aulas_concluidas') or 0):
                target['aulas_concluidas'] = s['aulas_concluidas']
            if (s.get('aulas_iniciadas') or 0) > (target.get('aulas_iniciadas') or 0):
                target['aulas_iniciadas'] = s['aulas_iniciadas']
            if (s.get('logins') or 0) > (target.get('logins') or 0):
                target['logins'] = s['logins']
            if (s.get('progresso') or 0) > (target.get('progresso') or 0):
                target['progresso'] = s['progresso']
                
            if s.get('vindi') and not target.get('vindi'):
                target['vindi'] = s['vindi']
            if s.get('asaas') and not target.get('asaas'):
                target['asaas'] = s['asaas']
                
            if len(s.get('events', []) or []) > len(target.get('events', []) or []):
                target['events'] = s['events']
                
            d1 = s.get('data_insc')
            d2 = target.get('data_insc')
            if d1 and d2:
                try:
                    p1 = pd.to_datetime(d1, dayfirst=True)
                    p2 = pd.to_datetime(d2, dayfirst=True)
                    if p1 < p2:
                        target['data_insc'] = d1
                        target['data_inscricao'] = d1
                        target['inscricao'] = d1
                except:
                    pass
            elif d1 and not d2:
                target['data_insc'] = d1
                target['data_inscricao'] = d1
                target['inscricao'] = d1

    students = list(unified_students_map.values())
    print(f'[UNIFICAÇÃO] Base final consolidada sem duplicatas: {len(students)} estudantes únicos.')'''

code = code.replace(old_dedup_early, '')

# 2. Insert deduplication right after auto-healing finishes
target_marker = "            s['curso_origem'] = 'Inferido'"
new_dedup_final = """            s['curso_origem'] = 'Inferido'

    # =========================================================================
    # DEDUPLICAÇÃO & UNIFICAÇÃO FINAL ABSOLUTA (1 REGISTRO ÚNICO POR ALUNO E CURSO)
    # =========================================================================
    unified_students_map = {}
    for s in students:
        em_clean = str(s.get('email', '')).lower().strip()
        c_clean = canonicalize_curso(str(s.get('curso', '')).strip(), em_clean)
        key = (em_clean, c_clean)
        
        if key not in unified_students_map:
            s_copy = dict(s)
            s_copy['curso'] = c_clean
            unified_students_map[key] = s_copy
        else:
            target = unified_students_map[key]
            nm_curr = str(s.get('nome', '')).strip()
            nm_targ = str(target.get('nome', '')).strip()
            if nm_curr and (not nm_targ or nm_targ == em_clean or (len(nm_curr) > len(nm_targ) and not nm_curr.isupper())):
                target['nome'] = nm_curr
            elif nm_curr and not nm_targ:
                target['nome'] = nm_curr
                
            if s.get('telefone') and not target.get('telefone'):
                target['telefone'] = s['telefone']
                
            if s.get('acessou'):
                target['acessou'] = True
            if (s.get('aulas_feitas') or 0) > (target.get('aulas_feitas') or 0):
                target['aulas_feitas'] = s['aulas_feitas']
            if (s.get('aulas_concluidas') or 0) > (target.get('aulas_concluidas') or 0):
                target['aulas_concluidas'] = s['aulas_concluidas']
            if (s.get('aulas_iniciadas') or 0) > (target.get('aulas_iniciadas') or 0):
                target['aulas_iniciadas'] = s['aulas_iniciadas']
            if (s.get('logins') or 0) > (target.get('logins') or 0):
                target['logins'] = s['logins']
            if (s.get('progresso') or 0) > (target.get('progresso') or 0):
                target['progresso'] = s['progresso']
                
            if s.get('vindi') and not target.get('vindi'):
                target['vindi'] = s['vindi']
            if s.get('asaas') and not target.get('asaas'):
                target['asaas'] = s['asaas']
                
            if len(s.get('events', []) or []) > len(target.get('events', []) or []):
                target['events'] = s['events']
                
            d1 = s.get('data_insc')
            d2 = target.get('data_insc')
            if d1 and d2:
                try:
                    p1 = pd.to_datetime(d1, dayfirst=True)
                    p2 = pd.to_datetime(d2, dayfirst=True)
                    if p1 < p2:
                        target['data_insc'] = d1
                        target['data_inscricao'] = d1
                        target['inscricao'] = d1
                except:
                    pass
            elif d1 and not d2:
                target['data_insc'] = d1
                target['data_inscricao'] = d1
                target['inscricao'] = d1

    students = list(unified_students_map.values())
    print(f'[UNIFICAÇÃO FINAL] Base final consolidada sem duplicatas: {len(students)} estudantes únicos.')"""

assert target_marker in code, 'target_marker not found'
code = code.replace(target_marker, new_dedup_final, 1)

with open('gerador.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('gerador.py updated with final deduplication!')

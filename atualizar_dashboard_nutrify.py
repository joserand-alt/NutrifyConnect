import urllib.request
import json
from concurrent.futures import ThreadPoolExecutor
import datetime
import unicodedata
import os
import re

TOKEN = 'idIsYOe8egEasc4xwhxmwu2uSZyWy3oEhWzE3kEHakhcPJzQpp7kGLmYrk7lcrMQ'
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'}

def norm(s):
    if not s:
        return ""
    nfkd = unicodedata.normalize('NFKD', str(s))
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

# Integração Dinâmica com a API do Academy (Modelo AcademyService do Dash_InfectoCast)
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "academy_curriculum_cache.json")

def fetch_curriculum_from_api(course_id=111):
    """
    Busca dinâmica de módulos e aulas diretamente na API InfectoCast Academy
    Modelo oficial utilizado no Dash_InfectoCast (GET /cursos/{id}/modulos e /aulas)
    """
    url_mods = f"https://academy.infectocast.com.br/api/cursos/{course_id}/modulos"
    try:
        req = urllib.request.Request(url_mods, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        raw_mods = data.get('data', data) if isinstance(data, dict) else data
        
        if not raw_mods or not isinstance(raw_mods, list):
            raise ValueError("Resposta de módulos vazia ou inválida")
            
        curriculum = []
        for m in raw_mods:
            mid = m.get('id')
            mnome = str(m.get('nome') or f"Módulo {mid}").strip()
            mord = m.get('ordem', 1)
            
            url_aulas = f"https://academy.infectocast.com.br/api/cursos/{course_id}/modulos/{mid}/aulas"
            try:
                req_a = urllib.request.Request(url_aulas, headers=HEADERS)
                with urllib.request.urlopen(req_a, timeout=12) as resp_a:
                    data_a = json.loads(resp_a.read().decode('utf-8'))
                raw_aulas = data_a.get('data', data_a) if isinstance(data_a, dict) else data_a
            except Exception as e_a:
                print(f"Aviso ao buscar aulas do módulo {mid}: {e_a}")
                raw_aulas = []
                
            aulas_list = []
            for a in raw_aulas:
                anome = str(a.get('nome') or "").strip()
                if not anome:
                    continue
                aord = a.get('ordem', 1)
                
                # Match patterns inteligentes baseados no nome da aula retornado pela API
                matches = [norm(anome)]
                norm_nome = norm(anome)
                if "DHA 1000" in norm_nome or "DHA1000" in norm_nome:
                    matches.extend(["DHA 1000", "DHA1000"])
                if "100% CREATINE" in norm_nome:
                    matches.extend(["100% CREATINE", "CREATINE 300G", "CREATINE 600G"])
                if "GLUTAMINA" in norm_nome or "GLUTAMINE" in norm_nome:
                    matches.extend(["GLUTAMINA", "GLUTAMINE"])
                if "VIT B COMPLEX" in norm_nome:
                    matches.extend(["VIT B COMPLEX", "VITB COMPLEX"])
                if "IMMUNE UP" in norm_nome or "IMUNE UP" in norm_nome:
                    matches.extend(["IMMUNE UP", "IMUNE UP", "IMUN UP"])
                if "PUREOX" in norm_nome or "PURE OX" in norm_nome:
                    matches.extend(["PUREOX", "PURE OX"])
                    
                aulas_list.append({
                    "id": a.get('id'),
                    "ordem": f"{aord}ª",
                    "nome": anome,
                    "curriculo": True,
                    "match": list(set(matches))
                })
                
            curriculum.append({
                "id": mid,
                "modulo": mnome,
                "ordem": mord,
                "aulas": aulas_list
            })
            
        # Salva em cache para redundância
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(curriculum, f, indent=2, ensure_ascii=False)
            
        print(f"[API] Currículo sincronizado ao vivo da API do Academy: {len(curriculum)} módulos, {sum(len(m['aulas']) for m in curriculum)} aulas.")
        return curriculum
    except Exception as e:
        print(f"[API] Falha ao consultar módulos na API ({e}). Tentando carregar cache local...")
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    if cached:
                        print(f"[Cache] Carregados {len(cached)} módulos do cache.")
                        return cached
            except Exception:
                pass
        return []

# Carregar currículo dinâmico ao vivo da API
MODULES_DEF = fetch_curriculum_from_api(course_id=111)
if not MODULES_DEF:
    # Fallback de segurança se offline
    MODULES_DEF = [
        {"modulo": "Ômegas", "aulas": [{"ordem": "1ª", "nome": "O que são os Ômegas e Por que são Importantes?", "curriculo": True, "match": ["O QUE SAO OS OMEGAS"]}]},
        {"modulo": "Creatinas", "aulas": [{"ordem": "1ª", "nome": "O que é Creatina e Por que é Importante?", "curriculo": True, "match": ["O QUE E CREATINA"]}]}
    ]

# Set of all lesson match patterns
ALL_NUTRI_PATTERNS = []
for m in MODULES_DEF:
    for a in m['aulas']:
        for pat in a['match']:
            ALL_NUTRI_PATTERNS.append((pat, a['nome'], m['modulo'], a['curriculo']))

NUTRI_GENERAL_KEYWORDS = [
    'NUTRIFY', 'CREATINE', 'CREATINA', 'MAGNESIUM INOSITOL', 'MAG 5 COMPLEX',
    'MULTI ALL', 'COLLAGEN', 'ARTROAID', 'DHA 1000', 'DHA1000', 'OMEGA 3', 'OMEGA BEAT',
    'HISTORIA DA NUTRIFY', 'FICHA TECNICA', 'LAMINA COMERCIAL', 'ANTIOXIDANTE', 'COENZIMA',
    'IMMUNE UP', 'PUREOX'
]

def identify_lesson(item_raw, comp_raw):
    it = norm(item_raw)
    co = norm(comp_raw)
    combined = f"{it} {co}"
    
    # Check exact/specific pattern match
    for pat, nome, modulo, curriculo in ALL_NUTRI_PATTERNS:
        # Avoid false positive with ADENOMEGALIAS
        if pat == 'OMEGA 3' and 'OMEGA 3' not in combined:
            continue
        if pat in it or pat in co:
            return {'nome': nome, 'modulo': modulo, 'curriculo': curriculo}
            
    # Check general keywords
    for kw in NUTRI_GENERAL_KEYWORDS:
        if kw in combined:
            return {'nome': item_raw or kw, 'modulo': 'Geral', 'curriculo': False}
            
    return None

def is_nutrify_event(item_raw, comp_raw, acao_raw):
    # Tests of Nutrify modules
    it = norm(item_raw)
    nutri_mod_tests = {'OMEGAS', 'CREATINAS', 'AMINOCIDOS', 'AMINOACIDOS', 'VITAMINAS E MINERAIS', 'COLAGENOS', 'ANTIOXIDANTES'}
    if 'TESTE' in norm(acao_raw) and it in nutri_mod_tests:
        return True
    return identify_lesson(item_raw, comp_raw) is not None

def fetch_aluno(uid):
    url_a = f'https://academy.infectocast.com.br/api/alunos/{uid}'
    url_l = f'https://academy.infectocast.com.br/api/alunos/{uid}/log'
    try:
        req_a = urllib.request.Request(url_a, headers=HEADERS)
        with urllib.request.urlopen(req_a, timeout=7) as resp:
            data_a = json.loads(resp.read().decode('utf-8'))
        aluno = data_a.get('data')
        if not aluno or not aluno.get('email'):
            return None
            
        req_l = urllib.request.Request(url_l, headers=HEADERS)
        with urllib.request.urlopen(req_l, timeout=9) as resp:
            data_l = json.loads(resp.read().decode('utf-8'))
        logs = data_l.get('data', [])
        return {'aluno': aluno, 'logs': logs}
    except Exception:
        return None

def parse_iso(d_str):
    if not d_str:
        return None
    # e.g. 2026-09-02T11:17:30.507 or 2026-05-29 16:31:00
    cleaned = d_str.replace('T', ' ')
    for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
        try:
            return datetime.datetime.strptime(cleaned, fmt)
        except Exception:
            pass
    return None

def generate_dashboard_from_api():
    print("Iniciando varredura 100% via API (sem arquivos Excel)...")
    
    # Query all students in parallel
    with ThreadPoolExecutor(max_workers=35) as ex:
        all_results = [r for r in ex.map(fetch_aluno, range(100001, 100350)) if r]
        
    print(f"Total de contas de alunos verificadas na API: {len(all_results)}")
    
    nutrify_candidates = []
    for item in all_results:
        aluno = item['aluno']
        logs = item['logs']
        email = aluno.get('email', '').strip().lower()
        
        # Strict corporate filter: only @nutrify or @integralmedica
        is_nutri_corporate = ('@nutrify' in email or '@integralmedica' in email)
        if not is_nutri_corporate:
            continue

        # Filter out test accounts
        if any(bad in email for bad in ['teste', 'rand', '@vector', '@infectocast']):
            continue
            
        # Check if student has ANY log in Nutrify
        nutri_logs = []
        for l in logs:
            acao = l.get('acao_evento', '')
            obj = l.get('item_objeto', '')
            comp = l.get('complemento', '')
            
            # If it's a login and user is a Nutrify student, keep login
            if is_nutrify_event(obj, comp, acao):
                nutri_logs.append(l)

        # Include all Nutrify logs + login events for activity tracking
        student_events = []
        for l in logs:
            acao = l.get('acao_evento', '')
            obj = l.get('item_objeto', '')
            comp = l.get('complemento', '')
            dt = parse_iso(l.get('data_hora'))
            
            is_n = is_nutrify_event(obj, comp, acao)
            is_login = ('LOGIN' in acao.upper())
            
            if is_n or is_login:
                student_events.append({
                    'dt': dt,
                    'data_hora_raw': l.get('data_hora', ''),
                    'acao': acao,
                    'item': obj,
                    'comp': comp,
                    'is_nutri': is_n
                })
                
        student_events.sort(key=lambda x: x['dt'] if x['dt'] else datetime.datetime.min, reverse=True)

        # Deduplicação: mesmo conteúdo + mesma ação + mesmo horário (minuto)
        seen_events = set()
        deduped_events = []
        for e in student_events:
            dt_min = e['dt'].strftime('%Y-%m-%d %H:%M') if e['dt'] else str(e['data_hora_raw'])[:16]
            dedup_key = (norm(e['acao']), norm(e['item']), dt_min)
            if dedup_key not in seen_events:
                seen_events.add(dedup_key)
                deduped_events.append(e)
        student_events = deduped_events

        nutrify_candidates.append({
            'aluno': aluno,
            'events': student_events,
            'nutri_event_count': len(nutri_logs)
        })

    print(f"Total de alunos inscritos no Nutrify identificados via API: {len(nutrify_candidates)}")
    
    # Process Metrics
    today = datetime.datetime.now()
    ref_date = today.date() + datetime.timedelta(days=1)
    
    students_output = []
    all_nutri_events = []
    
    for c in nutrify_candidates:
        aluno = c['aluno']
        evts = c['events']
        has_accessed = len(evts) > 0 and any(e['is_nutri'] for e in evts)
        
        # Determine enrollment date: date of first event, or today
        if evts:
            valid_dates = [e['dt'] for e in evts if e['dt']]
            first_dt = min(valid_dates) if valid_dates else today
            last_dt = max(valid_dates) if valid_dates else today
        else:
            first_dt = today
            last_dt = today
            
        data_insc_str = first_dt.strftime('%d/%m/%Y')
        last_fmt = last_dt.strftime('%d/%m/%Y')
        
        dias_ativo = float(max(0, (last_dt.date() - first_dt.date()).days))
        dias_inativo = float(max(0, (today.date() - last_dt.date()).days))
        
        # Modules progress
        completed_lessons = set()
        started_lessons = set()
        completed_modules = set()
        
        formatted_events = []
        logins_count = 0
        materiais_count = 0
        testes_count = 0
        
        for e in evts:
            acao = e['acao'].upper()
            obj = e['item']
            comp = e['comp']
            dt_fmt = e['dt'].strftime('%d/%m/%Y %H:%M') if e['dt'] else ''
            
            # Map category
            if 'LOGIN' in acao:
                cat = 'login'
                acao_label = 'Login'
                logins_count += 1
            elif 'CONCLUIU TESTE' in acao:
                cat = 'teste'
                acao_label = 'Concluiu teste'
                testes_count += 1
                completed_modules.add(norm(obj))
            elif 'REFAZER' in acao:
                cat = 'teste'
                acao_label = 'Refez teste'
                testes_count += 1
            elif 'CONCLUIU' in acao:
                cat = 'concluiu'
                acao_label = 'Concluiu aula'
            elif 'INICIOU' in acao:
                cat = 'iniciou'
                acao_label = 'Iniciou aula'
            elif 'PDF' in acao or 'MATERIAL' in acao:
                cat = 'material'
                acao_label = 'Baixou PDF'
                materiais_count += 1
            else:
                cat = 'material'
                acao_label = e['acao']
                
            info = identify_lesson(obj, comp)
            mod_nome = info['modulo'] if info else ''
            lesson_nome = info['nome'] if info else obj
            
            if cat == 'concluiu' and info:
                completed_lessons.add(info['nome'])
            elif cat == 'iniciou' and info:
                started_lessons.add(info['nome'])
                
            formatted_events.append({
                'd': dt_fmt,
                'acao': acao_label,
                'cat': cat,
                'item': lesson_nome or 'Conteúdo do curso',
                'mod': mod_nome
            })
            
            if e['is_nutri']:
                all_nutri_events.append(e)

        # Check module completions based on curriculum
        completed_mod_names = set()
        mods_status = {}
        for m in MODULES_DEF:
            m_name = m['modulo']
            curric_aulas = [a['nome'] for a in m['aulas'] if a['curriculo']]
            done_count = sum(1 for a_nome in curric_aulas if a_nome in completed_lessons)
            test_passed = any(norm(m_name) in norm(t) for t in completed_modules)
            is_mod_done = (done_count >= len(curric_aulas) and len(curric_aulas) > 0) or test_passed
            if is_mod_done:
                completed_mod_names.add(m_name)
            mods_status[m_name] = {
                'ativas': len(curric_aulas),
                'done': done_count,
                'concluido': is_mod_done
            }

        # Status calculation
        total_mods_count = len(MODULES_DEF)
        n_mods_done = len(completed_mod_names)
        pct_mods = round((n_mods_done / total_mods_count) * 100, 1)
        
        # Calculate cadência
        if logins_count > 1 and dias_ativo > 0:
            cadencia = dias_ativo / (logins_count - 1)
        else:
            cadencia = 7.0

        if not has_accessed or len(formatted_events) == 0:
            status = "Nunca acessou"
            status_motivo = "Conta cadastrada na plataforma, mas sem nenhuma atividade no log"
        elif n_mods_done >= total_mods_count:
            status = "Concluído"
            status_motivo = "Concluiu todos os módulos disponíveis do curso"
        elif (logins_count > 1 and dias_ativo > 0 and (dias_inativo > 30 or (dias_inativo > 14 and dias_inativo > cadencia * 2.5))) or ((logins_count <= 1 or dias_ativo == 0) and dias_inativo > 14):
            status = "Abandonou"
            status_motivo = f"Inatividade severa: {int(dias_inativo)} dias sem acessar a plataforma"
        elif (logins_count > 1 and dias_ativo > 0 and dias_inativo > (cadencia * 1.5 + 2)) or ((logins_count <= 1 or dias_ativo == 0) and dias_inativo > 7):
            status = "Em Risco"
            status_motivo = f"Quebra de cadência: {int(dias_inativo)} dias sem acesso (média habitual: {round(cadencia, 1)} dias)"
        elif len(completed_lessons) == 0:
            status = "Apenas Login"
            status_motivo = f"Acessou a plataforma recentemente ({logins_count} login(s)), mas ainda não iniciou as aulas"
        else:
            status = "Ativo"
            status_motivo = f"Em andamento e com acesso recente ({len(completed_lessons)} aulas feitas, {n_mods_done}/{total_mods_count} módulos)"

        students_output.append({
            "id": aluno['id'],
            "email": aluno['email'],
            "nome": aluno['nome'],
            "curso": "Nutrify Connect",
            "acessou": has_accessed,
            "data_insc": data_insc_str,
            "mods_concluidos": n_mods_done,
            "mods_concl_nomes": list(completed_modules),
            "total_mods": total_mods_count,
            "pct_mods": pct_mods,
            "eventos": len(formatted_events),
            "events": formatted_events,
            "first": first_dt.strftime('%Y-%m-%d'),
            "last": last_dt.strftime('%Y-%m-%d'),
            "last_fmt": last_fmt,
            "dias_ativo": dias_ativo,
            "dias_inativo": dias_inativo,
            "cadencia": round(cadencia, 1),
            "logins": logins_count,
            "aulas_iniciadas": len(started_lessons),
            "aulas_concluidas": len(completed_lessons),
            "materiais": materiais_count,
            "testes": testes_count,
            "mods": mods_status,
            "lag": 0.0,
            "status": status,
            "status_motivo": status_motivo,
            "aulas_feitas": len(completed_lessons)
        })

    # Sort students by last active date desc
    students_output.sort(key=lambda s: (s['acessou'], s['mods_concluidos'], s['aulas_feitas'], s['last'] if s['acessou'] else ''), reverse=True)
    
    # Generate action_counts
    action_counts = {
        'Concluiu aula': sum(s['aulas_concluidas'] for s in students_output),
        'Iniciou aula': sum(s['aulas_iniciadas'] for s in students_output),
        'Login': sum(s['logins'] for s in students_output),
        'Baixou PDF': sum(s['materiais'] for s in students_output),
        'Concluiu teste': sum(s['testes'] for s in students_output),
        'CONCLUIU AULA': sum(s['aulas_concluidas'] for s in students_output),
        'INICIOU AULA': sum(s['aulas_iniciadas'] for s in students_output),
        'LOGIN WEB': sum(s['logins'] for s in students_output),
        'BAIXOU MATERIAL PDF': sum(s['materiais'] for s in students_output),
        'CONCLUIU TESTE/MÓDULO': sum(s['testes'] for s in students_output)
    }

    n_inscritos = len(students_output)
    n_acessaram = sum(1 for s in students_output if s['acessou'])
    n_nunca = n_inscritos - n_acessaram

    meta = {
        "generated": today.strftime("%d/%m/%Y %H:%M"),
        "report_start": min((s['first'] for s in students_output), default=today.strftime("%d/%m/%Y")),
        "date_max": max((s['last'] for s in students_output), default=today.strftime("%d/%m/%Y")),
        "ref_date": ref_date.strftime("%d/%m/%Y"),
        "n_inscritos": n_inscritos,
        "n_acessaram": n_acessaram,
        "n_nunca_acessou": n_nunca,
        "taxa_acesso": round((n_acessaram / n_inscritos * 100), 1) if n_inscritos else 0.0,
        "n_eventos": sum(s['eventos'] for s in students_output),
        "total_mods": len(MODULES_DEF),
        "n_curric": sum(len([a for a in m['aulas'] if a['curriculo']]) for m in MODULES_DEF),
        "total_aulas_feitas": sum(s['aulas_feitas'] for s in students_output),
        "total_logins": action_counts['Login'],
        "total_materiais": action_counts['Baixou PDF']
    }

    modules_ref = []
    for m in MODULES_DEF:
        m_aulas = []
        for idx, a in enumerate(m['aulas']):
            m_aulas.append({
                "id": idx + 1,
                "ordem": a['ordem'],
                "nome": a['nome'],
                "iniciou": sum(1 for s in students_output if a['nome'] in [e['item'] for e in s['events'] if e['cat'] == 'iniciou']),
                "concluiu": sum(1 for s in students_output if a['nome'] in [e['item'] for e in s['events'] if e['cat'] == 'concluiu']),
                "curriculo": a['curriculo'],
                "reason": None if a['curriculo'] else "complementar"
            })
        concl_mod = sum(1 for s in students_output if s['mods'].get(m['modulo'], {}).get('concluido'))
        modules_ref.append({
            "modulo": m['modulo'],
            "n_curric": len([a for a in m['aulas'] if a['curriculo']]),
            "n_fora": len([a for a in m['aulas'] if not a['curriculo']]),
            "aulas": m_aulas,
            "alunos_concluiram": concl_mod
        })

    DATA = {
        "meta": meta,
        "action_counts": action_counts,
        "timeline": [],
        "timeline_wk": [],
        "survival": [],
        "modules_ref": modules_ref,
        "students": students_output,
        "curriculum": {
            "Nutrify Connect": modules_ref
        }
    }

    dash_files = [
        'index.html',
        'nutrify_connect_dashboard.html',
        r'c:\Users\DELL\Desktop\Acompanhamento de acessos\index.html',
        r'c:\Users\DELL\Desktop\Acompanhamento de acessos\nutrify_connect_dashboard.html',
        r'C:\Users\DELL\.gemini\antigravity-ide\scratch\lead-management-system\dashboard_gerado.html',
        r'C:\Users\DELL\.gemini\antigravity-ide\scratch\lead-management-system\nutrify_connect_dashboard.html'
    ]

    start_str = "const DATA = "
    json_str = json.dumps(DATA, ensure_ascii=False)

    for dpath in dash_files:
        if not os.path.exists(dpath):
            continue
        with open(dpath, 'r', encoding='utf-8') as f:
            html = f.read()
            
        start_idx = html.find(start_str)
        if start_idx == -1:
            print(f"Não encontrou 'const DATA = ' em {dpath}")
            continue
            
        # Find closing };
        end_idx = html.find("};\n", start_idx)
        if end_idx == -1:
            end_idx = html.find("};", start_idx)
            
        pre = html[:start_idx + len(start_str)]
        post = html[end_idx + 1:]
        
        new_html = pre + json_str + post
        
        with open(dpath, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f"Atualizado com sucesso a partir da API: {dpath}")

    print("\n[OK] Dashboard gerado com sucesso exclusivamente via API de logs!")
    print(f"Total de alunos inscritos detectados: {n_inscritos} ({n_acessaram} acessaram, {n_nunca} nunca acessaram)")

if __name__ == '__main__':
    generate_dashboard_from_api()

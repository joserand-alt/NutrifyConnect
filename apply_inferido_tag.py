import os, re

# ==========================================
# 1. Update gerador.py
# ==========================================
gerador_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'
with open(gerador_file, 'r', encoding='utf-8') as f:
    g_code = f.read()

# Update _infer_curso_from_asaas to return tuple (curso, is_inferred, origin)
old_infer_block = """        def _infer_curso_from_asaas(asaas_st, email):
            \"\"\"Tenta resolver o curso do aluno Asaas usando student_course_map, RD Station ou descrição da fatura.\"\"\"
            # 1. Verifica student_course_map (logs + planilhas)
            if email in student_course_map:
                return student_course_map[email]
            
            # 2. Verifica dicas do RD Station (Tags e Eventos)
            if 'rd_course_hints' in locals() and email in rd_course_hints:
                return rd_course_hints[email]
            
            # 2. Infere pelo valor total do plano (padrão de preços dos cursos)
            total = asaas_st.get('total_bruto') or 0
            if total <= 0:
                # Calcula total bruto a partir das faturas
                faturas = asaas_st.get('faturas', [])
                if faturas:
                    total = sum(f.get('valor', 0) for f in faturas)
            
            # 3. Tenta pela descrição do pagamento
            faturas = asaas_st.get('faturas', [])
            desc_text = ''
            for ft in faturas:
                d = ft.get('description', ft.get('descricao', ''))
                if d and d != 'N/A':
                    desc_text += ' ' + str(d).upper()
            
            desc_norm = desc_text.replace('Ã', 'A').replace('Ç', 'C').replace('Õ', 'O').replace('É', 'E').replace('Í', 'I')
            
            if any(w in desc_norm for w in ['CCIH', 'INFECCAO HOSPITALAR', 'PREVENCAO']):
                return normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)')
            if any(w in desc_norm for w in ['INFECTOPED', 'PEDIATRIA']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA')
            if any(w in desc_norm for w in ['ORTOPED', 'PARTES MOLES']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES')
            if any(w in desc_norm for w in ['SOS', 'ANTIBIOTICO', 'ATB']):
                return normalize_curso('S.O.S ANTIBIÓTICO')
            if any(w in desc_norm for w in ['FERRAMENTA', 'QUALIDADE']):
                return normalize_curso('FERRAMENTAS DE QUALIDADE')
            if any(w in desc_norm for w in ['IMUNODEPRIMIDO']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS')
            
            # 4. Infere pelo valor total (preços conhecidos dos cursos)
            # Cursos de pós-graduação: ~R$2.187 (total)
            # SOS ATB: ~R$487 (total)
            # Ferramentas: valores menores
            # Não é possível distinguir apenas pelo valor qual pós-graduação
            
            return "PLATAFORMA GERAL" """

new_infer_block = """        def _infer_curso_from_asaas(asaas_st, email):
            \"\"\"Tenta resolver o curso do aluno Asaas usando student_course_map, RD Station ou descrição da fatura.
            Retorna: (curso_nome, is_inferred, origem_str)\"\"\"
            # 1. Verifica student_course_map (logs + planilhas) -> OFICIAL (não inferido)
            if email in student_course_map:
                return student_course_map[email], False, "Oficial"
            
            # 2. Verifica dicas do RD Station (Tags e Eventos de Leads) -> INFERIDO
            if 'rd_course_hints' in locals() and email in rd_course_hints:
                return rd_course_hints[email], True, "RD Station"
            
            # 3. Tenta pela descrição do pagamento
            faturas = asaas_st.get('faturas', [])
            desc_text = ''
            for ft in faturas:
                d = ft.get('description', ft.get('descricao', ''))
                if d and d != 'N/A':
                    desc_text += ' ' + str(d).upper()
            
            desc_norm = desc_text.replace('Ã', 'A').replace('Ç', 'C').replace('Õ', 'O').replace('É', 'E').replace('Í', 'I')
            
            if any(w in desc_norm for w in ['CCIH', 'INFECCAO HOSPITALAR', 'PREVENCAO']):
                return normalize_curso('PÓS-GRADUAÇÃO EM PREVENÇÃO E CONTROLE DE INFECÇÃO HOSPITALAR (CCIH)'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['INFECTOPED', 'PEDIATRIA']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECTOPEDIATRIA'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['ORTOPED', 'PARTES MOLES']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES ORTOPÉDICAS E DE PARTES MOLES'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['SOS', 'ANTIBIOTICO', 'ATB']):
                return normalize_curso('S.O.S ANTIBIÓTICO'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['FERRAMENTA', 'QUALIDADE']):
                return normalize_curso('FERRAMENTAS DE QUALIDADE'), True, "Fatura Asaas"
            if any(w in desc_norm for w in ['IMUNODEPRIMIDO']):
                return normalize_curso('PÓS-GRADUAÇÃO EM INFECÇÕES EM IMUNODEPRIMIDOS'), True, "Fatura Asaas"
            
            return "PLATAFORMA GERAL", False, "Geral" """

# In case formatting or encoding differs, let's replace via regex
pattern_infer = r'def _infer_curso_from_asaas\(asaas_st, email\):[\s\S]*?return "PLATAFORMA GERAL"'
match = re.search(pattern_infer, g_code)
if match:
    g_code = g_code[:match.start()] + new_infer_block.strip() + g_code[match.end():]
    print("Updated _infer_curso_from_asaas successfully!")
else:
    print("Could not match _infer_curso_from_asaas pattern.")

# Update new_st creation in gerador.py
old_new_st = """            if st_email and st_email not in existing_emails:
                existing_emails.add(st_email)
                curso_resolved = _infer_curso_from_asaas(asaas_st, st_email)
                new_st = {
                    "email": st_email,
                    "nome": asaas_st.get('customer_name') or 'Aluno Academy',
                    "curso": curso_resolved,
                    "telefone": "",
                    "acessou": False,
                    "data_insc": None,
                    "data_inscricao": None,
                    "inscricao": None,
                    "dias_desde_insc": 0,
                    "plataforma": "Academy",
                    "id_aluno": str(asaas_st.get('aluno_id_extref', '')),
                    "events": [],
                    "vindi": None,
                    "asaas": asaas_st
                }
                if 'rd_events_map' in locals() and st_email in rd_events_map:
                    new_st['rd_funnel'] = dict(rd_events_map[st_email])
                students.append(new_st)
                if curso_resolved != "PLATAFORMA GERAL":
                    print(f"  [ASAAS] Curso resolvido para {st_email}: {curso_resolved}")
                added_from_api += 1
                asaas_matched += 1"""

new_new_st = """            if st_email and st_email not in existing_emails:
                existing_emails.add(st_email)
                curso_resolved, curso_inferido, curso_origem = _infer_curso_from_asaas(asaas_st, st_email)
                new_st = {
                    "email": st_email,
                    "nome": asaas_st.get('customer_name') or 'Aluno Academy',
                    "curso": curso_resolved,
                    "curso_inferido": curso_inferido,
                    "curso_origem": curso_origem,
                    "telefone": "",
                    "acessou": False,
                    "data_insc": None,
                    "data_inscricao": None,
                    "inscricao": None,
                    "dias_desde_insc": 0,
                    "plataforma": "Academy",
                    "id_aluno": str(asaas_st.get('aluno_id_extref', '')),
                    "events": [],
                    "vindi": None,
                    "asaas": asaas_st
                }
                if 'rd_events_map' in locals() and st_email in rd_events_map:
                    new_st['rd_funnel'] = dict(rd_events_map[st_email])
                students.append(new_st)
                if curso_resolved != "PLATAFORMA GERAL":
                    tag_info = f" (INFERIDO via {curso_origem})" if curso_inferido else ""
                    print(f"  [ASAAS] Curso resolvido para {st_email}: {curso_resolved}{tag_info}")
                added_from_api += 1
                asaas_matched += 1"""

pattern_new_st = r'if st_email and st_email not in existing_emails:[\s\S]*?asaas_matched \+= 1'
match_st = re.search(pattern_new_st, g_code)
if match_st:
    g_code = g_code[:match_st.start()] + new_new_st.strip() + g_code[match_st.end():]
    print("Updated new_st creation in gerador.py successfully!")
else:
    print("Could not match new_st pattern.")

# Also ensure default curso_inferido on existing students
if "for s in students:\n        s.setdefault('curso_inferido', False)" not in g_code:
    g_code = g_code.replace(
        "    data = {\n        \"meta\": {",
        "    for s in students:\n        s.setdefault('curso_inferido', False)\n        s.setdefault('curso_origem', 'Oficial')\n\n    data = {\n        \"meta\": {"
    )
    print("Added default curso_inferido for all students!")

with open(gerador_file, 'w', encoding='utf-8') as f:
    f.write(g_code)


# ==========================================
# 2. Update template.html
# ==========================================
template_file = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'
with open(template_file, 'r', encoding='utf-8') as f:
    t_code = f.read()

# 2.1 Add .badge-inferido CSS
css_badge = """.badge-inferido {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 600;
  padding: 1.5px 7px;
  border-radius: 12px;
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
  border: 1px solid rgba(245, 158, 11, 0.3);
  white-space: nowrap;
  vertical-align: middle;
  cursor: help;
}"""

if ".badge-inferido" not in t_code:
    t_code = t_code.replace(".badge{", css_badge + "\n.badge{", 1)
    print("Added .badge-inferido CSS!")

# 2.2 Add getCursoBadge function
js_get_curso_badge = """function getCursoBadge(s) {
  if (!s || !s.curso_inferido) return '';
  const orig = s.curso_origem || 'RD Station';
  return `<span class="badge-inferido" title="Curso deduzido através de ${orig}. Será atualizado automaticamente assim que houver registro oficial ou acesso às aulas na plataforma.">✨ Inferido (${orig})</span>`;
}"""

if "function getCursoBadge" not in t_code:
    # Insert right before getPlatBadge or getFinBadge
    if "function getPlatBadge" in t_code:
        t_code = t_code.replace("function getPlatBadge", js_get_curso_badge + "\nfunction getPlatBadge", 1)
        print("Added getCursoBadge function!")
    elif "function getFinBadge" in t_code:
        t_code = t_code.replace("function getFinBadge", js_get_curso_badge + "\nfunction getFinBadge", 1)
        print("Added getCursoBadge function!")

# 2.3 Update student row rendering in template.html (around line 1927)
old_td_curso = """<td style="font-size:11.5px;color:var(--muted);white-space:nowrap;max-width:140px;overflow:hidden;text-overflow:ellipsis" title="${s.curso}">${s.curso}</td>"""
new_td_curso = """<td style="font-size:11.5px;color:var(--muted);white-space:nowrap;max-width:160px;overflow:hidden;text-overflow:ellipsis" title="${s.curso}">${s.curso} ${getCursoBadge(s)}</td>"""

if old_td_curso in t_code:
    t_code = t_code.replace(old_td_curso, new_td_curso, 1)
    print("Updated student row course td!")
else:
    # Try regex match for course cell in student row
    pattern_td = r'<td style="font-size:11\.5px;color:var\(--muted\);white-space:nowrap;max-width:\d+px;overflow:hidden;text-overflow:ellipsis" title="\$\{s\.curso\}">\$\{s\.curso\}</td>'
    t_code = re.sub(pattern_td, new_td_curso, t_code, count=1)
    print("Updated student row course td via regex!")

# 2.4 Update student modal header (openStudent)
# In #md-stats
old_md_stats = "['Status',statusDisplay],['Módulos',`${s.mods_concluidos||0}/${s.total_mods||0}`]"
# Let's search with regex for md-stats
pattern_stats = r"\['Status',statusDisplay\],\s*\[(?:'Módulos'|'M.*?dulos'),`\$\{s\.mods_concluidos\|\|0\}/\$\{s\.total_mods\|\|0\}`\]"
match_stats = re.search(pattern_stats, t_code)
if match_stats:
    new_stats_item = "['Status',statusDisplay],['Curso',`${s.curso || 'Sem Curso'} ${getCursoBadge(s)}`],['Módulos',`${s.mods_concluidos||0}/${s.total_mods||0}`]"
    t_code = t_code[:match_stats.start()] + new_stats_item + t_code[match_stats.end():]
    print("Updated openStudent #md-stats!")

# 2.5 Update #modal-list (openModalList)
old_ml_curso = """<b style="color:var(--muted2)">Curso:</b> ${s.curso}<br>"""
new_ml_curso = """<b style="color:var(--muted2)">Curso:</b> ${s.curso} ${getCursoBadge(s)}<br>"""
if old_ml_curso in t_code:
    t_code = t_code.replace(old_ml_curso, new_ml_curso)
    print("Updated modal-list course line!")

# 2.6 Update Financial table (renderFinanceiroTable)
old_fin_curso = """<td style="padding:10px 8px; font-size:11.5px; color:var(--muted); max-width:180px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${st.curso}">${st.curso}</td>"""
new_fin_curso = """<td style="padding:10px 8px; font-size:11.5px; color:var(--muted); max-width:190px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${st.curso}">${st.curso} ${st.curso_inferido ? '<span class="badge-inferido" style="font-size:9.5px;padding:1px 5px" title="Inferido via ' + (st.curso_origem || 'RD') + '">✨ Inferido (' + (st.curso_origem || 'RD') + ')</span>' : ''}</td>"""

if old_fin_curso in t_code:
    t_code = t_code.replace(old_fin_curso, new_fin_curso)
    print("Updated financial table course td!")

# 2.7 Update Origem table
old_orig_curso = """<td style="padding:10px 8px; font-weight:500; color:var(--ink)">${s.curso}</td>"""
new_orig_curso = """<td style="padding:10px 8px; font-weight:500; color:var(--ink)">${s.curso} ${getCursoBadge(s)}</td>"""

if old_orig_curso in t_code:
    t_code = t_code.replace(old_orig_curso, new_orig_curso)
    print("Updated origem table course td!")

with open(template_file, 'w', encoding='utf-8') as f:
    f.write(t_code)

print("Saved template.html successfully!")

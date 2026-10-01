with open('template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update getMatriculasAuditoriaData pending date resolution
old_aud_pend = '''        if (isPendente) {
            const rawInscStr = s.data_insc || s.data_inscricao || s.data_matricula || s.first || (s.asaas && s.asaas.faturas && s.asaas.faturas[0] && (s.asaas.faturas[0].data_criacao || s.asaas.faturas[0].dateCreated || s.asaas.faturas[0].vencimento_iso || s.asaas.faturas[0].vencimento)) || (s.vindi && s.vindi.faturas && s.vindi.faturas[0] && (s.vindi.faturas[0].vencimento_iso || s.vindi.faturas[0].vencimento)) || s.created_at;
            const dtInsc = parseDateUniversal(rawInscStr);
            if (dtInsc && dtInsc <= now) {'''

new_aud_pend = '''        if (isPendente) {
            const dtCandidates = [
                s.data_insc, s.data_inscricao, s.data_matricula, s.first, s.created_at
            ];
            if (s.asaas && s.asaas.faturas) {
                s.asaas.faturas.forEach(f => {
                    dtCandidates.push(f.data_pagamento, f.data_pagamento_iso, f.data_criacao, f.dateCreated, f.vencimento_iso, f.vencimento);
                });
            }
            if (s.vindi && s.vindi.faturas) {
                s.vindi.faturas.forEach(f => {
                    dtCandidates.push(f.data_pagamento, f.data_pagamento_iso, f.vencimento_iso, f.vencimento);
                });
            }
            let dtInsc = null;
            const validDates = dtCandidates.map(parseDateUniversal).filter(d => d && d <= now);
            if (validDates.length > 0) {
                validDates.sort((a, b) => a - b);
                dtInsc = validDates[0];
            } else {
                dtInsc = parseDateUniversal(s.data_insc || s.data_inscricao || s.first);
                if (!dtInsc || dtInsc > now) dtInsc = now;
            }
            if (dtInsc && dtInsc <= now) {'''

# 2. Update allEnrichedStudents in renderCursoView to deduplicate rawStudents
old_raw_st = '''    // Enriquecimento Robusto da Base Completa de Alunos
    const rawStudents = (DATA && DATA.students) ? DATA.students.filter(s => !isInvalidOrInternal(s)) : [];
    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};

    const allEnrichedStudents = rawStudents.map(s => {'''

new_raw_st = '''    // Enriquecimento Robusto e Deduplicação da Base Completa de Alunos
    const rawStudents = (DATA && DATA.students) ? DATA.students.filter(s => !isInvalidOrInternal(s)) : [];
    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};

    const dedupRawMap = new Map();
    rawStudents.forEach(s => {
        const em = (s.email || '').toLowerCase().trim();
        const cCan = resolveCanonicalCourse(s.curso);
        const k = em + '___' + cCan;
        if (!dedupRawMap.has(k)) {
            dedupRawMap.set(k, { ...s });
        } else {
            const exist = dedupRawMap.get(k);
            if (s.nome && (!exist.nome || exist.nome === em || (s.nome.length > exist.nome.length && !s.nome.toUpperCase().includes(s.nome)))) {
                exist.nome = s.nome;
            }
            if (s.acessou) exist.acessou = true;
            if ((s.aulas_feitas || 0) > (exist.aulas_feitas || 0)) exist.aulas_feitas = s.aulas_feitas;
            if ((s.aulas_concluidas || 0) > (exist.aulas_concluidas || 0)) exist.aulas_concluidas = s.aulas_concluidas;
            if ((s.aulas_iniciadas || 0) > (exist.aulas_iniciadas || 0)) exist.aulas_iniciadas = s.aulas_iniciadas;
            if ((s.logins || 0) > (exist.logins || 0)) exist.logins = s.logins;
            if ((s.progresso || 0) > (exist.progresso || 0)) exist.progresso = s.progresso;
            if (s.vindi && !exist.vindi) exist.vindi = s.vindi;
            if (s.asaas && !exist.asaas) exist.asaas = s.asaas;
            if ((s.events || []).length > (exist.events || []).length) exist.events = s.events;
            if (s.data_insc && !exist.data_insc) exist.data_insc = s.data_insc;
        }
    });
    const uniqueRawStudents = Array.from(dedupRawMap.values());

    const allEnrichedStudents = uniqueRawStudents.map(s => {'''

# 3. Update parseEnrollDate in renderCursoView
old_parse_enroll = '''    const parseEnrollDate = (s) => {
        if (!s) return null;
        if (s.matricula_data instanceof Date && !isNaN(s.matricula_data.getTime())) return s.matricula_data;
        const dtStr = (s.data_insc || s.data_inscricao || s.inscricao || s.data_matricula || '').toString().trim();
        if (!dtStr) return null;
        if (dtStr.includes('/')) {
            const p = dtStr.split('/');
            if (p.length === 3) {
                const yr = parseInt(p[2].length === 2 ? '20' + p[2] : p[2], 10);
                return new Date(yr, parseInt(p[1], 10) - 1, parseInt(p[0], 10));
            }
        } else if (dtStr.includes('-')) {
            const p = dtStr.slice(0, 10).split('-');
            if (p.length === 3) {
                return new Date(parseInt(p[0], 10), parseInt(p[1], 10) - 1, parseInt(p[2], 10));
            }
        }
        const d = new Date(dtStr);
        return isNaN(d.getTime()) ? null : d;
    };'''

new_parse_enroll = '''    const parseEnrollDate = (s) => {
        if (!s) return null;
        if (s.matricula_data instanceof Date && !isNaN(s.matricula_data.getTime()) && s.matricula_data <= now) return s.matricula_data;
        const dtStr = (s.data_insc || s.data_inscricao || s.inscricao || s.data_matricula || s.first || '').toString().trim();
        const d = parseDateUniversal(dtStr);
        if (d && d <= now) return d;
        if (s.first) {
            const dFirst = parseDateUniversal(s.first);
            if (dFirst && dFirst <= now) return dFirst;
        }
        return (d && d <= now) ? d : null;
    };'''

# 4. Update table cell for MATRÍCULA
old_td_mat = '''                      <td style="padding:10px 14px; color:var(--ink)">
                        ${s.data_insc || s.data_inscricao || s.inscricao || '-'}
                      </td>'''

new_td_mat = '''                      <td style="padding:10px 14px; color:var(--ink)">
                        ${(() => {
                            const d = parseEnrollDate(s);
                            if (d) {
                                const pad = n => n < 10 ? '0' + n : n;
                                return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + '/' + d.getFullYear();
                            }
                            const raw = (s.data_insc || s.data_inscricao || s.inscricao || '').toString().trim();
                            if (raw.includes('-')) {
                                const p = raw.slice(0, 10).split('-');
                                if (p.length === 3) return p[2] + '/' + p[1] + '/' + p[0];
                            }
                            return raw || '-';
                        })()}
                      </td>'''

assert old_aud_pend in html, 'old_aud_pend not found'
assert old_raw_st in html, 'old_raw_st not found'
assert old_parse_enroll in html, 'old_parse_enroll not found'
assert old_td_mat in html, 'old_td_mat not found'

html = html.replace(old_aud_pend, new_aud_pend)
html = html.replace(old_raw_st, new_raw_st)
html = html.replace(old_parse_enroll, new_parse_enroll)
html = html.replace(old_td_mat, new_td_mat)

with open('template.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('template.html patched successfully!')

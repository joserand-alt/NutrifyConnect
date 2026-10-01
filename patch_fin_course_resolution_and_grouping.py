import os
import re

template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update _resolveFinCourse function
new_resolve_fin_course = """function _resolveFinCourse(f) {
    if (!f) return 'PLATAFORMA GERAL';
    if (f.curso && f.curso !== 'PLATAFORMA GERAL' && f.curso !== 'None' && f.curso !== 'SEM CURSO' && !f.curso.startsWith('Fatura Avulsa')) {
        return f.curso;
    }

    const plano = (f.plano || f._plano || f.description || f.descricao || '').toString();
    const textFull = plano.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');

    // 1. Inferir PRIMEIRO a partir do plano / descrição da própria fatura
    if (textFull.includes('ortop') || textFull.includes('partes moles') || textFull.includes('pele') || textFull.includes('musculo')) {
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PARTES MOLES';
    }
    if (textFull.includes('imuno') || textFull.includes('inuno') || textFull.includes('transplante')) {
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
    }
    if (textFull.includes('ccih') || textFull.includes('prevencao') || textFull.includes('hospitalar') || textFull.includes('pav') || textFull.includes('isc')) {
        if (textFull.includes('farm')) return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - FARMACIA';
        if (textFull.includes('enf')) return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH) - ENFERMAGEM';
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
    }
    if (textFull.includes('pediatria') || textFull.includes('infectoped') || textFull.includes('ped')) {
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
    }
    if (textFull.includes('multi-r') || textFull.includes('multi r') || textFull.includes('multir')) {
        return 'JORNADA MULTI-R';
    }
    if (textFull.includes('fungo') || textFull.includes('antifung')) {
        return 'DO FUNGO AO ANTIFUNGICO';
    }
    if (textFull.includes('s.o.s') || textFull.includes('sos') || textFull.includes('antibiotico') || textFull.includes('atb') || textFull.includes('mdr')) {
        return 'S.O.S ANTIBIOTICO';
    }
    if (textFull.includes('qualidade') || textFull.includes('ferramenta') || textFull.includes('ishikawa') || textFull.includes('pdca')) {
        return 'FERRAMENTAS DE QUALIDADE';
    }
    if (textFull.includes('expert')) {
        return 'INFECTOXPERT';
    }

    // 2. Fallback para aluno na plataforma
    const email = (f.email || f._email || '').toString().toLowerCase().trim();
    const aluno = (f.aluno || f._aluno || '').toString().toLowerCase().trim();
    const stList = (CURRENT_DATA && CURRENT_DATA.students) ? CURRENT_DATA.students : (DATA && DATA.students ? DATA.students : []);
    let stMatch = null;
    if (email) {
        stMatch = stList.find(s => s.email && s.email.toLowerCase().trim() === email && s.curso !== 'PLATAFORMA GERAL');
    }
    if (stMatch && stMatch.curso && stMatch.curso !== 'PLATAFORMA GERAL') {
        return stMatch.curso;
    }

    return 'PLATAFORMA GERAL';
}"""

pattern_resolve = r'function _resolveFinCourse\(f\) \{.*?\n\}'
match_resolve = re.search(pattern_resolve, html, re.DOTALL)
if match_resolve:
    html = html[:match_resolve.start()] + new_resolve_fin_course + html[match_resolve.end():]
    print("Updated _resolveFinCourse in template.html!")
else:
    print("Could not find _resolveFinCourse pattern.")

# 2. Update renderFinTable grouping and toggle button to use key = `${email}___${curso}`
old_grouping = """        // Agrupar faturas por aluno (email ou nome)
        const byStudent = {};
        faturas.forEach(f => {
            const email = (f._email || f.email || '').toLowerCase().trim();
            const aluno = f._aluno || f.aluno || 'Aluno';
            const curso = f.curso || _resolveFinCourse(f) || 'PLATAFORMA GERAL';
            const key = email || aluno;
            if (!byStudent[key]) {
                byStudent[key] = {
                    aluno: aluno,
                    email: email,
                    curso: curso,
                    gateway: f.gateway || (String(f.id||'').startsWith('pay_') ? 'Asaas' : 'Vindi'),
                    total: 0.0,
                    total_atraso: 0.0,
                    max_dias_atraso: 0,
                    has_atraso: false,
                    faturas: []
                };
            }"""

new_grouping = """        // Agrupar faturas por aluno E curso (para não misturar matrículas diferentes)
        const byStudent = {};
        faturas.forEach(f => {
            const email = (f._email || f.email || '').toLowerCase().trim();
            const aluno = f._aluno || f.aluno || 'Aluno';
            const curso = f.curso || _resolveFinCourse(f) || 'PLATAFORMA GERAL';
            const key = `${email}___${curso}`;
            if (!byStudent[key]) {
                byStudent[key] = {
                    key: key,
                    aluno: aluno,
                    email: email,
                    curso: curso,
                    gateway: f.gateway || (String(f.id||'').startsWith('pay_') ? 'Asaas' : 'Vindi'),
                    total: 0.0,
                    total_atraso: 0.0,
                    max_dias_atraso: 0,
                    has_atraso: false,
                    faturas: []
                };
            }"""

if old_grouping in html:
    html = html.replace(old_grouping, new_grouping)
    print("Updated byStudent grouping!")
else:
    print("Could not find exact old_grouping pattern.")

# Update toggle calls to use st.key
html = html.replace(
    "const isExpanded = _finExpandedStudents.has(st.email);",
    "const isExpanded = _finExpandedStudents.has(st.key || st.email);"
)
html = html.replace(
    "<button onclick=\"_finToggleStudentDetails('${st.email}')\"",
    "<button onclick=\"_finToggleStudentDetails('${st.key || st.email}')\""
)

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("template.html successfully updated!")

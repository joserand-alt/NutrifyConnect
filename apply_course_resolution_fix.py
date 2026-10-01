import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

RESOLVE_FUNCTION = '''
function _resolveFinCourse(f) {
    if (!f) return 'PLATAFORMA GERAL';
    if (f.curso && f.curso !== 'PLATAFORMA GERAL' && f.curso !== 'None') return f.curso;

    const email = (f.email || f._email || '').toString().toLowerCase().trim();
    const aluno = (f.aluno || f._aluno || '').toString().toLowerCase().trim();
    const plano = (f.plano || f._plano || f.description || '').toString();

    // 1. Tentar encontrar aluno no cadastro da plataforma (Academy / Cativa)
    const stList = (CURRENT_DATA && CURRENT_DATA.students) ? CURRENT_DATA.students : (DATA && DATA.students ? DATA.students : []);
    let stMatch = null;
    if (email) {
        stMatch = stList.find(s => s.email && s.email.toLowerCase().trim() === email);
    }
    if (!stMatch && aluno) {
        stMatch = stList.find(s => s.nome && s.nome.toLowerCase().trim() === aluno);
    }
    if (stMatch && stMatch.curso && stMatch.curso !== 'PLATAFORMA GERAL' && stMatch.curso !== 'None') {
        return stMatch.curso;
    }

    // 2. Inferir a partir do nome do plano ou descrição da cobrança na Vindi / Asaas
    const textFull = (plano + ' ' + (f.description || '')).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
    if (textFull.includes('ccih') || textFull.includes('prevencao') || textFull.includes('hospitalar')) {
        return 'POS-GRADUACAO EM PREVENCAO E CONTROLE DE INFECCAO HOSPITALAR (CCIH)';
    }
    if (textFull.includes('ortop') || textFull.includes('partes moles')) {
        return 'POS-GRADUACAO EM INFECCOES ORTOPEDICAS E DE PELE E PARTES MOLES';
    }
    if (textFull.includes('imuno') || textFull.includes('inuno')) {
        return 'POS-GRADUACAO EM INFECTOLOGIA DO PACIENTE IMUNODEPRIMIDO';
    }
    if (textFull.includes('pediatria') || textFull.includes('infectoped')) {
        return 'POS-GRADUACAO EM INFECTOPEDIATRIA';
    }
    if (textFull.includes('multi-r') || textFull.includes('multi r')) {
        return 'JORNADA MULTI-R';
    }
    if (textFull.includes('fungo') || textFull.includes('antifung')) {
        return 'DO FUNGO AO ANTIFUNGICO';
    }
    if (textFull.includes('s.o.s') || textFull.includes('antibiotico')) {
        return 'S.O.S ANTIBIOTICO';
    }
    if (textFull.includes('qualidade')) {
        return 'FERRAMENTAS DE QUALIDADE';
    }

    return 'PLATAFORMA GERAL';
}
'''

# 1. Insert _resolveFinCourse before function _getFinData
if 'function _resolveFinCourse(' not in html:
    target = 'function _getFinData('
    idx = html.find(target)
    assert idx != -1, "function _getFinData not found!"
    html = html[:idx] + RESOLVE_FUNCTION + '\n' + html[idx:]
    print("Inserted _resolveFinCourse helper function!")

# 2. Update mapping in _getFinData
old_vfaturas = "(vindi && vindi.faturas_tabela) ? vindi.faturas_tabela.map(f => ({ ...f, gateway: 'Vindi', _aluno: f.aluno, _email: f.email, _plano: f.plano })) : [];"
new_vfaturas = "(vindi && vindi.faturas_tabela) ? vindi.faturas_tabela.map(f => { const c = _resolveFinCourse(f); return { ...f, gateway: 'Vindi', curso: c, _curso: c, _aluno: f.aluno, _email: f.email, _plano: f.plano }; }) : [];"

old_afaturas = "(asaas && asaas.faturas_tabela) ? asaas.faturas_tabela.map(f => ({ ...f, gateway: 'Asaas', _aluno: f.aluno, _email: f.email, _plano: f.plano })) : [];"
new_afaturas = "(asaas && asaas.faturas_tabela) ? asaas.faturas_tabela.map(f => { const c = _resolveFinCourse(f); return { ...f, gateway: 'Asaas', curso: c, _curso: c, _aluno: f.aluno, _email: f.email, _plano: f.plano }; }) : [];"

if old_vfaturas in html:
    html = html.replace(old_vfaturas, new_vfaturas, 1)
    print("Updated vfaturas mapping!")
else:
    print("WARNING: old_vfaturas not found directly")

if old_afaturas in html:
    html = html.replace(old_afaturas, new_afaturas, 1)
    print("Updated afaturas mapping!")
else:
    print("WARNING: old_afaturas not found directly")

# 3. Update byStudent grouping in renderFinTable:
# const curso = f.curso || 'PLATAFORMA GERAL'; -> const curso = f.curso || _resolveFinCourse(f) || 'PLATAFORMA GERAL';
old_st_curso = "const curso = f.curso || 'PLATAFORMA GERAL';"
new_st_curso = "const curso = f.curso || _resolveFinCourse(f) || 'PLATAFORMA GERAL';"

if old_st_curso in html:
    html = html.replace(old_st_curso, new_st_curso)
    print("Updated byStudent curso fallback in renderFinTable!")

# 4. Save template.html
with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS: template.html updated with _resolveFinCourse!")

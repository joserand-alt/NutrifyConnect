import os

dash_dir = r'C:/Users/DELL/Desktop/Dash_InfectoCast'
template_path = os.path.join(dash_dir, 'template.html')

with open(template_path, 'r', encoding='utf-8') as f:
    t = f.read()

# 1. Update initFilters to include all courses from students + curriculum
old_init_filters = '''function initFilters() {
    const cursos = new Set();
    const alunos = new Set();
    const stList = (DATA && DATA.students) ? DATA.students : [];
    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};

    stList.forEach(s => {
        if(s.curso && s.curso !== 'Sem Curso' && curric) Object.keys(curric).forEach(c => cursos.add(c));
        if(s.nome || s.email) alunos.add((s.nome || 'Aluno') + " (" + (s.email || '') + ")");
    });

    const selCurso = $('#filter-curso');
    const sortedCourses = Object.keys(curric).sort((a, b) => {
        const aPos = a.startsWith('POS') || a.startsWith('P?S');
        const bPos = b.startsWith('POS') || b.startsWith('P?S');
        if (aPos && !bPos) return -1;
        if (!aPos && bPos) return 1;
        return a.localeCompare(b);
    });
    if (selCurso) selCurso.innerHTML = '<option value="all">Todos os Cursos</option>' + sortedCourses.map(c => `<option value="${c}">${c}</option>`).join('');

    const selAluno = $('#filter-aluno');
    if (selAluno) selAluno.innerHTML = '<option value="all">Todos os Alunos</option>' + Array.from(alunos).map(a => `<option value="${a}">${a}</option>`).join('');

    if (selCurso) selCurso.onchange = e => { FILTER.curso = e.target.value; applyFilters(); };
    if (selAluno) selAluno.onchange = e => { FILTER.aluno = e.target.value; applyFilters(); };
    if ($('#filter-date-start')) $('#filter-date-start').onchange = e => { FILTER.start = e.target.value; applyFilters(); };
    if ($('#filter-date-end')) $('#filter-date-end').onchange = e => { FILTER.end = e.target.value; applyFilters(); };
}'''

# Check if old_init_filters exists or search for it
idx_init = t.find('function initFilters() {')
idx_init_end = t.find('function parseDate(dStr)', idx_init)
print('Found initFilters block:', idx_init != -1 and idx_init_end != -1)

new_init_filters = '''function initFilters() {
    const cursos = new Set();
    const alunos = new Set();
    const stList = (DATA && DATA.students) ? DATA.students : [];
    const curric = (DATA && DATA.curriculum) ? DATA.curriculum : {};

    stList.forEach(s => {
        if(s.curso && s.curso !== 'Sem Curso') cursos.add(s.curso);
        if(s.nome || s.email) alunos.add((s.nome || 'Aluno') + " (" + (s.email || '') + ")");
    });
    if (curric) Object.keys(curric).forEach(c => { if(c && c !== 'Sem Curso') cursos.add(c); });

    const selCurso = $('#filter-curso');
    const sortedCourses = Array.from(cursos).sort((a, b) => {
        const aPos = a.startsWith('POS') || a.startsWith('PÓS') || a.startsWith('P?S');
        const bPos = b.startsWith('POS') || b.startsWith('PÓS') || b.startsWith('P?S');
        if (aPos && !bPos) return -1;
        if (!aPos && bPos) return 1;
        return a.localeCompare(b);
    });
    if (selCurso) selCurso.innerHTML = '<option value="all">Todos os Cursos</option>' + sortedCourses.map(c => `<option value="${c}">${c}</option>`).join('');

    const selAluno = $('#filter-aluno');
    if (selAluno) selAluno.innerHTML = '<option value="all">Todos os Alunos</option>' + Array.from(alunos).sort().map(a => `<option value="${a}">${a}</option>`).join('');

    if (selCurso) selCurso.onchange = e => { FILTER.curso = e.target.value; applyFilters(); };
    if (selAluno) selAluno.onchange = e => { FILTER.aluno = e.target.value; applyFilters(); };
    if ($('#filter-date-start')) $('#filter-date-start').onchange = e => { FILTER.start = e.target.value; applyFilters(); };
    if ($('#filter-date-end')) $('#filter-date-end').onchange = e => { FILTER.end = e.target.value; applyFilters(); };
}'''

t_updated = t[:idx_init] + new_init_filters + '\n\n' + t[idx_init_end:]

# 2. Add initialization trigger at the end of <script>
init_trigger = '''
// ==========================================
// INICIALIZAÇÃO AUTOMÁTICA DO DASHBOARD
// ==========================================
function initDashboard() {
    initFilters();
    applyFilters();
    selectTab('exec');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}
'''

idx_script_end = t_updated.rfind('</script>')
t_final = t_updated[:idx_script_end] + init_trigger + '\n' + t_updated[idx_script_end:]

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(t_final)

print('Successfully applied initFilters and initDashboard to template.html!')

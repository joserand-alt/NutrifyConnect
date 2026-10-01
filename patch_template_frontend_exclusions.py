import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# Locate drawExecView
idx1 = text.find('function drawExecView(')
assert idx1 != -1, "drawExecView not found"

idx_bs = text.find('const baseStudents = (CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0)', idx1)
assert idx_bs != -1, "baseStudents marker not found"

old_block = '''    // Usar CURRENT_DATA.students ou rawStudents enriquecido
    const baseStudents = (CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0)
        ? CURRENT_DATA.students
        : rawStudents.map(s => {'''

new_block = '''    // Regra de exclusão para contas internas, testes e curso Nutrify Connect
    const isInvalidOrInternal = s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const cr = (s.curso || '').toString().toUpperCase().trim();
        if (cr.includes('NUTRIFY')) return true;
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@vectorcomunica')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com')) return true;
        return false;
    };

    // Usar CURRENT_DATA.students ou rawStudents enriquecido (sempre excluindo testes e contas internas)
    const validRawStudents = rawStudents.filter(s => !isInvalidOrInternal(s));
    const baseStudents = (CURRENT_DATA && CURRENT_DATA.students && CURRENT_DATA.students.length > 0)
        ? CURRENT_DATA.students.filter(s => !isInvalidOrInternal(s))
        : validRawStudents.map(s => {'''

assert old_block in text, "old_block not found in template.html"
text = text.replace(old_block, new_block)

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("template.html updated with isInvalidOrInternal filter!")

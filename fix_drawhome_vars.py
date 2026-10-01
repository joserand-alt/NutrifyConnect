import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# Locate drawHome status distribution calculation
target = '''    const criticos = (stCounts['Abandonou'] || 0) + (stCounts['Nunca acessou'] || 0);
    const taxaCriticos = totalMatriculasAtivas > 0 ? ((criticos / totalMatriculasAtivas) * 100).toFixed(0) : '0';'''

replacement = '''    const criticos = (stCounts['Abandonou'] || 0) + (stCounts['Nunca acessou'] || 0);
    const taxaCriticos = totalMatriculasAtivas > 0 ? ((criticos / totalMatriculasAtivas) * 100).toFixed(0) : '0';

    const unicosAtivos = new Set(matriculasAtivas.filter(s => (s.status === 'Ativo' || (s.status||'').includes('Conclu'))).map(s => (s.email||'').toLowerCase().trim()).filter(Boolean)).size;
    const unicosRisco = new Set(matriculasAtivas.filter(s => ((s.status||'').includes('Risco') || (s.status||'').includes('Login'))).map(s => (s.email||'').toLowerCase().trim()).filter(Boolean)).size;
    const unicosAbandonaram = new Set(matriculasAtivas.filter(s => (s.status === 'Abandonou' || s.status === 'Inativo')).map(s => (s.email||'').toLowerCase().trim()).filter(Boolean)).size;
    const unicosNunca = new Set(matriculasAtivas.filter(s => (s.status === 'Nunca acessou' || !s.acessou)).map(s => (s.email||'').toLowerCase().trim()).filter(Boolean)).size;'''

assert target in text, "target not found in template.html"
text = text.replace(target, replacement)

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed drawHome unique student variables in template.html!")

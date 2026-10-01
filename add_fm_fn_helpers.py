import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''function drawExecView(force) {
    if (_execDrawn && !force) return;
    _execDrawn = true;

    const mount = $('#exec-content-mount');
    if (!mount) return;'''

replacement = '''function fM(val) {
    const n = Number(val) || 0;
    return 'R$ ' + n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fN(val) {
    const n = Number(val) || 0;
    return n.toLocaleString('pt-BR');
}

function drawExecView(force) {
    if (_execDrawn && !force) return;
    _execDrawn = true;

    const mount = $('#exec-content-mount');
    if (!mount) return;'''

assert target in text, "target not found in template.html"
text = text.replace(target, replacement)

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("Added fM and fN helper functions to template.html!")

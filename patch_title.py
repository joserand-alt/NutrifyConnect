template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update title in HTML
text = text.replace(
    '<h3 style="font-size:15px; font-weight:800; color:var(--ink); margin:0 0 4px">Todas as Faturas e Cobranças (Vindi)</h3>',
    '<h3 id="fin-table-title" style="font-size:15px; font-weight:800; color:var(--ink); margin:0 0 4px">Todas as Faturas e Cobranças (Consolidado)</h3>'
)

# 2. In _finSetSource, update title text dynamically
old_set_source = """function _finSetSource(src) {
    _finSource = src;
    ['all', 'asaas', 'vindi'].forEach(s => {
        const el = $(`#fin-src-${s}`);
        if (el) el.classList.toggle('on', s === src);
    });
    drawFinanceiro(true);
}"""

new_set_source = """function _finSetSource(src) {
    _finSource = src;
    ['all', 'asaas', 'vindi'].forEach(s => {
        const el = $(`#fin-src-${s}`);
        if (el) el.classList.toggle('on', s === src);
    });
    const titleEl = $('#fin-table-title');
    if (titleEl) {
        if (src === 'asaas') titleEl.textContent = 'Todas as Faturas e Cobranças (Asaas)';
        else if (src === 'vindi') titleEl.textContent = 'Todas as Faturas e Cobranças (Vindi)';
        else titleEl.textContent = 'Todas as Faturas e Cobranças (Consolidado)';
    }
    drawFinanceiro(true);
}"""

if old_set_source in text:
    text = text.replace(old_set_source, new_set_source)
    print("Updated _finSetSource with dynamic table title")

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved template.html")

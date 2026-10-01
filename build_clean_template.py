import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

# Read original_template.html
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove Tab button for apilogs:
text = re.sub(r'\s*<button class="tab" data-p="apilogs">.*?</button>', '', text, flags=re.DOTALL)

# 2. Remove Panel for apilogs:
text = re.sub(r'\s*<!--\s*PANEL:\s*ACADEMY\s*API\s*LOGS\s*-->\s*<section class="panel" id="p-apilogs">.*?</section>', '', text, flags=re.DOTALL)

# 3. Remove API logs JS cleanly using exact start and end strings:
start_str = '// --- API LOGS SYSTEM (INFECTOCAST ACADEMY) ---'
end_str = 'function openAllocModal(curso, aulaNome)'

pos_start = text.find(start_str)
pos_end = text.find(end_str)

print(f"Replacing from pos {pos_start} to {pos_end}")
if pos_start != -1 and pos_end != -1:
    text = text[:pos_start] + '\n\n' + text[pos_end:]

# 4. Add drawFinanceiro right before _renderFinKpiCards
if 'function drawFinanceiro' not in text:
    target = 'function _renderFinKpiCards() {'
    draw_fin_code = """function drawFinanceiro(force) {
    if (_finDrawn && !force) return;
    _finDrawn = true;

    const activeCurso = (FILTER && FILTER.curso && FILTER.curso !== 'all') ? FILTER.curso : null;
    const badgeFiltro = $('#fin-curso-filtro-badge');
    if (badgeFiltro) {
        if (activeCurso) {
            badgeFiltro.style.display = 'inline-block';
            badgeFiltro.textContent = `Curso ativo: ${activeCurso}`;
        } else {
            badgeFiltro.style.display = 'none';
        }
    }

    const fin = _getFinData(_finSource);
    if (!fin) {
        $('#fin-kpis-grid').innerHTML = '<div style="padding:24px; color:var(--muted); font-size:13px; text-align:center">Dados financeiros não disponíveis para o filtro selecionado.</div>';
        return;
    }
    _cachedFinObj = fin;

    _renderFinKpiCards();
    _drawFinChart(fin);
    _renderFinCursosTable(fin);

    _allFinFaturas = (fin.faturas_tabela || []);

    _updateFinChips();
    _updateFinViewButtons();
    renderFinTable();
}

"""
    text = text.replace(target, draw_fin_code + target)

# 5. Save as template.html
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'w', encoding='utf-8') as f:
    f.write(text)

# Extract JS and test with node
scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_clean.js', 'w', encoding='utf-8') as f:
        f.write(scripts[0])
    res = subprocess.run(['node', '-c', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_clean.js'], capture_output=True, text=True)
    print("Node syntax returncode:", res.returncode)
    if res.returncode != 0:
        print("Node error:", res.stderr)
    else:
        print("SUCCESS! template.html JS syntax is 100% CLEAN with 0 ERRORS!")

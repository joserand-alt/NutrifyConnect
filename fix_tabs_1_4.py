import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove obsolete p-apilogs panel if present
text = re.sub(r'\s*<!--\s*PANEL:\s*ACADEMY\s*API\s*LOGS\s*-->\s*<section class="panel" id="p-apilogs">.*?</section>', '', text, flags=re.DOTALL)
text = re.sub(r'\s*<section class="panel" id="p-apilogs">.*?</section>', '', text, flags=re.DOTALL)

# 2. Update selectTab to handle all tabs cleanly and robustly
old_select_tab = """function selectTab(pId) {
    if (!pId) return;
    $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.p === pId));
    $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));

    if (pId === 'exec') {
        drawExecView(true);
        if ($('#kpis')) $('#kpis').style.display = 'none';
    } else {
        if ($('#kpis')) $('#kpis').style.display = 'grid';
    }

    if (pId === 'home') drawHome(true);
    if (pId === 'prog') renderRows();
    if (pId === 'tl') drawTimeline(true);
    if (pId === 'mod') renderModules();
    if (pId === 'origem') drawOrigem(true);
    if (pId === 'fin') drawFinanceiro(true);
    if (pId === 'funil') {
        drawFunil(true);
        if ($('.filters')) $('.filters').style.display = 'none';
    } else {
        if ($('.filters')) $('.filters').style.display = 'flex';
    }
}"""

new_select_tab = """function selectTab(pId) {
    if (!pId) return;
    $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.p === pId));
    $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));

    // Exibe/oculta barra de KPIs do cabeçalho de acordo com a aba
    if (pId === 'exec' || pId === 'home' || pId === 'fin' || pId === 'funil') {
        if ($('#kpis')) $('#kpis').style.display = 'none';
    } else {
        if ($('#kpis')) $('#kpis').style.display = 'grid';
    }

    if (pId === 'exec') drawExecView(true);
    if (pId === 'home') drawHome(true);
    if (pId === 'prog') {
        buildHead();
        statusChips();
        renderRows();
    }
    if (pId === 'mod') renderModules();
    if (pId === 'ret') renderRetention();
    if (pId === 'tl') drawTimeline(true);
    if (pId === 'funil') {
        drawFunil(true);
        if ($('.filters')) $('.filters').style.display = 'none';
    } else {
        if ($('.filters')) $('.filters').style.display = 'flex';
    }
    if (pId === 'origem') drawOrigem(true);
    if (pId === 'fin') drawFinanceiro(true);
}"""

if old_select_tab in text:
    text = text.replace(old_select_tab, new_select_tab)
    print("Updated selectTab function!")
else:
    print("Could not find exact old selectTab function, checking...")

# 3. Enhance renderModules to allow course selection inside tab 2 and default to first course if 'all'
old_render_modules = """function renderModules() {
    const c = FILTER.curso;
    const view = $('#modcard');
    if (c === 'all') {
        view.innerHTML = '<div style="padding:20px; text-align:center; color:var(--muted)">Por favor, selecione um curso específico no filtro acima para ver os módulos.</div>';
        return;
    }
    
    let mods = DATA.curriculum[c];
    if (!mods) {
        view.innerHTML = '<div style="padding:20px; text-align:center; color:var(--muted)">Nenhum módulo encontrado para este curso.</div>';
        return;
    }"""

new_render_modules = """function setModCourse(cName) {
    FILTER.curso = cName;
    const sel = $('#filter-curso');
    if (sel) sel.value = cName;
    renderModules();
}

function renderModules() {
    let c = FILTER.curso;
    const view = $('#modcard');
    if (!view) return;

    const curric = DATA.curriculum || {};
    const availableCourses = Object.keys(curric).sort((a, b) => {
        const aPos = a.startsWith('POS') || a.startsWith('PÓS');
        const bPos = b.startsWith('POS') || b.startsWith('PÓS');
        if (aPos && !bPos) return -1;
        if (!aPos && bPos) return 1;
        return a.localeCompare(b);
    });

    if (c === 'all' && availableCourses.length > 0) {
        c = availableCourses[0];
    }
    
    let mods = curric[c];
    if (!mods || mods.length === 0) {
        view.innerHTML = '<div style="padding:20px; text-align:center; color:var(--muted)">Nenhum módulo encontrado para este curso.</div>';
        return;
    }

    const coursePills = `
      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:18px; padding-bottom:12px; border-bottom:1px solid var(--line)">
        ${availableCourses.map(cName => {
            const isSel = (c === cName);
            const bg = isSel ? 'var(--emerald)' : 'var(--card)';
            const col = isSel ? '#fff' : 'var(--ink)';
            const border = isSel ? '1px solid var(--emerald-d)' : '1px solid var(--line)';
            return `<button type="button" onclick="setModCourse('${cName}')" style="padding:6px 12px; font-size:11px; font-weight:700; border-radius:20px; background:${bg}; color:${col}; border:${border}; cursor:pointer; transition:all 0.15s ease">${cName}</button>`;
        }).join('')}
      </div>
    `;"""

# We need to replace in renderModules
pos_mod = text.find('function renderModules() {')
pos_view_inner = text.find('view.innerHTML = mods.map(m => {', pos_mod)

if pos_mod != -1 and pos_view_inner != -1:
    old_mod_part = text[pos_mod:pos_view_inner]
    replacement_mod_part = new_render_modules + '\n\n    view.innerHTML = coursePills + mods.map(m => {\n'
    text = text[:pos_mod] + replacement_mod_part + text[pos_view_inner + len('view.innerHTML = mods.map(m => {\n'):]
    print("Enhanced renderModules with interactive course selector!")

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'w', encoding='utf-8') as f:
    f.write(text)

# Extract JS and test syntax with node
scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_tabs_patch.js', 'w', encoding='utf-8') as f:
        f.write(scripts[0])
    res = subprocess.run(['node', '-c', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_tabs_patch.js'], capture_output=True, text=True)
    print("Node syntax returncode:", res.returncode)
    if res.returncode != 0:
        print("Node error:", res.stderr)
    else:
        print("SUCCESS! template.html syntax verified 100% CLEAN!")

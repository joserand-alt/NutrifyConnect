import os

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    t = f.read()

old_mod_code = '''    let mods = curric[c];
    if (!mods || mods.length === 0) {
        view.innerHTML = '<div style="padding:20px; text-align:center; color:var(--muted)">Nenhum m\xf3dulo encontrado para este curso.</div>';
        return;
    }'''

if old_mod_code not in t:
    # let's search
    idx = t.find('let mods = curric[c];')
    print('Found mods at:', idx)
    print(t[idx:idx+300])

new_mod_code = '''    let mods = curric[c];
    if (!mods || mods.length === 0) {
        view.innerHTML = '<div style="padding:20px; text-align:center; color:var(--muted)">Nenhum módulo encontrado para este curso.</div>';
        return;
    }

    let maxIni = 1;
    mods.forEach(m => {
        (m.aulas || []).forEach(a => {
            const aNorm = a.nome ? a.nome.toString().trim().toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') : '';
            const views = (CURRENT_DATA?.lesson_views?.[a.id]?.size) || (CURRENT_DATA?.lesson_views?.[aNorm]?.size) || 0;
            if (views > maxIni) maxIni = views;
        });
    });
    if (maxIni <= 0) maxIni = 1;'''

idx = t.find('let mods = curric[c];')
idx_end = t.find('const coursePills = `', idx)

t_updated = t[:idx] + new_mod_code + '\n\n    ' + t[idx_end:]

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(t_updated)

print('Successfully patched renderModules in template.html!')

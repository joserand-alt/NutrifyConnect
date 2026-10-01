import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_tabs_deep.js', 'w', encoding='utf-8') as f:
        mock_env = """
        const elementsMap = {};
        const mockEl = (id) => {
            if (!elementsMap[id]) {
                elementsMap[id] = {
                    id: id || '',
                    dataset: { p: id || '', g: 'day', m: 'stack' },
                    style: {},
                    textContent: '',
                    innerHTML: '',
                    value: '',
                    clientWidth: 1000,
                    classList: {
                        _classes: new Set(),
                        add(c){ this._classes.add(c); },
                        remove(c){ this._classes.delete(c); },
                        toggle(c, force){ if(force) this._classes.add(c); else this._classes.delete(c); return force; }
                    },
                    setAttribute(){},
                    appendChild(){},
                    addEventListener(){},
                    scrollIntoView(){}
                };
            }
            return elementsMap[id];
        };
        global.document = {
            getElementById: (id) => mockEl(id),
            querySelector: (sel) => mockEl(sel.replace(/^[#.]/, '')),
            querySelectorAll: (sel) => [mockEl(sel.replace(/^[#.]/, ''))],
            createElement: (tag) => mockEl(tag),
            body: { appendChild(){}, removeChild(){} }
        };
        global.window = {
            location: { href: '', pathname: '', search: '' },
            addEventListener: () => {}
        };
        """
        f.write(mock_env + '\n' + scripts[0] + '\n' + """
        console.log('--- RUNNING INITIALIZATION ---');
        initFilters();
        applyFilters();

        console.log('\\n--- 1. TESTING TAB 1: PROG (Progresso por aluno) ---');
        buildHead();
        statusChips();
        renderRows();
        console.log('Tab 1 (tbody HTML length):', mockEl('tbody').innerHTML.length);
        console.log('Tab 1 (kpis HTML length):', mockEl('kpis').innerHTML.length);

        console.log('\\n--- 2. TESTING TAB 2: MOD (Engajamento por módulo) ---');
        renderModules();
        console.log('Tab 2 (modcard HTML snippet):', mockEl('modcard').innerHTML.substring(0, 200));

        console.log('\\n--- 3. TESTING TAB 3: RET (Retenção & abandono) ---');
        renderRetention();
        console.log('Tab 3 (o-never text):', mockEl('o-never').textContent);
        console.log('Tab 3 (o-aband text):', mockEl('o-aband').textContent);
        console.log('Tab 3 (o-risco text):', mockEl('o-risco').textContent);
        console.log('Tab 3 (o-ativo text):', mockEl('o-ativo').textContent);
        console.log('Tab 3 (ret-insight HTML):', mockEl('ret-insight').innerHTML);

        console.log('\\n--- 4. TESTING TAB 4: TL (Linha temporal) ---');
        drawTimeline(true);
        console.log('Tab 4 (timeline SVG length):', mockEl('timeline').innerHTML.length);
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_tabs_deep.js'], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Stderr:\n", res.stderr)

import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_tabs2.js', 'w', encoding='utf-8') as f:
        mock_env = """
        const mockEl = (id) => ({
            id: id || '',
            dataset: { p: id || '' },
            style: {},
            textContent: '',
            innerHTML: '',
            value: '',
            classList: { add(){}, remove(){}, toggle(){ return true; } },
            setAttribute(){},
            appendChild(){},
            addEventListener(){},
            scrollIntoView(){}
        });
        global.document = {
            getElementById: (id) => mockEl(id),
            querySelector: (sel) => mockEl(sel),
            querySelectorAll: (sel) => [mockEl(sel)],
            createElement: (tag) => mockEl(tag),
            body: { appendChild(){}, removeChild(){} }
        };
        global.window = {
            location: { href: '', pathname: '', search: '' },
            addEventListener: () => {}
        };
        """
        f.write(mock_env + '\n' + scripts[0] + '\n' + """
        console.log('Testing each tab and its render functions:');
        
        console.log('\\n1. Testing initFilters & applyFilters...');
        try {
            initFilters();
            applyFilters();
            console.log('applyFilters OK! CURRENT_DATA.students count:', CURRENT_DATA?.students?.length);
        } catch(e) { console.error('applyFilters ERROR:', e); }

        console.log('\\n2. Testing drawHome (Tab 1)...');
        try {
            drawHome(true);
            console.log('drawHome OK!');
        } catch(e) { console.error('drawHome ERROR:', e); }

        console.log('\\n3. Testing renderModules (Tab 2)...');
        try {
            renderModules();
            console.log('renderModules OK!');
        } catch(e) { console.error('renderModules ERROR:', e); }

        console.log('\\n4. Testing renderRetention (Tab 3)...');
        try {
            renderRetention();
            console.log('renderRetention OK!');
        } catch(e) { console.error('renderRetention ERROR:', e); }

        console.log('\\n5. Testing drawOrigem (Tab 4)...');
        try {
            drawOrigem(true);
            console.log('drawOrigem OK!');
        } catch(e) { console.error('drawOrigem ERROR:', e); }
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_tabs2.js'], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Stderr:\n", res.stderr)

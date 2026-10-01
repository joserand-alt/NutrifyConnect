import sys, re, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_inspect_asaas.js', 'w', encoding='utf-8') as f:
        mock_env = """
        const mockEl = (id) => ({
            id: id || '',
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
        console.log('--- ASAAS KPIS ---');
        console.log(JSON.stringify(DATA.financeiro_asaas.kpis, null, 2));

        console.log('\\n--- ASAAS DATA SAMPLES (first 5) ---');
        const aData = DATA.financeiro_asaas.data || {};
        const entries = Object.entries(aData).slice(0, 5);
        entries.forEach(([k, v]) => {
            console.log(k, '=>', JSON.stringify(v));
        });

        console.log('\\n--- VINDI KPIS ---');
        console.log(JSON.stringify(DATA.financeiro.kpis, null, 2));

        console.log('\\n--- VINDI SUBSCRIPTIONS SAMPLE (first 3) ---');
        const vSubs = DATA.financeiro.subscriptions || [];
        vSubs.slice(0, 3).forEach(s => {
            console.log('VSub:', s.id, s.status, s.status_financeiro, s.valor_parcela, s.plano);
        });
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_inspect_asaas.js'], capture_output=True, text=True)
    print("Node output:\n", res.stdout)
    if res.stderr:
        print("Node stderr:\n", res.stderr)

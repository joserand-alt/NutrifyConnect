import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_unified_mrr.js', 'w', encoding='utf-8') as f:
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
        // Let's test updated computeUnifiedFinancialDataset logic
        const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
        const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
        const vSubs = (vindi && vindi.subscriptions) ? vindi.subscriptions : [];
        const aFaturas = (asaas && asaas.faturas_tabela) ? asaas.faturas_tabela : [];

        console.log('Vindi MRR KPI:', vindi.kpis?.mrr_ativo);
        console.log('Asaas MRR KPI:', asaas.kpis?.mrr_ativo);
        console.log('Consolidated expected MRR:', Number(vindi.kpis?.mrr_ativo || 0) + Number(asaas.kpis?.mrr_ativo || 0));
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_unified_mrr.js'], capture_output=True, text=True)
    print("Node output:\n", res.stdout)

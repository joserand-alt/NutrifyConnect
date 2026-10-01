import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_verify_all.js', 'w', encoding='utf-8') as f:
        # Load mock environment and the template script with mock DATA
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
        console.log('--- TEST DATA FINANCIAL VERIFICATION ---');
        const finAll = computeUnifiedFinancialDataset('all');
        const finVindi = computeUnifiedFinancialDataset('vindi');
        const finAsaas = computeUnifiedFinancialDataset('asaas');

        console.log('Global Consolidado MRR:', finAll.global.kpis.mrr_ativo);
        console.log('Global Vindi MRR:', finVindi.global.kpis.mrr_ativo);
        console.log('Global Asaas MRR:', finAsaas.global.kpis.mrr_ativo);

        let sumCoursesMrr = 0;
        Object.values(finAll.courses).forEach(cm => {
            console.log(`  Course MRR [${cm.curso}]: R$ ${cm.mrr.toFixed(2)}`);
            sumCoursesMrr += cm.mrr;
        });
        console.log('Sum of all course MRRs:', sumCoursesMrr.toFixed(2));
        console.log('Global MRR matches sum of courses:', Math.abs(finAll.global.kpis.mrr_ativo - sumCoursesMrr) < 0.01);

        console.log('\\n--- TEST DRAW FUNCTIONS ---');
        drawExecView(true);
        console.log('drawExecView executed successfully!');
        drawFinanceiro(true);
        console.log('drawFinanceiro executed successfully!');
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_verify_all.js'], capture_output=True, text=True)
    print("Node output:\n", res.stdout)
    if res.stderr:
        print("Node stderr:\n", res.stderr)

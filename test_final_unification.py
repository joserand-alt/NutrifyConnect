import sys, re, subprocess, shutil
sys.stdout.reconfigure(encoding='utf-8')

shutil.copy(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html')
print("Copied dashboard_gerado.html to index.html.")

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_final.js', 'w', encoding='utf-8') as f:
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
        console.log('====================================================');
        console.log('1. ABA FINANCEIRO — COMPUTE UNIFIED FINANCIAL DATASET');
        console.log('====================================================');
        const finAll = computeUnifiedFinancialDataset('all');
        const finVindi = computeUnifiedFinancialDataset('vindi');
        const finAsaas = computeUnifiedFinancialDataset('asaas');

        console.log('MRR Consolidado Global:', finAll.global.kpis.mrr_ativo);
        console.log('MRR Vindi Global:      ', finVindi.global.kpis.mrr_ativo);
        console.log('MRR Asaas Global:      ', finAsaas.global.kpis.mrr_ativo);

        console.log('\\nMRR Por Curso (Aba Financeiro / Consolidado):');
        let sumCourseMrr = 0;
        Object.values(finAll.courses).forEach(c => {
            console.log(`  - ${c.curso}: R$ ${c.mrr.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})}`);
            sumCourseMrr += c.mrr;
        });
        console.log(`  Total Soma Cursos: R$ ${sumCourseMrr.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})}`);

        console.log('\\n====================================================');
        console.log('2. VISÃO EXECUTIVA — DRAW EXEC VIEW');
        console.log('====================================================');
        drawExecView(true);
        console.log('drawExecView executed successfully with 0 errors!');

        console.log('\\n====================================================');
        console.log('3. ABA FINANCEIRO — DRAW FINANCEIRO');
        console.log('====================================================');
        drawFinanceiro(true);
        console.log('drawFinanceiro executed successfully with 0 errors!');
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_final.js'], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Stderr:\n", res.stderr)

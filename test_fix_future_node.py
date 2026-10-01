import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_fix_future.js', 'w', encoding='utf-8') as f:
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
        # Patch the function in memory to include 'futuro'
        patched_script = scripts[0].replace(
            "if (st === 'pendente' || st === 'pending' || st === 'a_vencer')",
            "if (st === 'pendente' || st === 'pending' || st === 'a_vencer' || st === 'futuro')"
        )
        f.write(mock_env + '\n' + patched_script + '\n' + """
        console.log('=== VERIFYING SOS ANTIBIOTICO WITH FUTURO INCLUDED ===');
        const finAll = computeUnifiedFinancialDataset('all');
        const sosFin = finAll.courses['S.O.S ANTIBIOTICO'];

        console.log('SOS Antibiótico KPIs:');
        console.log('  Total Recebido:      R$', sosFin.kpis.total_recebido);
        console.log('  Recebido Mês Atual:  R$', sosFin.kpis.recebido_mes_atual);
        console.log('  A Vencer Mês Atual:  R$', sosFin.kpis.a_vencer_mes_atual);
        console.log('  Previsto Mês:        R$', sosFin.kpis.previsto_mes_vigente);
        console.log('  MRR Ativo:           R$', sosFin.kpis.mrr_ativo);
        console.log('  Projeção 30d:        R$', sosFin.kpis.projecao_30d);
        console.log('  Projeção 3M:         R$', sosFin.kpis.proj_3m);
        console.log('  Projeção 6M:         R$', sosFin.kpis.proj_6m);
        console.log('  Projeção 12M:        R$', sosFin.kpis.proj_12m);

        console.log('\\nSOS Antibiótico Projeção Mensal (Próximos 6 meses):');
        sosFin.projecao_mensal.slice(0, 6).forEach(m => {
            console.log(`  ${m.label} (${m.mes}): Previsto R$ ${m.previsto.toFixed(2)}`);
        });

        console.log('\\n=== GLOBAL CONSOLIDATED PROJECTIONS ===');
        console.log('Global Proj 3M:  R$', finAll.global.kpis.proj_3m);
        console.log('Global Proj 6M:  R$', finAll.global.kpis.proj_6m);
        console.log('Global Proj 12M: R$', finAll.global.kpis.proj_12m);
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_fix_future.js'], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Stderr:\n", res.stderr)

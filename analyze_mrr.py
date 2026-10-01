import sys, re, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_mrr.js', 'w', encoding='utf-8') as f:
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
        console.log('--- 1. ABA FINANCEIRO (computeUnifiedFinancialDataset) ---');
        const finAll = computeUnifiedFinancialDataset('all');
        console.log('Financeiro Global MRR:', finAll.global.kpis.mrr_ativo);
        console.log('Financeiro Vindi MRR:', computeUnifiedFinancialDataset('vindi').global.kpis.mrr_ativo);
        console.log('Financeiro Asaas MRR:', computeUnifiedFinancialDataset('asaas').global.kpis.mrr_ativo);

        console.log('\\n--- 2. VISAO EXECUTIVA (drawExecView direct calculations) ---');
        const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
        const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
        const vKpis = vindi.kpis || {};
        const aKpis = asaas.kpis || {};
        console.log('vKpis.mrr_ativo:', vKpis.mrr_ativo);
        console.log('aKpis.mrr_ativo:', aKpis.mrr_ativo);
        console.log('Exec consolidado (vKpis.mrr_ativo + aKpis.mrr_ativo):', (Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0));

        // Let's inspect subscription details in Vindi and Asaas
        console.log('\\n--- 3. DETALHES DE ASSINATURAS VINDI ---');
        const vSubs = vindi.subscriptions || [];
        console.log('Total Vindi subscriptions:', vSubs.length);
        let vActiveCount = 0, vActiveSum = 0;
        let vAdimplenteSum = 0, vActiveAllSum = 0;
        vSubs.forEach(s => {
            const st = (s.status || '').toLowerCase();
            const stFin = (s.status_financeiro || '').toLowerCase();
            const val = Number(s.valor_parcela || s.price || s.valor) || 0;
            if (st === 'active') {
                vActiveAllSum += val;
                if (stFin === 'adimplente') {
                    vAdimplenteSum += val;
                }
            }
        });
        console.log('Vindi active (todas):', vActiveAllSum);
        console.log('Vindi active (apenas adimplente):', vAdimplenteSum);

        console.log('\\n--- 4. DETALHES DE ASSINATURAS/CUSTOMERS ASAAS ---');
        const aData = asaas.data || {};
        console.log('Total Asaas customers:', Object.keys(aData).length);
        let aActiveSum = 0, aAdimplenteSum = 0;
        Object.values(aData).forEach(s => {
            const val = Number(s.valor_parcela || s.mrr) || 0;
            const stFin = (s.status_financeiro || '').toLowerCase();
            aActiveSum += val;
            if (stFin === 'adimplente') {
                aAdimplenteSum += val;
            }
        });
        console.log('Asaas total parcela sum:', aActiveSum);
        console.log('Asaas apenas adimplente sum:', aAdimplenteSum);
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_mrr.js'], capture_output=True, text=True)
    print("Node output:\n", res.stdout)
    if res.stderr:
        print("Node stderr:\n", res.stderr)

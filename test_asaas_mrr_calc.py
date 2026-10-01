import sys, re, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_asaas_mrr.js', 'w', encoding='utf-8') as f:
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
        const asaas = DATA.financeiro_asaas || {};
        const aKpis = asaas.kpis || {};
        console.log('Asaas kpis.mrr_ativo:', aKpis.mrr_ativo);
        console.log('Asaas kpis.a_vencer_mes_atual:', aKpis.a_vencer_mes_atual);
        console.log('Asaas kpis.projecao_30d:', aKpis.projecao_30d);

        const aData = asaas.data || {};
        const aFaturas = asaas.faturas_tabela || [];

        // Check faturas pending
        let pendingSum = 0;
        let pendingNextMonthSum = 0;
        const studentPendingMap = {};

        aFaturas.forEach(f => {
            const st = (f.status || '').toLowerCase();
            if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
                const val = Number(f.valor) || 0;
                pendingSum += val;
                const em = (f.email || '').toLowerCase().trim();
                studentPendingMap[em] = (studentPendingMap[em] || 0) + val;
            }
        });

        console.log('Total Asaas pending faturas sum:', pendingSum);
        console.log('Distinct students with pending faturas in Asaas:', Object.keys(studentPendingMap).length);

        // Let's test MRR calculation from asaas customer subscriptions/pending installments
        let calculatedAsaasMrr = 0;
        Object.values(aData).forEach(stInfo => {
            if (stInfo.status_financeiro === 'adimplente') {
                const fts = stInfo.faturas || [];
                const pending = fts.filter(f => {
                    const st = (f.status || f.status_raw || '').toLowerCase();
                    return st === 'pendente' || st === 'pending' || st === 'a_vencer';
                });
                if (pending.length > 0) {
                    // One installment per active adimplente student
                    const firstPendingVal = Number(pending[0].valor) || 0;
                    calculatedAsaasMrr += firstPendingVal;
                }
            }
        });
        console.log('Calculated Asaas MRR from first pending installment of adimplente students:', calculatedAsaasMrr);
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_asaas_mrr.js'], capture_output=True, text=True)
    print("Node output:\n", res.stdout)
    if res.stderr:
        print("Node stderr:\n", res.stderr)

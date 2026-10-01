import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_inspect_sos.js', 'w', encoding='utf-8') as f:
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
        console.log('=== SOS ANTIBIÓTICO DEEP INSPECTION ===');
        const stList = DATA.students || [];
        console.log('Total students:', stList.length);

        const sosStudents = stList.filter(s => {
            const c = (s.curso || '').toUpperCase();
            return c.includes('ANTIBIOT') || c.includes('SOS') || c.includes('S.O.S');
        });

        console.log('Students with course matching SOS/ANTIBIOTICO:', sosStudents.length);
        sosStudents.forEach(s => {
            console.log(`\\nStudent: ${s.nome} | Email: ${s.email} | Curso: ${s.curso} | Status: ${s.status}`);
            if (s.vindi) {
                console.log('  Vindi:', JSON.stringify({
                    status_financeiro: s.vindi.status_financeiro,
                    plano: s.vindi.plano,
                    valor_parcela: s.vindi.valor_parcela,
                    faturas_count: s.vindi.faturas?.length,
                    faturas: s.vindi.faturas
                }));
            }
            if (s.asaas) {
                console.log('  Asaas:', JSON.stringify({
                    status_financeiro: s.asaas.status_financeiro,
                    total_pago: s.asaas.total_pago,
                    faturas_count: s.asaas.faturas?.length,
                    faturas: s.asaas.faturas
                }));
            }
        });

        console.log('\\n=== CHECK ALL FATURAS IN BOTH GATEWAYS FOR SOS / ANTIBIOTICO ===');
        const vFaturas = DATA.financeiro?.faturas_tabela || [];
        const aFaturas = DATA.financeiro_asaas?.faturas_tabela || [];

        console.log('Total Vindi faturas:', vFaturas.length);
        console.log('Total Asaas faturas:', aFaturas.length);

        const vSos = vFaturas.filter(f => (f.plano||f.description||f.curso||'').toLowerCase().includes('antibiot') || (f.plano||f.description||f.curso||'').toLowerCase().includes('sos'));
        console.log('Vindi faturas matching SOS/Antibiotico:', vSos.length);
        vSos.forEach(f => {
            console.log('  Vindi Fat:', f.id, f.status, 'R$' + f.valor, f.vencimento, f.data_pagamento, f.aluno, f.email, f.plano);
        });

        // Let's check Asaas faturas for students of SOS
        const sosEmails = new Set(sosStudents.map(s => (s.email||'').toLowerCase().trim()));
        const aSosByEmail = aFaturas.filter(f => sosEmails.has((f.email||'').toLowerCase().trim()));
        console.log('Asaas faturas for students enrolled in SOS:', aSosByEmail.length);
        aSosByEmail.forEach(f => {
            console.log('  Asaas Fat (by student email):', f.id, f.status, f.status_raw, 'R$' + f.valor, f.vencimento, f.data_pagamento, f.aluno, f.email, f.description);
        });

        console.log('\\n=== UNIFIED FINANCIAL DATASET FOR SOS ANTIBIOTICO ===');
        const finAll = computeUnifiedFinancialDataset('all');
        const sosFin = finAll.courses['S.O.S ANTIBIOTICO'];
        console.log('S.O.S ANTIBIOTICO metrics in finAll:', JSON.stringify(sosFin, null, 2));
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_inspect_sos.js'], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Stderr:\n", res.stderr)

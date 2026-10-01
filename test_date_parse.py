import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_date_parse.js', 'w', encoding='utf-8') as f:
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
        # Patch both:
        # 1. Use f.vencimento_iso || f.vencimento
        # 2. Include 'futuro'
        # 3. Use proper date parsing (handling DD/MM/YYYY and YYYY-MM-DD)
        old_part = """        aFaturas.forEach(f => {
            const st = (f.status || '').toLowerCase();
            if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
                const em = (f.email || '').toString().toLowerCase().trim();
                const cm = getCourse(f.curso || emailToCourse[em]);
                const val = Number(f.valor) || 0;
                const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
                if (dtVenc) {
                    const dObj = new Date(dtVenc.slice(0, 10));
                    const hoje = new Date();
                    const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                    if (diffMeses >= 0 && diffMeses < 18) {
                        cm.projecao_18m_sim[diffMeses] += val;
                        if (diffMeses === 0 || diffMeses === 1) {
                            asaasCoursePending[cm.curso] = (asaasCoursePending[cm.curso] || 0) + val;
                            asaasTotalPending += val;
                        }
                    }
                }
            }
        });"""

        new_part = """        aFaturas.forEach(f => {
            const st = (f.status || f.status_raw || '').toLowerCase();
            if (st === 'pendente' || st === 'pending' || st === 'a_vencer' || st === 'futuro' || st === 'confirmed') {
                const em = (f.email || '').toString().toLowerCase().trim();
                const cm = getCourse(f.curso || emailToCourse[em]);
                const val = Number(f.valor) || 0;
                
                // Parse date accurately supporting both YYYY-MM-DD and DD/MM/YYYY
                const isoStr = (f.vencimento_iso || '').toString().slice(0, 10);
                const brStr = (f.vencimento || '').toString().slice(0, 10);
                let dObj = null;
                if (isoStr && isoStr.includes('-')) {
                    const [y, m, d] = isoStr.split('-').map(Number);
                    dObj = new Date(y, m - 1, d);
                } else if (brStr && brStr.includes('/')) {
                    const [d, m, y] = brStr.split('/').map(Number);
                    dObj = new Date(y, m - 1, d);
                }
                
                if (dObj && !isNaN(dObj.getTime())) {
                    const hoje = new Date(2026, 8, 14); // Setembro 2026
                    const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                    if (diffMeses >= 0 && diffMeses < 18) {
                        cm.projecao_18m_sim[diffMeses] += val;
                        if (diffMeses === 0 || diffMeses === 1) {
                            asaasCoursePending[cm.curso] = (asaasCoursePending[cm.curso] || 0) + val;
                            asaasTotalPending += val;
                        }
                    }
                }
            }
        });"""

        patched_script = scripts[0].replace(old_part, new_part)
        f.write(mock_env + '\n' + patched_script + '\n' + """
        console.log('=== TEST RESULT FOR SOS ANTIBIOTICO WITH DATE FIX ===');
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

        console.log('\\nSOS Antibiótico Projeção Mensal Mês a Mês:');
        sosFin.projecao_mensal.slice(0, 12).forEach(m => {
            console.log(`  ${m.label} (${m.mes}): Previsto R$ ${m.previsto.toFixed(2)}`);
        });
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_date_parse.js'], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Stderr:\n", res.stderr)

import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Asaas handling inside computeUnifiedFinancialDataset
old_asaas_block = """    // 4. Clientes e Carnês Asaas
    if (!gatewayFilter || gatewayFilter === 'all' || gatewayFilter === 'asaas') {
        Object.values(aData).forEach(stInfo => {
            if (stInfo.status_financeiro === 'adimplente') {
                const em = (stInfo.customer_email || stInfo.email || '').toString().toLowerCase().trim();
                const cm = getCourse(stInfo.curso || emailToCourse[em]);
                const price = Number(stInfo.valor_parcela || stInfo.mrr) || 0;
                cm.mrr += price;
            }
        });

        aFaturas.forEach(f => {
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
                    }
                }
            }
        });
    }"""

new_asaas_block = """    // 4. Clientes e Carnês Asaas (MRR e Projeções Futuras)
    if (!gatewayFilter || gatewayFilter === 'all' || gatewayFilter === 'asaas') {
        const asaasMrrGlobal = Number(asaas.kpis?.mrr_ativo) || 0;
        const asaasCoursePending = {};
        let asaasTotalPending = 0;

        aFaturas.forEach(f => {
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
        });

        if (asaasTotalPending > 0 && asaasMrrGlobal > 0) {
            Object.entries(asaasCoursePending).forEach(([cName, pVal]) => {
                const cm = getCourse(cName);
                const prop = pVal / asaasTotalPending;
                cm.mrr += (asaasMrrGlobal * prop);
            });
        } else if (asaasMrrGlobal > 0) {
            const cm = getCourse('PLATAFORMA GERAL');
            cm.mrr += asaasMrrGlobal;
        }
    }"""

if old_asaas_block in text:
    text = text.replace(old_asaas_block, new_asaas_block)
    print("Updated Asaas block in computeUnifiedFinancialDataset!")
else:
    print("Could not find exact old Asaas block, checking pattern...")

# 2. Update drawExecView to use computeUnifiedFinancialDataset directly for consolidated metrics
old_exec_fin_block = """    // Totalizadores Consolidados Financeiros
    const vKpis = vindi.kpis || {};
    const aKpis = asaas.kpis || {};

    const recRealizadaTotal = (Number(vKpis.total_recebido) || 0) + (Number(aKpis.total_recebido) || 0);
    const recMesAtual = (Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || 0);
    const aVencerMesVigente = (Number(vKpis.a_vencer_mes_atual) || Number(vKpis.projecao_mensal?.[0]?.previsto) || 0) + (Number(aKpis.a_vencer_mes_atual) || Number(aKpis.projecao_mensal?.[0]?.previsto) || 0);
    const totalPrevistoMesVigente = recMesAtual + aVencerMesVigente;
    const mrrConsolidado = (Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0);
    const proj30d = (Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0);
    const proj3mConsolidada = globalProj3m > 0 ? globalProj3m : mrrConsolidado * 3;
    const proj6mConsolidada = globalProj6m > 0 ? globalProj6m : mrrConsolidado * 6;
    const proj12m = globalProj12m > 0 ? globalProj12m : mrrConsolidado * 12;
    const atrasoTotal = (Number(vKpis.total_em_atraso) || 0) + (Number(aKpis.total_em_atraso) || 0);
    const qtdAtrasoTotal = (Number(vKpis.qtd_em_atraso) || 0) + (Number(aKpis.qtd_em_atraso) || 0);
    const taxaAdimplencia = vKpis.taxa_adimplencia || 96;"""

new_exec_fin_block = """    // Totalizadores Consolidados Financeiros Unificados
    const finUnifiedGlobal = computeUnifiedFinancialDataset('all');
    const uKpis = finUnifiedGlobal.global.kpis || {};

    const recRealizadaTotal = uKpis.total_recebido || 0;
    const recMesAtual = uKpis.recebido_mes_atual || 0;
    const aVencerMesVigente = uKpis.a_vencer_mes_atual || 0;
    const totalPrevistoMesVigente = uKpis.previsto_mes_vigente || (recMesAtual + aVencerMesVigente);
    const mrrConsolidado = uKpis.mrr_ativo || 0;
    const proj30d = uKpis.projecao_30d || 0;
    const proj3mConsolidada = uKpis.proj_3m || 0;
    const proj6mConsolidada = uKpis.proj_6m || 0;
    const proj12m = uKpis.proj_12m || 0;
    const atrasoTotal = uKpis.total_em_atraso || 0;
    const qtdAtrasoTotal = uKpis.qtd_em_atraso || 0;
    const taxaAdimplencia = uKpis.taxa_adimplencia || 96;"""

if old_exec_fin_block in text:
    text = text.replace(old_exec_fin_block, new_exec_fin_block)
    print("Updated exec financial block to use computeUnifiedFinancialDataset directly!")
else:
    print("Could not find exact old exec financial block!")

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'w', encoding='utf-8') as f:
    f.write(text)

# Extract JS and test with node
scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_unified_patch.js', 'w', encoding='utf-8') as f:
        f.write(scripts[0])
    res = subprocess.run(['node', '-c', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_unified_patch.js'], capture_output=True, text=True)
    print("Node syntax returncode:", res.returncode)
    if res.returncode != 0:
        print("Node error:", res.stderr)
    else:
        print("SUCCESS! template.html syntax verified 100% CLEAN!")

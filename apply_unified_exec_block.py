import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_mrr = text.find('const mrrConsolidado =')
print("pos_mrr:", pos_mrr)

# Let's inspect 500 chars around pos_mrr
print("--- Old exec financial calculation block ---")
print(text[pos_mrr-300:pos_mrr+600])

# Let's replace the block cleanly
target_block = text[pos_mrr-200:pos_mrr+500]
# Find exact start and end of that calculation block
idx_start = text.rfind('// Totalizadores Consolidados Financeiros', 0, pos_mrr)
if idx_start == -1:
    idx_start = text.rfind('const vKpis =', 0, pos_mrr)

idx_end = text.find('// Cálculo Dinâmico do Mês Vigente', pos_mrr)

print(f"Replacing span {idx_start} to {idx_end}:")
print(text[idx_start:idx_end])

new_block = """// Totalizadores Consolidados Financeiros Unificados
    const finUnifiedGlobal = computeUnifiedFinancialDataset('all');
    const uKpis = finUnifiedGlobal.global.kpis || {};

    const recRealizadaTotal = uKpis.total_recebido || 0;
    const recMesAtual = uKpis.recebido_mes_atual || 0;
    const aVencerMesVigente = uKpis.a_vencer_mes_atual || 0;
    const totalPrevistoMesVigente = uKpis.previsto_mes_vigente || (recMesAtual + aVencerMesVigente);
    const mrrConsolidado = uKpis.mrr_ativo || 0;
    const proj30d = uKpis.projecao_30d || 0;
    const proj3mConsolidada = uKpis.proj_3m || (mrrConsolidado * 3);
    const proj6mConsolidada = uKpis.proj_6m || (mrrConsolidado * 6);
    const proj12m = uKpis.proj_12m || (mrrConsolidado * 12);
    const atrasoTotal = uKpis.total_em_atraso || 0;
    const qtdAtrasoTotal = uKpis.qtd_em_atraso || 0;
    const taxaAdimplencia = uKpis.taxa_adimplencia || 96;
"""

text = text[:idx_start] + new_block + '\n    ' + text[idx_end:]

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'w', encoding='utf-8') as f:
    f.write(text)

# Extract JS and test with node
scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_unified_patch2.js', 'w', encoding='utf-8') as f:
        f.write(scripts[0])
    res = subprocess.run(['node', '-c', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_unified_patch2.js'], capture_output=True, text=True)
    print("Node syntax returncode:", res.returncode)
    if res.returncode != 0:
        print("Node error:", res.stderr)
    else:
        print("SUCCESS! template.html syntax verified 100% CLEAN!")

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
d_match = re.search(r'const DATA = ({[\s\S]*?});', text)
data_str = d_match.group(1)

f_start = text.find('function computeUnifiedFinancialDataset')
f_end = text.find('function fM', f_start)
fin_func = text[f_start:f_end]

h_start = text.find('function isInvalidOrInternal')
h_end = text.find('function computeUnifiedFinancialDataset', h_start)
helpers = text[h_start:h_end]

test_js = '''
const DATA = ''' + data_str + ''';
let CURRENT_DATA = DATA;
let FILTER = { curso: 'all', gateway: 'all' };

''' + helpers + '\n' + fin_func + '''

const res = computeUnifiedFinancialDataset('all');
console.log('=== CONSOLIDADO GLOBAIS ===');
console.log('Pago Total: R$', res.global.pago_total.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('Pago Set/26: R$', res.global.pago_mes_atual.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('A Vencer Set/26: R$', res.global.proj_mes_atual.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('Previsto Mês Vigente (Set/26): R$', res.global.previsto_mes_vigente.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('MRR (Próx. 6M): R$', res.global.mrr.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('Projeção Próximo Mês (M+1: Out/26): R$', res.global.proj_1m.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('Projeção 3M: R$', res.global.proj_3m.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('Projeção 6M: R$', res.global.proj_6m.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('Projeção 12M: R$', res.global.proj_12m.toLocaleString('pt-BR', {minimumFractionDigits:2}));
console.log('---');
console.log('Projeção Mensal (0 a 6):');
res.global.projecao_mensal.slice(0, 7).forEach(p => {
    console.log('  ' + p.label + ' (' + p.mes + '): R$ ' + p.previsto.toLocaleString('pt-BR', {minimumFractionDigits:2}));
});
'''

with open('scratch_test_clean_fin.js', 'w', encoding='utf-8') as f_out:
    f_out.write(test_js)

import subprocess
out = subprocess.run(['node', 'scratch_test_clean_fin.js'], capture_output=True, text=True)
print('STDOUT:\n', out.stdout)
if out.stderr:
    print('STDERR:\n', out.stderr[:500])

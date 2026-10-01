const fs = require('fs');

const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'utf8');

// Extract javascript code
const idx1 = html.indexOf('<script>');
const idx2 = html.lastIndexOf('</script>');
const jsCode = html.slice(idx1 + 8, idx2);

// Mock DOM
const mockDOM = `
const dummyElem = {
    innerHTML: '',
    value: '',
    style: {},
    classList: { add: () => {}, remove: () => {}, contains: () => false },
    addEventListener: () => {},
    setAttribute: () => {},
    getAttribute: () => '',
    appendChild: () => {},
    querySelector: () => null,
    querySelectorAll: () => []
};
const document = {
    querySelector: (s) => dummyElem,
    querySelectorAll: (s) => [],
    getElementById: (s) => dummyElem,
    createElement: () => dummyElem
};
const window = {
    addEventListener: () => {},
    Chart: function() { return { destroy: () => {}, update: () => {} }; }
};
`;

const fullScript = mockDOM + '\n' + jsCode + `
console.log('\\n=== TESTING COMPUTE UNIFIED FINANCIAL DATASET ===');
const fin = computeUnifiedFinancialDataset('all');
const ped = fin.courses['POS-GRADUACAO EM INFECTOPEDIATRIA'];
console.log('PED MRR:', ped.kpis.mrr_ativo);
console.log('PED Pago Mês Atual:', ped.kpis.recebido_mes_atual);
console.log('PED A Vencer Mês Atual:', ped.kpis.a_vencer_mes_atual);
console.log('PED Proj 3M:', ped.kpis.proj_3m);
console.log('PED Proj 6M:', ped.kpis.proj_6m);
console.log('PED Proj 12M:', ped.kpis.proj_12m);
console.log('PED Projeção Mensal (8 meses):');
ped.projecao_mensal.slice(0, 8).forEach(p => console.log('  ' + p.label + ': R$ ' + p.previsto.toLocaleString('pt-BR', {minimumFractionDigits: 2})));

console.log('\\n=== TESTING DRAW CURSO VIEW ===');
FILTER = { curso: 'POS-GRADUACAO EM INFECTOPEDIATRIA', aluno: '' };
drawCursoView(true);
console.log('drawCursoView executed successfully!');
`;

fs.writeFileSync('temp_verify_fix.js', fullScript, 'utf8');

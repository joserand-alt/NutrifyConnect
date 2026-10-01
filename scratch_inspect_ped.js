const DATA = require('./extracted_data.js');

console.log('Students count:', DATA.students ? DATA.students.length : 0);
console.log('Vindi subs count:', DATA.financeiro && DATA.financeiro.subscriptions ? DATA.financeiro.subscriptions.length : 0);
console.log('Vindi faturas count:', DATA.financeiro && DATA.financeiro.faturas_tabela ? DATA.financeiro.faturas_tabela.length : 0);
console.log('Asaas faturas count:', DATA.financeiro_asaas && DATA.financeiro_asaas.faturas_tabela ? DATA.financeiro_asaas.faturas_tabela.length : 0);

// Let's inspect emailToCourse
const emailToCourse = {};
DATA.students.forEach(s => {
    const em = (s.email || '').toLowerCase().trim();
    if (em) emailToCourse[em] = s.curso;
});

// Check Vindi subs matching PED
const pedSubs = (DATA.financeiro.subscriptions || []).filter(sub => {
    const c = (sub.curso || emailToCourse[(sub.customer_email || '').toLowerCase()] || '');
    return c.toUpperCase().includes('PEDIAT') || c.toUpperCase().includes('PED');
});

console.log('PED subs found in Vindi:', pedSubs.length);
if (pedSubs.length > 0) {
    console.log('Sample PED sub:', JSON.stringify(pedSubs[0], null, 2));
}

// Check all statuses and plans of pedSubs
const planCounts = {};
const statusFinCounts = {};
const statusCounts = {};
let sumParcela = 0;
let sumAdimplenteParcela = 0;

pedSubs.forEach(s => {
    planCounts[s.plano] = (planCounts[s.plano] || 0) + 1;
    statusFinCounts[s.status_financeiro] = (statusFinCounts[s.status_financeiro] || 0) + 1;
    statusCounts[s.status] = (statusCounts[s.status] || 0) + 1;
    sumParcela += (Number(s.valor_parcela) || 0);
    if (s.status_financeiro === 'adimplente') {
        sumAdimplenteParcela += (Number(s.valor_parcela) || 0);
    }
});

console.log('Plan counts:', planCounts);
console.log('Status financeiro counts:', statusFinCounts);
console.log('Status counts:', statusCounts);
console.log('Total sumParcela:', sumParcela);
console.log('Sum adimplente parcela (MRR?):', sumAdimplenteParcela);

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
    location: { reload: () => {} },
    Chart: function() { return { destroy: () => {}, update: () => {} }; }
};
`;

const fullScript = mockDOM + '\n' + jsCode + `
console.log('\\n=== TESTING DRAW ORIGEM ===');
FILTER = { curso: 'all', aluno: 'all' };
drawOrigem(true);
console.log('drawOrigem executed successfully!');

// Check student without pre-enrollment conversions
const gabriela = DATA.students.find(s => s.nome.includes('GABRIELA VALE'));
if (gabriela) {
    console.log('\\nGabriela rd_funnel:');
    console.log('conversoes_antes:', gabriela.rd_funnel.conversoes_antes);
    console.log('eventos length:', gabriela.rd_funnel.eventos.length);
    console.log('dias_venda:', JSON.stringify(gabriela.rd_funnel.dias_venda));
}

// Check student with real pre-enrollment conversions
const caroline = DATA.students.find(s => s.nome.includes('CAROLINE DE ARRIADA'));
if (caroline) {
    console.log('\\nCaroline rd_funnel:');
    console.log('conversoes_antes:', caroline.rd_funnel.conversoes_antes);
    console.log('eventos length:', caroline.rd_funnel.eventos.length);
    console.log('events:', caroline.rd_funnel.eventos);
}
process.exit(0);
`;

fs.writeFileSync('temp_verify_origem.js', fullScript, 'utf8');

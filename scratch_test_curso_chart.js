const fs = require('fs');

const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'utf8');

const idx1 = html.indexOf('<script>');
const idx2 = html.lastIndexOf('</script>');
const jsCode = html.slice(idx1 + 8, idx2);

const runner = `
let capturedMountHTML = '';
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
    getElementById: (s) => {
        if (s === 'curso-content-mount') {
            return {
                set innerHTML(val) {
                    capturedMountHTML = val;
                },
                get innerHTML() {
                    return capturedMountHTML;
                }
            };
        }
        return dummyElem;
    },
    createElement: () => dummyElem
};
const window = {
    addEventListener: () => {},
    location: { reload: () => {} },
    Chart: function() { return { destroy: () => {}, update: () => {} }; }
};

${jsCode}

console.log('\\nCalling drawCursoView for POS-GRADUACAO EM INFECTOPEDIATRIA:');
drawCursoView('POS-GRADUACAO EM INFECTOPEDIATRIA', true);

// Extract the financial chart from capturedMountHTML
const idxChart = capturedMountHTML.indexOf('Realizado vs Previsto');
console.log('Found Realizado vs Previsto in mount at:', idxChart);

const svgStart = capturedMountHTML.indexOf('<svg', idxChart);
const svgEnd = capturedMountHTML.indexOf('</svg>', svgStart) + 6;
const svg = capturedMountHTML.slice(svgStart, svgEnd);

// Extract all text elements with values
const re = /<text[^>]*>([^<]+)<\\/text>/g;
let m;
const texts = [];
while ((m = re.exec(svg)) !== null) {
    texts.push(m[1].trim());
}
console.log('All text labels in the financial chart SVG:');
console.log(texts);

process.exit(0);
`;

fs.writeFileSync('temp_test_curso_chart2.js', runner, 'utf8');

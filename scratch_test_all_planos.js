const DATA = require('./extracted_data.js');

function parsePlanCycles(planoStr) {
    if (!planoStr) return 18;
    const p = planoStr.toString().toUpperCase().trim();

    // 1. Check for à vista / 1x
    if (p.includes('À VISTA') || p.includes('A VISTA')) return 1;

    // 2. Explicit cycle indicators with X: e.g. "24X", "18X", "12X", "10X", "3X", "6X"
    // Match numbers directly followed by X or separated by space: "18X", "18 X", "24x"
    const mX = p.match(/\b(\d+)\s*X\b/);
    if (mX) {
        return parseInt(mX[1], 10);
    }

    // 3. Match "24 MESES", "18 PARCELAS", etc.
    const mWord = p.match(/\b(\d+)\s*(?:MESES|PARCELAS|VEZES)\b/);
    if (mWord) {
        return parseInt(mWord[1], 10);
    }

    // 4. Match "- 24" at end of string or "- 12" when not %
    const mHyphen = p.match(/-\s*(\d+)(?!\s*%)(\s*X)?$/);
    if (mHyphen) {
        return parseInt(mHyphen[1], 10);
    }

    // 5. Specific keywords
    if (p.includes('RESIDENTES 24')) return 24;
    if (p.includes('ANUAL')) return 12;
    if (p.includes('SEMESTRAL')) return 6;

    // 6. Default by product type:
    // All "Pós-Graduação" in this institution are 18 months standard
    if (p.includes('PÓS') || p.includes('POS') || p.includes('MENSALIDADE')) return 18;

    return 12;
}

const subs = DATA.financeiro.subscriptions || [];
const allPlanos = new Set();
subs.forEach(s => {
    if (s.plano) allPlanos.add(s.plano);
});

console.log('Testing ALL planos with parsePlanCycles:');
Array.from(allPlanos).sort().forEach(plano => {
    console.log(`Cycles: ${String(parsePlanCycles(plano)).padStart(2, ' ')} | "${plano}"`);
});

const DATA = require('./extracted_data.js');

function isCheckoutEvent(ev) {
    if (!ev) return false;
    const cat = (ev.categoria || '').toLowerCase();
    const raw = (ev.evento_raw || '').toLowerCase();
    const clean = (ev.evento_clean || '').toLowerCase();
    if (cat.includes('checkout') || cat.includes('matrícula') || cat.includes('matricula')) return true;
    if (raw.includes('checkout') || raw.includes('pago') || raw.includes('pendente') || raw.includes('recorrencia') || raw.includes('compra')) return true;
    if (clean.includes('checkout') || clean.includes('pagamento') || clean.includes('compra')) return true;
    return false;
}

// Compare metrics before and after excluding checkout
let beforeCountWithConv = 0;
let beforeTotalPoints = 0;
let afterCountWithConv = 0;
let afterTotalPoints = 0;

let beforeEventsCount = 0;
let afterEventsCount = 0;

DATA.students.forEach(s => {
    if (s.rd_funnel) {
        const evs = s.rd_funnel.eventos_detalhados || [];
        const nonCheckoutEvs = evs.filter(e => !isCheckoutEvent(e));

        beforeEventsCount += evs.length;
        afterEventsCount += nonCheckoutEvs.length;

        if (evs.length > 0) {
            beforeCountWithConv++;
            beforeTotalPoints += evs.length;
        }

        if (nonCheckoutEvs.length > 0) {
            afterCountWithConv++;
            afterTotalPoints += nonCheckoutEvs.length;
        }
    }
});

console.log('=== BEFORE (with Checkout) ===');
console.log('Total events:', beforeEventsCount);
console.log('Students with conversions:', beforeCountWithConv);
console.log('Avg points of contact per student with conv:', (beforeTotalPoints / beforeCountWithConv).toFixed(2));

console.log('\n=== AFTER (without Checkout) ===');
console.log('Total events:', afterEventsCount);
console.log('Students with conversions:', afterCountWithConv);
console.log('Avg points of contact per student with conv:', (afterTotalPoints / afterCountWithConv).toFixed(2));

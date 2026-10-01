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

let changedMatCount = 0;
let validMatBefore = 0;
let validMatAfter = 0;

DATA.students.forEach(s => {
    if (s.rd_funnel) {
        const evs = s.rd_funnel.eventos_detalhados || [];
        const nonCheckout = evs.filter(e => !isCheckoutEvent(e));
        if (s.rd_funnel.dias_venda !== '' && s.rd_funnel.dias_venda !== null && !isNaN(s.rd_funnel.dias_venda)) {
            validMatBefore++;
        }

        // If all events were checkout, student has no pre-enrollment touchpoint
        if (evs.length > 0 && nonCheckout.length === 0) {
            changedMatCount++;
        }
    }
});

console.log('Valid maturacao before:', validMatBefore);
console.log('Students who only had checkout events:', changedMatCount);

const fs = require('fs');

function isCheckoutEvent(ev) {
    if (!ev) return false;
    const cat = (ev.categoria || '').toLowerCase();
    const raw = (ev.evento_raw || '').toLowerCase();
    const clean = (ev.evento_clean || '').toLowerCase();
    if (cat.includes('checkout') || cat.includes('matrícula') || cat.includes('matricula')) return true;
    if (raw.includes('checkout') || raw.includes('pago') || raw.includes('pendente') || raw.includes('recorrencia') || raw.includes('compra') || raw.includes('problema') || raw.includes('hotmart') || raw.includes('woocommerce')) return true;
    if (clean.includes('checkout') || clean.includes('pagamento') || clean.includes('compra')) return true;
    return false;
}

function isCheckoutString(s) {
    if (!s) return false;
    const low = s.toString().toLowerCase();
    return low.includes('checkout') || low.includes('pagamento') || low.includes('pago') || low.includes('pendente') || low.includes('recorrencia') || low.includes('compra') || low.includes('problema') || low.includes('hotmart') || low.includes('woocommerce');
}

const DATA = require('./extracted_data.js');

let cleanedCount = 0;
let totalRemoved = 0;

DATA.students.forEach(s => {
    if (s.rd_funnel) {
        const evs = s.rd_funnel.eventos_detalhados || [];
        const fmt = s.rd_funnel.eventos || [];
        
        const newEvs = evs.filter(e => !isCheckoutEvent(e));
        const newFmt = fmt.filter(e => !isCheckoutString(e));
        
        if (evs.length !== newEvs.length || fmt.length !== newFmt.length) {
            cleanedCount++;
            totalRemoved += (evs.length - newEvs.length);
            s.rd_funnel.eventos_detalhados = newEvs;
            s.rd_funnel.eventos = newFmt;
            s.rd_funnel.conversoes_antes = newEvs.length;
            if (newEvs.length > 0 && newEvs[0].data) {
                s.rd_funnel.dt_primeira = newEvs[0].data;
            } else if (newEvs.length === 0) {
                s.rd_funnel.dt_primeira = '—';
                s.rd_funnel.dias_venda = '';
            }
        }
    }
});

console.log('Students cleaned:', cleanedCount);
console.log('Total checkout events removed:', totalRemoved);

// Check sample student (like the one with 3 checkouts)
const sample = DATA.students.find(s => s.rd_funnel && s.rd_funnel.conversoes_antes === 0 && s.rd_funnel.conversoes > 0);
if (sample) {
    console.log('\nSample direct checkout student:');
    console.log('Name:', sample.nome);
    console.log('rd_funnel:', JSON.stringify(sample.rd_funnel, null, 2));
}

const fs = require('fs');

const DATA = require('./extracted_data.js');

let totalStudents = DATA.students.length;
let withRd = 0;
let checkoutEventsFound = 0;
let allEventsCount = 0;
const checkoutIdentSet = new Set();
const otherIdentSet = new Set();

DATA.students.forEach(s => {
    if (s.rd_funnel) {
        withRd++;
        const evs = s.rd_funnel.eventos_detalhados || [];
        evs.forEach(ev => {
            allEventsCount++;
            const raw = (ev.evento_raw || '').toLowerCase();
            const clean = (ev.evento_clean || '').toLowerCase();
            const cat = ev.categoria || '';
            const isCheckout = cat.includes('Checkout') || 
                               raw.includes('checkout') || 
                               raw.includes('pago') || 
                               raw.includes('pendente') || 
                               raw.includes('recorrencia') || 
                               raw.includes('compra');
            if (isCheckout) {
                checkoutEventsFound++;
                checkoutIdentSet.add(ev.evento_clean + ' || ' + ev.evento_raw);
            } else {
                otherIdentSet.add(ev.evento_clean + ' || ' + ev.evento_raw);
            }
        });
    }
});

console.log('Total students:', totalStudents);
console.log('Students with rd_funnel:', withRd);
console.log('All events count:', allEventsCount);
console.log('Checkout events count:', checkoutEventsFound);
console.log('\nDistinct Checkout events:');
Array.from(checkoutIdentSet).forEach(e => console.log('  - ' + e));

console.log('\nSample Other events (first 10):');
Array.from(otherIdentSet).slice(0, 10).forEach(e => console.log('  - ' + e));

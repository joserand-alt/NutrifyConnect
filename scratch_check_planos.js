const DATA = require('./extracted_data.js');

const subs = DATA.financeiro.subscriptions || [];
if (subs.length > 0) {
    const s = subs[0];
    const keys = Object.keys(s);
    console.log('Subscription keys:', keys);
    console.log('Sample sub without faturas:');
    const copy = { ...s };
    delete copy.faturas;
    console.log(copy);
}

// Let's inspect all distinct planos across ALL subscriptions
const allPlanos = new Set();
subs.forEach(s => {
    if (s.plano) allPlanos.add(s.plano);
});
console.log('\nAll distinct planos in Vindi subs:');
Array.from(allPlanos).sort().forEach(p => console.log(' - ' + p));

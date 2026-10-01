import subprocess

code = '''
const fs = require('fs');
const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'utf-8');

const dataIdx = html.indexOf('const DATA =');
const dataEnd = html.indexOf('</script>', dataIdx);
const scriptContent = html.slice(dataIdx, dataEnd);

const vm = require('vm');

const elements = {};
function getOrCreate(id) {
    if (!elements[id]) {
        elements[id] = {
            id: id,
            _html: '',
            set innerHTML(val) { this._html = val; },
            get innerHTML() { return this._html; },
            value: '',
            style: {},
            options: [],
            addEventListener: () => {}
        };
    }
    return elements[id];
}

const context = {
    console: console,
    setTimeout: () => {},
    clearTimeout: () => {},
    setInterval: () => {},
    clearInterval: () => {},
    document: { 
        getElementById: (id) => getOrCreate(id),
        querySelector: (s) => getOrCreate(s.replace('#', '')),
        querySelectorAll: () => []
    },
    window: { addEventListener: () => {} },
    mesesNomes: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
    mesesNomesCompletos: ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
};
vm.createContext(context);

try {
    vm.runInContext(scriptContent, context);
    console.log('Script loaded.');

    console.log('Calling drawHome...');
    context.drawHome(true);
    console.log('drawHome succeeded!');
    
    const liveSection = elements['home-live-section'];
    console.log('home-live-section display:', liveSection.style.display);
    
    const miniKpis = elements['home-live-mini-kpis'];
    console.log('miniKpis HTML length:', miniKpis ? miniKpis._html.length : 0);
    
    const feedList = elements['home-live-feed-list'];
    console.log('feedList HTML length:', feedList ? feedList._html.length : 0);

} catch(e) {
    console.error('ERROR in execution:', e.message);
    console.error(e.stack);
}
'''

res = subprocess.run(['node', '-e', code], capture_output=True, encoding='utf-8', errors='replace')
print(res.stdout)
if res.stderr:
    print('STDERR:', res.stderr)

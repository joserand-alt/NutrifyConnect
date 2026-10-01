import subprocess

code = '''
const fs = require('fs');
const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'utf-8');

const dataIdx = html.indexOf('const DATA =');
const dataEnd = html.indexOf('</script>', dataIdx);
const scriptContent = html.slice(dataIdx, dataEnd);

const vm = require('vm');

const context = {
    console: console,
    setTimeout: () => {},
    clearTimeout: () => {},
    setInterval: () => {},
    clearInterval: () => {},
    document: { 
        getElementById: () => ({ innerHTML: '', style: {} }),
        querySelector: () => ({ innerHTML: '', style: {}, addEventListener: () => {} }),
        querySelectorAll: () => []
    },
    window: { addEventListener: () => {} },
    mesesNomes: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
    mesesNomesCompletos: ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
};
vm.createContext(context);
vm.runInContext(scriptContent, context);

const DATA = vm.runInContext('DATA', context);
const students = DATA.students || [];
const curric = DATA.curriculum || {};
console.log('Curriculum keys:', Object.keys(curric));

const pedStudents = students.filter(s => (s.nome || '').includes('FABRIZIO') || (s.nome || '').includes('DERRICK') || (s.nome || '').includes('GABRIELA VALE'));
pedStudents.forEach(s => {
    console.log('--- Student:', s.nome, '---');
    console.log('  curso in student:', s.curso);
    console.log('  aulas_feitas:', s.aulas_feitas);
    console.log('  total_aulas_curric:', s.total_aulas_curric, 'aulas_feitas_curric:', s.aulas_feitas_curric);
    console.log('  total_mods:', s.total_mods, 'mods_concluidos:', s.mods_concluidos, 'pct_mods:', s.pct_mods);
    console.log('  events length:', (s.events || []).length);
});
'''

res = subprocess.run(['node', '-e', code], capture_output=True, encoding='utf-8', errors='replace')
print(res.stdout)
if res.stderr:
    print('STDERR:', res.stderr)

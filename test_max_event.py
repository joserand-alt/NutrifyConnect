import subprocess

code = '''
const fs = require('fs');
const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'utf-8');

const dataIdx = html.indexOf('const DATA =');
const dataEnd = html.indexOf('</script>', dataIdx);
const scriptContent = html.slice(dataIdx, dataEnd);

const vm = require('vm');
const context = {
    document: { querySelector: () => null, getElementById: () => null }
};
vm.createContext(context);
vm.runInContext(scriptContent.slice(0, scriptContent.indexOf('const API_LOGS =')) + '; this.DATA = DATA;', context);

const DATA = context.DATA;
const students = DATA.students || [];

let maxDt = null;
let maxStr = '';
let countEvents = 0;

students.forEach(s => {
    (s.events || []).forEach(e => {
        countEvents++;
        if (e.d) {
            const p = e.d.split(' ')[0].split('/');
            const t = e.d.split(' ')[1] ? e.d.split(' ')[1].split(':') : [0,0,0];
            if (p.length === 3) {
                const yr = parseInt(p[2].length === 2 ? '20' + p[2] : p[2], 10);
                const dt = new Date(yr, parseInt(p[1], 10) - 1, parseInt(p[0], 10), parseInt(t[0]||0, 10), parseInt(t[1]||0, 10), parseInt(t[2]||0, 10));
                if (!maxDt || dt > maxDt) {
                    maxDt = dt;
                    maxStr = e.d;
                }
            }
        }
    });
});

console.log('Total events:', countEvents);
console.log('Max event date:', maxStr);
console.log('Max event Date obj:', maxDt);
console.log('Current system Date:', new Date());
'''

res = subprocess.run(['node', '-e', code], capture_output=True, encoding='utf-8', errors='replace')
print(res.stdout)
if res.stderr:
    print('STDERR:', res.stderr)

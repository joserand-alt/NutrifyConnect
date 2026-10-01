const fs = require('fs');
const path = require('path');

const data = JSON.parse(fs.readFileSync('extracted_DATA_temp.json', 'utf8'));
global.DATA = data;

const htmlPath = path.join('C:', 'Users', 'DELL', 'Desktop', 'Dash_InfectoCast', 'dashboard_gerado.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const parseDateIdx = html.indexOf('function parseDateUniversal(');
const parseDateEndIdx = html.indexOf('function getMatriculasAuditoriaData()', parseDateIdx);
const parseDateStr = html.substring(parseDateIdx, parseDateEndIdx);

const fnIdx = html.indexOf('function getMatriculasAuditoriaData()');
const fnEndIdx = html.indexOf('function getSync24hData()', fnIdx);
const fnStr = html.substring(fnIdx, fnEndIdx);

eval(parseDateStr);
eval(fnStr);

const res = getMatriculasAuditoriaData();
console.log('Total Confirmadas:', res.allRecords.length);
console.log('Confirmadas 48h:', res.list48h.length);
console.log('Confirmadas 30d:', res.list30d.length);
console.log('Total Pendentes:', res.allPendentes.length);
console.log('Pendentes 48h:', res.pendentes48h.length);
console.log('Pendentes 30d:', res.pendentes30d.length);
console.log('\n--- LISTA PENDENTES 30D ---');
console.log(JSON.stringify(res.pendentes30d.map(p => ({
    email: p.email,
    nome: p.nome,
    curso: p.curso,
    data_fmt: p.data_fmt,
    origem: p.origem
})), null, 2));

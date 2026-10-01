const fs = require('fs');

const data = JSON.parse(fs.readFileSync('extracted_DATA_temp.json', 'utf8'));
global.DATA = data;

const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'utf8');

const parseDateIdx = html.indexOf('function parseDateUniversal(');
const parseDateEndIdx = html.indexOf('function getMatriculasAuditoriaData()', parseDateIdx);
const parseDateStr = html.substring(parseDateIdx, parseDateEndIdx);

const fnIdx = html.indexOf('function getMatriculasAuditoriaData()');
const fnEndIdx = html.indexOf('function getSync24hData()', fnIdx);
const fnStr = html.substring(fnIdx, fnEndIdx);

eval(parseDateStr);
eval(fnStr);

const res = getMatriculasAuditoriaData();
console.log('Confirmadas 48h:', res.list48h.length);
console.log('Confirmadas 30d:', res.list30d.length);
console.log('Pendentes 48h:', res.pendentes48h.length);
console.log('Pendentes 30d:', res.pendentes30d.length);

console.log('List 48h:', JSON.stringify(res.list48h, null, 2));
console.log('List 30d count:', res.list30d.length);
console.log('List 30d items:', res.list30d.map(c => ({ nome: c.nome, email: c.email, data: c.data, data_fmt: c.data_fmt })));

import os

dash_dir = r'C:\Users\DELL\Desktop\Dash_InfectoCast'
path = os.path.join(dash_dir, 'dashboard_gerado.html')
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Let's inspect drawExecView from start to end
pos_start = code.find('function drawExecView(')
pos_end = code.find('function drawHome(', pos_start)

exec_code = code[pos_start:pos_end]

# Let's write a small node test to evaluate drawExecView in a minimal DOM
test_js = f"""
const fs = require('fs');
const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'utf-8');

const matchData = html.match(/const DATA = (\\{{[\\s\\S]*?\\}});/);
const DATA = JSON.parse(matchData[1]);

// Mock DOM & globals
let _execDrawn = false;
let CURRENT_DATA = DATA;
let FILTER = {{ curso: 'all' }};

const $ = sel => ({{
    innerHTML: '',
    style: {{}},
    classList: {{ add: () => {{}}, remove: () => {{}} }}
}});
const $$ = sel => [];
const fN = n => String(n || 0);
const fM = n => 'R$ ' + Number(n || 0).toFixed(2);
const fmt = fN;

const matchParse = html.match(/function parseDateUniversal\\(dStr\\) \\{{[\\s\\S]*?\\n\\}}/);
const matchMat = html.match(/function getMatriculasAuditoriaData\\(\\) \\{{[\\s\\S]*?\\n\\}}/);

eval(matchParse[0]);
eval(matchMat[0]);

try {{
    {exec_code}
    console.log('Testing drawExecView(true)...');
    drawExecView(true);
    console.log('✅ drawExecView executed successfully without errors!');
}} catch (err) {{
    console.error('❌ Error executing drawExecView:', err.message);
    console.error(err.stack);
}}
"""

with open('test_exec_debug.js', 'w', encoding='utf-8') as f:
    f.write(test_js)

print("Created test_exec_debug.js")
